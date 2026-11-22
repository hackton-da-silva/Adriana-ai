import { requestManualAnswer, hasChatProvider } from './ai-provider';
import { randomUUID } from 'node:crypto';
import { documentExcerpts, loadDocumentIndex } from './document-rag';
import { searchDocumentHybrid } from './document-embeddings';
import { isMaintenanceTurn } from './maintenance-query';
import { newCallTrace, traceCall, type CallTrace } from './call-observability';

export const MAINTENANCE_MANUAL_MCP = 'ManualManutencaoLTQ';
export const CONSULT_MAINTENANCE_MANUAL = 'consultar_manual_de_manutencao';

type Source = { source: string; reference: string };
export type ResearchResult =
  | { id: string; query: string; status: 'pending' }
  | { id: string; query: string; status: 'done'; answer: string; sources: Source[] }
  | { id: string; query: string; status: 'not_found' | 'insufficient_evidence' | 'failed' };

type ResearchJob = { deliveryFailed?: boolean; result: ResearchResult; startedAt: number; fallback: boolean };
type ResearchSession = {
  mcpToken: string;
  deliver?: (result: ResearchResult) => Promise<unknown>;
  plantEnabled: boolean;
  trace: CallTrace;
  telemetryEvents: number;
  expires: number;
  jobs: Map<string, ResearchJob>;
  lastTranscriptTurn?: number;
};

const state = globalThis as typeof globalThis & {
  unmuteDocumentResearch?: { sessions: Map<string, ResearchSession>; active: number };
};
const research = state.unmuteDocumentResearch ??= { sessions: new Map(), active: 0 };

function prune() {
  for (const [token, session] of research.sessions) {
    if (session.expires <= Date.now()) research.sessions.delete(token);
  }
}

export async function createResearchSession(trace = newCallTrace(), plantEnabled = false) {
  const origin = process.env.AGORA_ANNOTATION_ORIGIN;
  if (!origin || !process.env.RAG_DOCUMENT_PATH || !hasChatProvider()) return;
  try {
    const endpoint = new URL('/api/document-mcp', origin);
    if (endpoint.protocol !== 'https:' || endpoint.username || endpoint.password) return;
    if (!(await loadDocumentIndex()).sections.length) return;
    prune();
    if (research.sessions.size >= 100) return;
    const token = randomUUID();
    const session: ResearchSession = { plantEnabled, mcpToken: randomUUID(), trace, telemetryEvents: 0, expires: Date.now() + 3_600_000, jobs: new Map<string, ResearchJob>() };
    research.sessions.set(token, session);
    return {
      token,
      bindDelivery: (deliver: NonNullable<ResearchSession['deliver']>) => { session.deliver = deliver; },
      discard: () => research.sessions.delete(token),
      server: {
        name: MAINTENANCE_MANUAL_MCP,
        endpoint: endpoint.toString(),
        transport: 'streamable_http' as const,
        headers: { Authorization: `Bearer ${session.mcpToken}` },
        allowed_tools: [CONSULT_MAINTENANCE_MANUAL, 'consultar_resultado'],
        timeout_ms: 5000,
      },
    };
  } catch {
    console.warn('Document retrieval is unavailable. Check RAG_DOCUMENT_PATH.');
  }
}

export function getResearchSession(token: string | null, client: 'mcp' | 'browser') {
  if (!token || token.length !== 36) return;
  prune();
  return client === 'browser'
    ? research.sessions.get(token)
    : [...research.sessions.values()].find((session) => session.mcpToken === token);
}

class InvalidManualAnswer extends Error {}

async function summarize(query: string, excerpts: ReturnType<typeof documentExcerpts>) {
  const result = await requestManualAnswer(query, excerpts);
  if (result?.answer === null && Array.isArray(result.sources) && result.sources.length === 0) return;
  if (typeof result?.answer !== 'string' || !result.answer.trim() || !Array.isArray(result.sources)) {
    throw new InvalidManualAnswer('invalid_format');
  }
  const sources = new Map<string, Source>();
  for (const id of result.sources) {
    const item = Number.isInteger(id) && excerpts[id - 1];
    if (item) sources.set(`${item.source}\n${item.reference}`, { source: item.source, reference: item.reference });
  }
  if (!sources.size) throw new InvalidManualAnswer('invalid_citation');
  return { answer: result.answer.trim().slice(0, 1000), sources: [...sources.values()] };
}

