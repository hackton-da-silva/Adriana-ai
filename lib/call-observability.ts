import { randomBytes } from 'node:crypto';

export type CallTrace = { traceId: string; rootSpanId: string };
type TraceFields = Record<string, string | number | boolean>;
type Observation = {
  name: string;
  type?: 'span' | 'event' | 'tool' | 'retriever' | 'generation' | 'chain' | 'agent';
  startedAt?: number;
  spanId?: string;
  parentSpanId?: string;
  root?: boolean;
  error?: boolean;
  input: TraceFields;
  data?: TraceFields;
};

export function newCallTrace(): CallTrace {
  return { traceId: randomBytes(16).toString('hex'), rootSpanId: randomBytes(8).toString('hex') };
}

export function traceCall(trace: CallTrace, observation: Observation) {
  const { LANGFUSE_BASE_URL: base, LANGFUSE_PUBLIC_KEY: publicKey, LANGFUSE_SECRET_KEY: secret } = process.env;
  if (!base || !publicKey || !secret) return;
  const end = Date.now();
  const attribute = (key: string, stringValue: string) => ({ key, value: { stringValue } });
  const ns = (milliseconds: number) => `${milliseconds}000000`;
  const attributes = [
    attribute('langfuse.trace.name', 'Unmute · chamada Agora'),
    attribute('langfuse.session.id', trace.traceId),
    attribute('langfuse.observation.type', observation.type ?? 'span'),
    attribute('langfuse.observation.input', JSON.stringify(observation.input)),
    attribute('langfuse.observation.output', JSON.stringify(observation.data ?? { status: observation.error ? 'error' : 'ok' })),
    ...Object.entries(observation.data ?? {}).map(([key, value]) =>
      attribute(`langfuse.observation.metadata.${key}`, JSON.stringify(value))),
  ];
  const span = {
    traceId: trace.traceId,
    spanId: observation.root ? trace.rootSpanId : observation.spanId ?? randomBytes(8).toString('hex'),
    ...(!observation.root && { parentSpanId: observation.parentSpanId ?? trace.rootSpanId }),
    name: observation.name,
    kind: 1,
    startTimeUnixNano: ns(observation.startedAt ?? end),
    endTimeUnixNano: ns(end),
    attributes,
    status: { code: observation.error ? 2 : 1 },
  };
  const payload = {
    resourceSpans: [{
      resource: { attributes: [attribute('service.name', 'unmute-poc')] },
      scopeSpans: [{ scope: { name: 'unmute.agora' }, spans: [span] }],
    }],
  };
  const headers = {
    Authorization: `Basic ${Buffer.from(`${publicKey}:${secret}`).toString('base64')}`,
    'Content-Type': 'application/json',
    'x-langfuse-ingestion-version': '4',
  };
  void fetch(`${base.replace(/\/$/, '')}/api/public/otel/v1/traces`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(3000),
  }).then(async (response) => {
    if (!response.ok) console.warn('Langfuse export failed:', response.status);
    await response.body?.cancel();
  }).catch(() => undefined);
}
