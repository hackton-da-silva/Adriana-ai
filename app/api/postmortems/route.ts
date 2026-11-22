import { z } from 'zod';
import { collectPostmortem, finishPostmortem, getPostmortemSession, postmortemBatchSchema, postmortemStatus, retryPostmortem } from '@/lib/postmortem';

export const runtime = 'nodejs';
const actionSchema = z.discriminatedUnion('action', [
  z.object({ action: z.literal('finish'), reason: z.enum(['operator_ended', 'page_closed']), batch: postmortemBatchSchema.optional() }).strict(),
  z.object({ action: z.literal('retry') }).strict(),
]);

async function handle(request: Request) {
  const session = getPostmortemSession(request.headers.get('X-Postmortem-Token'));
  if (!session) return Response.json({ error: 'Sessão inválida ou expirada.' }, { status: 401 });
  const headers = { 'Cache-Control': 'no-store' };
  if (request.method === 'GET') return Response.json(postmortemStatus(session), { headers });
  if (++session.requests > 5000) return new Response(null, { status: 429 });
  // Enforce the actual streamed size, including requests without Content-Length.
  const reader = request.body?.getReader();
  if (!reader) return new Response(null, { status: 400 });
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 60_000) { await reader.cancel(); return new Response(null, { status: 413 }); }
      chunks.push(value);
    }
    const body: unknown = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if (request.method === 'PUT') {
      const batch = postmortemBatchSchema.safeParse(body);
      if (!batch.success) return new Response(null, { status: 400 });
      if (!collectPostmortem(session, batch.data)) return new Response(null, { status: 409 });
      return new Response(null, { status: 204 });
    }
    const action = actionSchema.safeParse(body);
    if (!action.success) return new Response(null, { status: 400 });
    if (action.data.action === 'finish') {
      if (action.data.batch) collectPostmortem(session, action.data.batch);
      return Response.json(finishPostmortem(session, action.data.reason), { status: 202, headers });
    }
    if (!retryPostmortem(session)) return new Response(null, { status: 409 });
    return Response.json(postmortemStatus(session), { status: 202, headers });
  } catch {
    return new Response(null, { status: 400 });
  } finally {
    reader.releaseLock();
  }
}
export const GET = handle;
export const PUT = handle;
export const POST = handle;