export function startResearch(session: ResearchSession, input: string, searchTerms?: string, fallback = false) {
  const query = input.trim();
  if (!query || query.length > 450) return { status: 'invalid_query' };
  const latest = [...session.jobs.values()].at(-1);
  if (latest && latest.fallback && !fallback && Date.now() - latest.startedAt < 4000) {
    return { id: latest.result.id, status: 'queued' };
  }
  if (latest?.result.status === 'pending' || session.jobs.size >= 6 || research.active >= 4) return { status: 'busy' };

  const id = randomUUID();
  const job: ResearchJob = { result: { id, query, status: 'pending' }, startedAt: Date.now(), fallback };
  const spanId = id.replaceAll('-', '').slice(0, 16);
  session.jobs.set(id, job);
  research.active++;
  setImmediate(async () => {
    const source = fallback ? 'transcript' : 'mcp';
    try {
      const retrievalStarted = Date.now();
      let mode = 'hybrid';
      const excerpts = await searchDocumentHybrid(await loadDocumentIndex(), query, searchTerms, () => { mode = 'bm25'; });
      traceCall(session.trace, {
        name: 'rag.retrieval', type: 'retriever', parentSpanId: spanId, startedAt: retrievalStarted,
        input: { jobId: id, queryCharacters: query.length, translatedTerms: Boolean(searchTerms) },
        data: { jobId: id, mode, excerpts: excerpts.length, pages: excerpts.map(item => /^p\. (\d+)/.exec(item.reference)?.[1] ?? '-').join(','), translatedTerms: Boolean(searchTerms) },
      });
      const generationStarted = Date.now();
      let answer: Awaited<ReturnType<typeof summarize>>;
      if (excerpts.length) {
        let outcome = 'provider_error';
        try {
          answer = await summarize(query, excerpts);
          outcome = answer ? 'cited' : 'insufficient_evidence';
        } catch (error) {
          if (error instanceof InvalidManualAnswer) outcome = error.message;
          throw error;
        } finally {
          traceCall(session.trace, {
            name: 'rag.answer', type: 'generation', parentSpanId: spanId, startedAt: generationStarted,
            input: { jobId: id, excerpts: excerpts.length, queryCharacters: query.length },
            data: { jobId: id, cited: Boolean(answer), outcome },
          });
        }
      }
      job.result = answer ? { id, query, status: 'done', ...answer } : { id, query, status: excerpts.length ? 'insufficient_evidence' : 'not_found' };
    } catch (error) {
      console.warn('Document research failed:', error instanceof Error ? error.message : 'unknown error');
      job.result = { id, query, status: 'failed' };
    } finally {
      research.active--;
      traceCall(session.trace, {
        name: 'rag.job', type: 'chain', spanId, startedAt: job.startedAt,
        input: { jobId: id, source, queryCharacters: query.length },
        error: job.result.status === 'failed', data: { jobId: id, source, status: job.result.status },
      });
    }
    if (session.deliver) {
      try {
        await session.deliver(job.result);
      } catch {
        job.deliveryFailed = true;
      }
      traceCall(session.trace, {
        name: 'rag.agora_delivery', type: 'event', error: job.deliveryFailed,
        input: { jobId: id, status: job.result.status },
        data: { jobId: id, status: job.deliveryFailed ? 'failed' : 'accepted' },
      });
    }
  });
  return { id, status: 'queued' };
}

export function routeMaintenanceTranscript(session: ResearchSession, turn: number, query: string, topic: string) {
  if (session.plantEnabled && !/rolament|manca[li]|mancais|anel (externo|interno)|SKF|BC4|VU001/i.test(query + ' ' + topic)) {
    return { status: 'out_of_scope' };
  }
  if (!isMaintenanceTurn(query, topic)) return { status: 'out_of_scope' };
  if (turn <= (session.lastTranscriptTurn ?? -1)) return { status: 'already_handled' };
  session.lastTranscriptTurn = turn;
  const latest = [...session.jobs.values()].at(-1);
  if (latest && Date.now() - latest.startedAt < 8000) return { status: 'already_handled' };
  const contextualQuery = (topic ? `${query} Contexto: ${topic}` : query).slice(0, 450);
  return startResearch(session, contextualQuery, undefined, true);
}
