import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

export type DocumentSection = { reference: string; text: string };
export type RagDocument = { title: string; sections: DocumentSection[] };

type IndexedSection = DocumentSection & { words: Map<string, number>; length: number };
export type DocumentIndex = {
  title: string;
  sections: IndexedSection[];
  frequency: Map<string, number>;
  meanLength: number;
};

const stopWords = new Set(
  'a ao aos as com como da das de dela dele do dos e ela ele em entre era essa esse esta este eu foi isso ja mais me meu minha na nas no nos o os ou para pela pelas pelo pelos por qual quais que quem se sem ser seu sua tem um uma voce sobre the and for from how is it of on or that to what which with'.split(' '),
);

function words(text: string) {
  const normalized = text.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
  return (normalized.match(/[\p{L}\p{N}]+/gu) ?? [])
    .filter((word) => word.length > 1 && !stopWords.has(word))
    .map((word) => word.length > 4 ? word.replace(/(oes|aes)$/, 'ao').replace(/s$/, '') : word);
}

function splitSection(section: DocumentSection): DocumentSection[] {
  const result: DocumentSection[] = [];
  let start = 0;
  while (start < section.text.length) {
    const hardEnd = Math.min(start + 1250, section.text.length);
    const paragraphEnd = section.text.lastIndexOf('\n\n', hardEnd);
    const wordEnd = section.text.lastIndexOf(' ', hardEnd);
    const end = hardEnd === section.text.length ? hardEnd
      : paragraphEnd > start + 650 ? paragraphEnd
      : wordEnd > start + 650 ? wordEnd : hardEnd;
    const text = section.text.slice(start, end).trim();
    if (text) result.push({ reference: section.reference, text });
    if (end === section.text.length) break;
    const overlap = section.text.indexOf(' ', end - 150);
    start = overlap >= start + 500 && overlap < end ? overlap + 1 : end;
  }
  return result;
}

function parseText(title: string, raw: string): RagDocument {
  const sections: DocumentSection[] = [];
  const pages = raw.split('\f');
  if (pages.length > 1 && !pages.at(-1)?.trim()) pages.pop();
  for (const [number, page] of pages.entries()) {
    const pageReference = pages.length > 1 ? `p. ${number + 1}` : '';
    let reference = pageReference || 'Texto';
    let lines: string[] = [];
    function flush() {
      const text = lines.join('\n').trim();
      if (text) sections.push({ reference, text });
      lines = [];
    }
    for (const line of page.split(/\r?\n/)) {
      const heading = /^#{1,6}\s+(.+)$/.exec(line);
      if (heading) {
        flush();
        const label = heading[1].trim().slice(0, 160);
        reference = pageReference ? `${pageReference} · ${label}` : label;
        lines.push(heading[1]);
      } else lines.push(line);
    }
    flush();
  }
  return { title, sections };
}

function buildIndex(document: RagDocument): DocumentIndex {
  const frequency = new Map<string, number>();
  let totalLength = 0;
  const sections = document.sections.flatMap(splitSection).flatMap((section) => {
    const terms = words(section.text);
    const counts = new Map<string, number>();
    for (const term of terms) counts.set(term, (counts.get(term) ?? 0) + 1);
    if (!counts.size) return [];
    for (const term of counts.keys()) frequency.set(term, (frequency.get(term) ?? 0) + 1);
    totalLength += terms.length;
    return [{ ...section, words: counts, length: terms.length }];
  });
  return { title: document.title, sections, frequency, meanLength: totalLength / (sections.length || 1) };
}

export function rankDocumentTerms(index: DocumentIndex, query: string) {
  const terms = [...new Set(words(query))];
  if (!terms.length) return [];
  const ranked = index.sections.flatMap((section, position) => {
    let score = 0;
    let matches = 0;
    for (const term of terms) {
      const count = section.words.get(term);
      if (!count) continue;
      matches++;
      const documentFrequency = index.frequency.get(term) ?? 0;
      const idf = Math.log(1 + (index.sections.length - documentFrequency + 0.5) / (documentFrequency + 0.5));
      score += idf * (count * 2.2) / (count + 1.2 * (0.25 + 0.75 * section.length / index.meanLength));
    }
    return matches ? [{ position, score: score * (0.5 + matches / terms.length) }] : [];
  });
  return ranked.sort((a, b) => b.score - a.score).map(({ position }) => position);
}

export function documentExcerpts(index: DocumentIndex, positions: number[]) {
  return positions.slice(0, 4).map((position) => index.sections[position]).map((section) => ({
    source: index.title,
    reference: section.reference,
    excerpt: section.text,
  }));
}

let cache: { path: string; index: Promise<DocumentIndex> } | undefined;

export function loadDocumentIndex() {
  // The private source is installed on the server at runtime.
  const path = resolve(/* turbopackIgnore: true */ process.cwd(), process.env.RAG_DOCUMENT_PATH || '.rag/document.md');
  if (cache?.path !== path) {
    const index = (async () => {
      const raw = await readFile(path, 'utf8');
      if (raw.length > 2_000_000 || !raw.trim()) throw new Error('Invalid document size');
      const title = process.env.RAG_DOCUMENT_TITLE || path.split(/[/\\]/).pop() || 'Documento';
      const document = parseText(title, raw);
      return buildIndex(document);
    })();
    cache = { path, index };
    // Permit installing the file after startup and retrying on the next session.
    void index.catch(() => { if (cache?.index === index) cache = undefined; });
  }
  return cache.index;
}
