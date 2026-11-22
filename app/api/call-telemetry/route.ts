import { getResearchSession } from '@/lib/document-research';
import { traceCall } from '@/lib/call-observability';

export const runtime = 'nodejs';

export async function POST(request: Request) {
  const session = getResearchSession(request.headers.get('X-Research-Token'), 'browser');
  if (!session) return new Response(null, { status: 401 });
  if (session.telemetryEvents >= 160) return new Response(null, { status: 429 });
  if (Number(request.headers.get('Content-Length')) > 2048) return new Response(null, { status: 413 });
  const body = await request.json().catch(() => null);
  if (!body) return new Response(null, { status: 400 });

  if (body.event === 'microphone' && typeof body.ready === 'boolean' && typeof body.unavailable === 'boolean' &&
      typeof body.connected === 'boolean' && typeof body.publishFailed === 'boolean' && typeof body.enabled === 'boolean') {
    traceCall(session.trace, {
      name: 'browser.microphone', type: 'event', error: body.unavailable || body.publishFailed,
      input: { event: 'microphone', enabled: body.enabled, connected: body.connected },
      data: { ready: body.ready, enabled: body.enabled, unavailable: body.unavailable, connected: body.connected, publishFailed: body.publishFailed },
    });
  } else if (body.event === 'transcript' && Number.isSafeInteger(body.turn) && Number.isSafeInteger(body.characters) &&
      body.characters >= 0 && body.characters <= 10000 && typeof body.eligible === 'boolean' && typeof body.final === 'boolean') {
    traceCall(session.trace, {
      name: body.final ? 'browser.transcript_final' : 'browser.transcript_partial', type: 'event',
      input: { event: 'transcript', turn: body.turn, characters: body.characters, final: body.final },
      data: { turn: body.turn, characters: body.characters, eligible: body.eligible },
    });
  } else if (body.event === 'camera' && ['starting', 'published', 'capture_failed', 'publish_failed', 'sending_frames', 'no_frames', 'ended', 'stopped'].includes(body.state)) {
    traceCall(session.trace, {
      name: 'browser.camera', type: 'event',
      input: { event: 'camera', state: body.state },
      error: body.state === 'capture_failed' || body.state === 'publish_failed' || body.state === 'no_frames',
      data: { state: body.state },
    });
  } else {
    return new Response(null, { status: 400 });
  }

  session.telemetryEvents++;
  return new Response(null, { status: 204 });
}
