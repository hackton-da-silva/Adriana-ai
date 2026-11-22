import { maintenanceSearchTerms } from './maintenance-query';
import { requestEmbeddings } from './ai-provider';
import { createHash, randomUUID } from 'node:crypto';
import { mkdir, readFile, rename, unlink, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { documentExcerpts, rankDocumentTerms, type DocumentIndex } from './document-rag';

const MODEL = 'text-embedding-3-small';
const DIMENSIONS = 512;
const CANDIDATES = 12;
const pending = new WeakMap<DocumentIndex, Promise<number[][]>>();

function isVector(value: unknown): value is number[] {
  return Array.isArray(value) && value.length === DIMENSIONS && value.every(Number.isFinite);
}

async function embed(input: string[]): Promise<number[][]> {
  const payload: { data: { index: number; embedding: unknown }[] } = await requestEmbeddings(input, MODEL, DIMENSIONS);
  const vectors = payload.data.sort((a, b) => a.index - b.index).map((item, i) => {
    if (item.index !== i || !isVector(item.embedding)) throw new Error('Invalid embedding in API response');
    return item.embedding;
  });
  if (vectors.length !== input.length) throw new Error('Incomplete embeddings response');
  return vectors;
}

async function loadOrGenerate(index: DocumentIndex) {
  const input = index.sections.map(({ text }) => text);
  const fingerprint = createHash('sha256').update(JSON.stringify([MODEL, DIMENSIONS, input])).digest('hex');
  const directory = join(/* turbopackIgnore: true */ process.cwd(), '.rag', 'vectors');
  const path = join(directory, `${fingerprint}.json`);
  try {
    const saved: unknown = JSON.parse(await readFile(path, 'utf8'));
    if (Array.isArray(saved) && saved.length === input.length && saved.every(isVector)) return saved;
  } catch {
    // Missing or unreadable cache entries can be regenerated from source.
  }
  const vectors: number[][] = [];
  for (let offset = 0; offset < input.length; offset += 64) {
    vectors.push(...await embed(input.slice(offset, offset + 64)));
  }
  try {
    await mkdir(directory, { recursive: true, mode: 0o700 });
    const temporary = `${path}.${randomUUID()}.tmp`;
    try {
      await writeFile(temporary, JSON.stringify(vectors), { mode: 0o600 });
      await rename(temporary, path);
    } finally {
      await unlink(temporary).catch(() => undefined);
    }
  } catch {
    // Keep the in-memory index usable if the runtime filesystem is read-only.
  }
  return vectors;
}

export function loadDocumentVectors(index: DocumentIndex) {
  const current = pending.get(index);
  if (current) return current;
  const vectors = loadOrGenerate(index);
  pending.set(index, vectors);
  void vectors.catch(() => pending.delete(index));
  return vectors;
}

function fuseRanks(lexical: number[], semantic: number[]) {
  const scores = new Map<number, number>();
  for (const [ranking, weight] of [[lexical, 1], [semantic, 1.15]] as const) {
    ranking.slice(0, CANDIDATES).forEach((position, rank) => {
      scores.set(position, (scores.get(position) ?? 0) + weight / (8 + rank));
    });
  }
  return [...scores.entries()].sort((a, b) => b[1] - a[1]).map(([position]) => position);
}

export async function searchDocumentHybrid(index: DocumentIndex, query: string, searchTerms?: string, onFallback?: () => void) {
  const englishManual = /ingl[eê]s|english/i.test(process.env.RAG_DOCUMENT_LANGUAGE ?? '');
  const terms = searchTerms?.trim() || (englishManual ? maintenanceSearchTerms(query) : '');
  const lexical = rankDocumentTerms(index, terms ? query + ' ' + terms : query);
  if (!index.sections.length) return [];
  try {
    const [vectors, [question]] = await Promise.all([loadDocumentVectors(index), embed([query])]);
    const semantic = vectors.map((vector, position) => {
      const score = vector.reduce((similarity, value, i) => similarity + value * question[i], 0);
      return { position, score };
    }).filter(({ score }) => score >= 0.22)
      .sort((a, b) => b.score - a.score)
      .map(({ position }) => position);
    return documentExcerpts(index, fuseRanks(lexical, semantic));
  } catch (error) {
    onFallback?.();
    console.warn('Semantic retrieval unavailable; using BM25:', error instanceof Error ? error.message : 'unknown error');
    return documentExcerpts(index, lexical);
  }
}
