import { NextResponse } from 'next/server';
import { authorizeBrowser, authorizeCallback, describeCamera, locateObject, requestAnnotation } from '@/lib/vision-annotation-server';

export const runtime = 'nodejs';

async function readBody(request: Request, limit: number) {
  if (!request.body || Number(request.headers.get('Content-Length')) > limit) return null;
  const reader = request.body.getReader();
  const decoder = new TextDecoder();
  let size = 0;
  let text = '';
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) return JSON.parse(text + decoder.decode());
      size += value.byteLength;
      if (size > limit) {
        await reader.cancel();
        return null;
      }
      text += decoder.decode(value, { stream: true });
    }
  } catch {
    return null;
  } finally {
    reader.releaseLock();
  }
}

export async function POST(request: Request) {
  const callback = request.headers.get('X-Annotation-Callback');
  if (!callback || callback.length !== 36) return new Response(null, { status: 401 });
  const body = await readBody(request, 2048);
  const session = typeof body?.session === 'string'
    ? authorizeCallback(body.session, callback)
    : undefined;
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const target = typeof body.target === 'string' ? body.target.trim() : '';
  if (!target || target.length > 120) return NextResponse.json({ status: 'unavailable' }, { status: 400 });
  const result = await requestAnnotation(session, target, body.mode === 'describe' ? 'describe' : 'mark');
  return NextResponse.json(result);
}

export function GET(request: Request) {
  const session = authorizeBrowser(request.headers.get('X-Annotation-Token'));
  if (!session) return new Response(null, { status: 401 });
  const job = session.pending;
  return NextResponse.json(
    { job: job && !job.claimed ? { id: job.id, target: job.target, mode: job.mode } : null },
    { headers: { 'Cache-Control': 'no-store' } },
  );
}

export async function PUT(request: Request) {
  const session = authorizeBrowser(request.headers.get('X-Annotation-Token'));
  if (!session) return new Response(null, { status: 401 });
  const body = await readBody(request, 900_000);
  const job = session.pending;
  if (!job || body?.id !== job.id || job.claimed) return new Response(null, { status: 409 });
  if (body.image === null) {
    job.complete({ status: 'camera_off' });
    return NextResponse.json({ box: null });
  }
  if (typeof body.image !== 'string' || body.image.length > 850_000 ||
      !/^data:image\/jpeg;base64,[A-Za-z0-9+/]+=*$/.test(body.image)) {
    job.complete({ status: 'unavailable' });
    return NextResponse.json({ error: 'Invalid frame' }, { status: 400 });
  }

  job.claimed = true;
  try {
    if (job.mode === 'describe') {
      const description = await describeCamera(job.target, body.image);
      if (session.pending !== job) return new Response(null, { status: 409 });
      job.complete({ status: 'described', description });
      return NextResponse.json({ described: true });
    }
    const box = await locateObject(job.target, body.image);
    if (session.pending !== job) return new Response(null, { status: 409 });
    job.complete({ status: box ? 'marked' : 'not_found' });
    return NextResponse.json({ box });
  } catch (error) {
    console.warn('Annotation analysis failed:', error instanceof Error ? error.message : 'unknown error');
    job.complete({ status: 'unavailable' });
    return NextResponse.json({ error: 'Vision analysis failed' }, { status: 502 });
  }
}
