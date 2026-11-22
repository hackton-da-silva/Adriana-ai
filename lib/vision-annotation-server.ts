import { recordPostmortemEvent } from './postmortem';
import { hasChatProvider } from './ai-provider';
export { describeCamera, locateObject } from './ai-provider';
import { randomUUID } from 'node:crypto';
import type { LlmTool } from 'agora-agents';
import type { AnnotationRequest } from './vision-annotation';
import { newCallTrace, traceCall, type CallTrace } from './call-observability';

type Result =
  | { status: 'marked' | 'not_found' | 'camera_off' | 'unavailable' | 'timeout' }
  | { status: 'described'; description: string };
type Pending = AnnotationRequest & {
  claimed: boolean;
  complete: (result: Result) => void;
};
type Session = {
  trace: CallTrace;
  token: string;
  callbackToken: string;
  expires: number;
  count: number;
  pending?: Pending;
};

const HOUR = 3_600_000;
const state = globalThis as typeof globalThis & {
  unmuteAnnotations?: { sessions: Map<string, Session>; requests: number[] };
};
const { sessions, requests } = state.unmuteAnnotations ??= {
  sessions: new Map<string, Session>(),
  requests: [] as number[],
};

function prune() {
  const now = Date.now();
  for (const [id, session] of sessions) if (session.expires <= now) sessions.delete(id);
  while (requests.length && requests[0] <= now - HOUR) requests.shift();
}

export function createAnnotationSession(trace = newCallTrace()): { token: string; discard: () => void; tools: LlmTool[] } | undefined {
  const origin = process.env.AGORA_ANNOTATION_ORIGIN;
  if (!hasChatProvider() || !origin) return;
  let url: URL;
  try {
    url = new URL('/api/vision-annotation', origin);
  } catch {
    return;
  }
  if (url.protocol !== 'https:' || url.username || url.password) return;
  prune();
  if (sessions.size >= 100) return;
  const id = randomUUID();
  const session = { trace, token: randomUUID(), callbackToken: randomUUID(), expires: Date.now() + HOUR, count: 0 };
  sessions.set(id, session);

  function tool(mode: AnnotationRequest['mode'], name: string, description: string, targetDescription: string): LlmTool {
    return {
      type: 'function',
      function: {
        name,
        description,
        parameters: {
          type: 'object',
          properties: { target: { type: 'string', description: targetDescription } },
          required: ['target'],
          additionalProperties: false,
        },
      },
      execution: { mode: 'sync' },
      server: {
        method: 'POST',
        url: url.toString(),
        headers: { 'Content-Type': 'application/json', 'X-Annotation-Callback': session.callbackToken },
        body: { session: id, target: '{{args.target}}', mode },
        timeout_ms: 30_000,
      },
    };
  }
  return {
    token: session.token,
    discard: () => sessions.delete(id),
    tools: [
      tool('mark', 'circular_objeto', 'Use somente quando pedirem para circular, apontar ou destacar um objeto na câmera.', 'Objeto solicitado, por exemplo garrafa azul.'),
      tool('describe', 'observar_camera', 'Use quando a pessoa pedir o que está vendo, o que está na frente da câmera ou fizer uma pergunta sobre algo que está mostrando agora. Um quadro atual é analisado.', 'Pergunta visual curta ou “descreva o que está visível”.'),
    ],
  };
}

export function authorizeBrowser(token: string | null) {
  if (!token) return;
  prune();
  return [...sessions.values()].find((session) => session.token === token);
}

export function authorizeCallback(id: string, token: string | null) {
  prune();
  const session = sessions.get(id);
  return token && session?.callbackToken === token ? session : undefined;
}

export async function requestAnnotation(session: Session, target: string, mode: AnnotationRequest['mode'] = 'mark'): Promise<Result> {
  prune();
  if (session.pending || session.count >= 4 || requests.length >= 12) return { status: 'unavailable' };
  session.count += 1;
  const startedAt = Date.now();
  requests.push(startedAt);
  recordPostmortemEvent(session.trace.traceId, 'vision.requested', { mode, target, status: 'pending' });

  return new Promise((resolve) => {
    const id = randomUUID();
    const complete = (result: Result) => {
      if (session.pending?.id !== id) return;
      clearTimeout(timer);
      if (session.pending?.id === id) delete session.pending;
      traceCall(session.trace, {
        name: mode === 'describe' ? 'vision.observar_camera' : 'vision.circular_objeto',
        type: 'tool', startedAt, error: result.status === 'unavailable' || result.status === 'timeout',
        input: { mode, targetCharacters: target.length, frameLimit: 1 },
        data: { status: result.status },
      });
      recordPostmortemEvent(session.trace.traceId, 'vision.result', { target, mode, ...result });
      resolve(result);
    };
    const timer = setTimeout(() => complete({ status: 'timeout' }), 23_000);
    session.pending = { id, target, mode, claimed: false, complete };
  });
}
