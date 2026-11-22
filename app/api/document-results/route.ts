import { NextResponse } from 'next/server';
import { getResearchSession, routeMaintenanceTranscript } from '@/lib/document-research';
import { traceCall } from '@/lib/call-observability';

export const runtime = 'nodejs';

export function GET(request: Request) {
  const session = getResearchSession(request.headers.get('X-Research-Token'), 'browser');
  if (!session) return new Response(null, { status: 401 });
  return NextResponse.json(
    { results: [...session.jobs.values()].map(({ result, deliveryFailed }) => ({ ...result, deliveryFailed })) },
    { headers: { 'Cache-Control': 'no-store' } },
  );
}

export async function POST(request: Request) {
  const session = getResearchSession(request.headers.get('X-Research-Token'), 'browser');
  if (!session) return new Response(null, { status: 401 });
  if (Number(request.headers.get('Content-Length')) > 4096) return new Response(null, { status: 413 });
  const body = await request.json().catch(() => null);
  if (!body || !Number.isSafeInteger(body.turn) || body.turn < 0 ||
      typeof body.query !== 'string' || !body.query.trim() || body.query.length > 450 ||
      typeof body.topic !== 'string' || body.topic.length > 160) {
    return new Response(null, { status: 400 });
  }
  const result = routeMaintenanceTranscript(session, body.turn, body.query, body.topic);
  traceCall(session.trace, {
    name: 'rag.transcript_route', type: 'event',
    input: { turn: body.turn, queryCharacters: body.query.length, hasPriorTopic: Boolean(body.topic) },
    data: { turn: body.turn, status: result.status },
  });
  return NextResponse.json(result);
}
