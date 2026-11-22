import assert from 'node:assert/strict';
import { AgoraClient } from 'agora-agents';
import { POST as stopConversation } from '../app/api/stop-conversation/route';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { GET, POST, PUT } from '../app/api/postmortems/route';
import { createPostmortemSession, getPostmortemSession, postmortemStatus, recordPostmortemEvent, recordPostmortemTool, sweepPostmortems } from '../lib/postmortem';

async function until(test: () => boolean) {
  const deadline = Date.now() + 3000;
  while (!test()) {
    assert(Date.now() < deadline, 'Postmortem worker timed out');
    await new Promise(resolve => setTimeout(resolve, 10));
  }
}

export async function verifyPostmortems() {
  const cwd = process.cwd();
  const directory = await mkdtemp(path.join(tmpdir(), 'unmute-postmortem-'));
  const originalFetch = globalThis.fetch;
  const originalStop = AgoraClient.prototype.stopAgent;
  const originalKey = process.env.OPENAI_API_KEY;
  const originalBackup = process.env.FEITA_API_KEY;
  const captures: ReturnType<typeof createPostmortemSession>[] = [];
  const create = (trace: string) => {
    const capture = createPostmortemSession(trace)!;
    assert(capture);
    captures.push(capture);
    capture.bindAgent('agent-' + trace);
    return capture;
  };
  const request = (token: string, method: string, body?: unknown) => new Request('http://localhost/api/postmortems', {
    method, headers: { 'X-Postmortem-Token': token, 'Content-Type': 'application/json' },
    ...(body !== undefined && { body: JSON.stringify(body) }),
  });
  const sections = Object.fromEntries(['summary', 'context', 'timeline', 'evidence', 'analysis', 'outcome', 'actions', 'quality', 'limitations']
    .map(key => [key, `Teste ${key} [T1] [E1]. Resolução não confirmada.`]));
  let calls = 0;
  let invalid = false;
  let release: (() => void) | undefined;
  let waiting: Promise<void> | undefined;
  try {
    process.chdir(directory);
    process.env.OPENAI_API_KEY = 'private-test-key';
    delete process.env.FEITA_API_KEY;
    globalThis.fetch = async (url, options) => {
      assert.equal(String(url), 'https://api.openai.com/v1/chat/completions');
      calls++;
      const payload = JSON.parse(String(options?.body));
      assert.equal(payload.store, false);
      assert(!payload.messages[1].content.includes('private-test-key'), 'Secrets must not reach the summarizer');
      if (waiting) await waiting;
      return Response.json({ choices: [{ message: { content: invalid ? '{bad' : JSON.stringify(sections) } }] });
    };
    const a = create('trace-a');
    const b = create('trace-b');
    assert.equal((await GET(request('missing', 'GET'))).status, 401);
    assert.equal((await PUT(request(a.token, 'PUT', { turns: [{ turn: 1, speaker: 'intruder', text: 'x' }] }))).status, 400);
    assert.equal((await PUT(request(a.token, 'PUT', { junk: 'x'.repeat(60_001) }))).status, 413);
    const batch = { turns: [
      { turn: 1, speaker: 'operator', status: 'completed', text: 'A F5 está parada. private-test-key' },
      { turn: 1, speaker: 'assistant', status: 'interrupted', text: 'Vou consultar a telemetria.' },
    ] };
    assert.equal((await PUT(request(a.token, 'PUT', batch))).status, 204);
    await PUT(request(a.token, 'PUT', batch));
    recordPostmortemTool(a.toolToken, 'plant.telemetria.result', {
      result: { alarm: 'TESTE', simulated: true }, authorization: 'must-not-save', image: 'must-not-save',
    });
    recordPostmortemEvent('trace-a', 'test.diagnostic', { status: 'ok' });
    assert.equal(getPostmortemSession(b.token)!.turns.size, 0, 'Sessions must be isolated');
    assert.equal(getPostmortemSession(b.token)!.events.length, 0);
    waiting = new Promise(resolve => { release = resolve; });
    const response = await POST(request(a.token, 'POST', { action: 'finish', reason: 'operator_ended' }));
    assert.equal(response.status, 202);
    await POST(request(a.token, 'POST', { action: 'finish', reason: 'page_closed' }));
    await until(() => calls === 1);
    assert.equal(postmortemStatus(getPostmortemSession(a.token)!).status, 'generating', 'Generation must run asynchronously');
    assert.equal((await PUT(request(a.token, 'PUT', batch))).status, 409, 'Evidence must be sealed at finish');
    release!();
    waiting = undefined;
    const session = getPostmortemSession(a.token)!;
    await until(() => session.state.status === 'completed');
    const json = JSON.parse(await readFile(path.join(directory, session.state.files!.json), 'utf8'));
    const md = await readFile(path.join(directory, session.state.files!.markdown), 'utf8');
    assert.equal(json.transcript.length, 2, 'Repeated batches must not duplicate turns');
    assert.equal(json.transcript[1].status, 'interrupted');
    assert.equal(json.endReason, 'operator_ended', 'Duplicate finish must not overwrite the reason');
    assert(md.includes('Registro integral da transcrição') && md.includes('Próximas ações'));
    assert(!JSON.stringify(json).includes('private-test-key') && !JSON.stringify(json).includes(a.token));
    assert(!JSON.stringify(json).includes('must-not-save'));
    assert.equal(calls, 1, 'Duplicate finish must generate only once');
    assert.equal((await POST(request(a.token, 'POST', { action: 'retry' }))).status, 409);

    invalid = true;
    await POST(request(b.token, 'POST', { action: 'finish', reason: 'page_closed', batch }));
    const sessionB = getPostmortemSession(b.token)!;
    await until(() => sessionB.state.status === 'partial');
    const basic = JSON.parse(await readFile(path.join(directory, sessionB.state.files!.json), 'utf8'));
    assert.equal(basic.transcript.length, 2, 'Page-close batch must be collected before sealing');
    invalid = false;
    assert.equal((await POST(request(b.token, 'POST', { action: 'retry' }))).status, 202);
    await until(() => sessionB.state.status === 'completed');

    delete process.env.OPENAI_API_KEY;
    const c = create('trace-c');
    sweepPostmortems(Date.now() + 120_001);
    const sessionC = getPostmortemSession(c.token)!;
    await until(() => sessionC.state.status === 'partial');
    assert.equal(sessionC.reason, 'connection_lost');
    assert(sessionC.state.notice?.includes('Sem provedor'));
    const invalidStop = await stopConversation(new Request('http://localhost/api/stop-conversation', {
      method: 'POST', headers: { 'X-Postmortem-Token': 'invalid' }, body: JSON.stringify({ agent_id: 'unrelated-agent' }),
    }));
    assert.equal(invalidStop.status, 401);
    const d = create('trace-d');
    const wrong = await stopConversation(new Request('http://localhost/api/stop-conversation', {
      method: 'POST', headers: { 'X-Postmortem-Token': d.token }, body: JSON.stringify({ agent_id: 'wrong-agent' }),
    }));
    assert.equal(wrong.status, 403);
    assert.equal(getPostmortemSession(d.token)!.state.status, 'collecting');
    AgoraClient.prototype.stopAgent = (async () => { throw { statusCode: 404 }; }) as typeof originalStop;
    const stopped = await stopConversation(new Request('http://localhost/api/stop-conversation', {
      method: 'POST', headers: { 'X-Postmortem-Token': d.token }, body: JSON.stringify({ agent_id: 'agent-trace-d' }),
    }));
    assert.equal(stopped.status, 200);
    assert.equal((await stopped.json()).state, 'already-stopping');
    const sessionD = getPostmortemSession(d.token)!;
    await until(() => sessionD.state.status === 'partial');
    assert.equal(sessionD.reason, 'operator_ended', 'Idempotent Agora stop must still finalize the postmortem');

    const final = await GET(request(c.token, 'GET'));
    const status = await final.json();
    assert.equal(final.headers.get('cache-control'), 'no-store');
    assert(!('transcript' in status) && !('token' in status), 'Status must not disclose call content or capabilities');
  } finally {
    release?.();
    for (const capture of captures) capture?.discard();
    globalThis.fetch = originalFetch;
    AgoraClient.prototype.stopAgent = originalStop;
    if (originalKey === undefined) delete process.env.OPENAI_API_KEY;
    else process.env.OPENAI_API_KEY = originalKey;
    if (originalBackup === undefined) delete process.env.FEITA_API_KEY;
    else process.env.FEITA_API_KEY = originalBackup;
    process.chdir(cwd);
    await rm(directory, { recursive: true, force: true });
  }
}
