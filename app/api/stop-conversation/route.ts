import { NextResponse } from 'next/server';
import { AgoraClient, Area } from 'agora-agents';
import { finishPostmortem, getPostmortemSession, recordPostmortemEvent } from '@/lib/postmortem';
import { StopConversationRequest } from '@/types/conversation';

function isAgentAlreadyStoppingOrStopped(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;

  const maybeErr = error as {
    statusCode?: number;
    body?: { detail?: string; reason?: string };
    message?: string;
  };

  const statusCode = maybeErr.statusCode;
  const reason = maybeErr.body?.reason?.toLowerCase();
  const detail = maybeErr.body?.detail?.toLowerCase() ?? maybeErr.message?.toLowerCase() ?? '';

  if (statusCode === 404) return true;
  if (reason === 'invalidrequest' && detail.includes('already in the process of shutting down')) {
    return true;
  }
  return false;
}

export async function POST(request: Request) {
  const capability = request.headers.get('X-Postmortem-Token');
  const postmortem = getPostmortemSession(capability);
  if (capability && !postmortem) return NextResponse.json({ error: 'Sessão inválida.' }, { status: 401 });
  let matched = false;
  let stopFailed = false;
  try {
    const body: StopConversationRequest = await request.json();
    const { agent_id } = body;

    if (!agent_id) {
      return NextResponse.json(
        { error: 'agent_id is required' },
        { status: 400 },
      );
    }

    if (postmortem && postmortem.agentId !== agent_id) return NextResponse.json({ error: 'Sessão inválida.' }, { status: 403 });
    matched = Boolean(postmortem);
    const appId = process.env.NEXT_PUBLIC_AGORA_APP_ID;
    const appCertificate = process.env.NEXT_AGORA_APP_CERTIFICATE;
    if (!appId || !appCertificate) {
      throw new Error(
        'Missing Agora configuration. Set NEXT_PUBLIC_AGORA_APP_ID and NEXT_AGORA_APP_CERTIFICATE.',
      );
    }

    // area: change to Area.EU or Area.AP for European or Asia-Pacific deployments.
    const client = new AgoraClient({
      area: Area.US,
      appId,
      appCertificate,
    });
    try {
      await client.stopAgent(agent_id);
    } catch (error) {
      if (isAgentAlreadyStoppingOrStopped(error)) {
        // Treat stop as idempotent: agent is already exiting (or gone).
        return NextResponse.json({ success: true, state: 'already-stopping' });
      }
      throw error;
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    stopFailed = true;
    console.error('Error stopping conversation:', error);
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Failed to stop conversation',
      },
      { status: 500 },
    );
  } finally {
    if (postmortem && matched) {
      recordPostmortemEvent(postmortem.traceId, 'agora.stop', { status: stopFailed ? 'failed' : 'accepted' });
      finishPostmortem(postmortem, 'operator_ended');
    }
  }
}
