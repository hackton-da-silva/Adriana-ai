import { NextRequest, NextResponse } from 'next/server';
import {
  AgoraClient,
  Agent,
  Area,
  DeepgramSTT,
  ExpiresIn,
  MiniMaxTTS,
  OpenAI,
} from 'agora-agents';
import { ClientStartRequest, AgentResponse } from '@/types/conversation';
import { DEFAULT_AGENT_UID } from '@/lib/agora';
import { createAnnotationSession } from '@/lib/vision-annotation-server';
import { CONSULT_MAINTENANCE_MANUAL, createResearchSession } from '@/lib/document-research';
import { plantMcpServers } from '@/lib/plant-mcp';
import { createPostmortemSession } from '@/lib/postmortem';
import { newCallTrace, traceCall } from '@/lib/call-observability';

const MAINTENANCE_PROMPT = `Você é a assistente de manutenção da Unmute. Ajude o operador a entender o problema da máquina e a decidir o próximo passo para corrigi-lo.
Responda a cada pergunta em português brasileiro, em uma ou duas frases, salvo se pedirem detalhes. Fale sem listas nem Markdown. Aproveite o que o operador já contou e, se faltar um dado importante, faça uma pergunta por vez.
Comece pelo relato do operador. Só sugira ligar a câmera como último recurso, quando restar uma dúvida visual que a conversa e a documentação disponível não resolveram. Diga qual detalhe ajudaria, como o código no painel. Se o operador preferir, ele pode ler ou descrever o detalhe. Se ele já pediu ajuda visual, atenda ao pedido. Descreva somente o que conseguir ver.
Diferencie observações de causas confirmadas. Nunca improvise procedimentos, ajustes ou valores. Se faltar base para orientar a intervenção, explique o que falta e encaminhe à manutenção responsável quando necessário.`;

const GREETING = 'Oi! Sou a assistente de manutenção da Unmute. O que está acontecendo com a máquina?';
const ANNOTATION_INSTRUCTIONS = 'Para pedidos sobre o que está na câmera agora, como “o que você está vendo?” ou “que objeto estou mostrando?”, chame observar_camera. Se retornar described, descreva em voz alta o que ela encontrou. Para circular, apontar ou destacar algo, chame circular_objeto. Só confirme a marcação após status marked. Para not_found, diga que não localizou. Para camera_off, peça para compartilhar a câmera. Se o pedido for apenas visual, use a ferramenta de câmera; só consulte o manual se também pedirem orientação técnica.';
const DOCUMENT_INSTRUCTIONS = `Ao ouvir um sintoma de rolamento, use ${CONSULT_MAINTENANCE_MANUAL} com o componente e o relato do operador. Com queued, avise que a pesquisa começou e libere o turno. Se pedirem o andamento, use consultar_resultado pelo ID.
Ao receber “Retorno da pesquisa no manual”, responda à pergunta original usando o resultado como evidência. Cite a seção ou página aplicável. Informe se a busca falhou ou se o manual não esclarece o caso.`;

// agentUid identifies the AI in the RTC channel and shares its default with the client.
const agentUid = String(DEFAULT_AGENT_UID);

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required environment variable: ${name}`);
  return value;
}

export async function POST(request: NextRequest) {
  const trace = newCallTrace();
  const startedAt = Date.now();
  let postmortem: ReturnType<typeof createPostmortemSession>;
  let annotation: ReturnType<typeof createAnnotationSession>;
  let research: Awaited<ReturnType<typeof createResearchSession>>;
  try {
    // --- 1. Parse request ---

    const body: ClientStartRequest = await request.json();
    const { requester_id, channel_name } = body;

    // Validate required env vars on first request so misconfiguration surfaces
    // with a clear error message rather than a silent failure.
    const appId = requireEnv('NEXT_PUBLIC_AGORA_APP_ID');
    const appCertificate = requireEnv('NEXT_AGORA_APP_CERTIFICATE');

    if (!channel_name || !requester_id) {
      return NextResponse.json(
        { error: 'channel_name and requester_id are required' },
        { status: 400 },
      );
    }

    // --- 2. Build and start the agent ---

    // AgoraClient authenticates API calls to the Agora Conversational AI service.
    // area: change to Area.EU or Area.AP for European or Asia-Pacific deployments.
    const client = new AgoraClient({
      area: Area.US,
      appId,
      appCertificate,
    });

    // Pipeline: Deepgram (reseller) STT → OpenAI (reseller) LLM → MiniMax (reseller) TTS.
    // Omit vendor API keys for supported models — AgentKit infers reseller presets on start (see Agora Console / billing).
    postmortem = createPostmortemSession(trace.traceId);
    annotation = createAnnotationSession(trace);
    const plant = plantMcpServers(postmortem?.toolToken);
    research = await createResearchSession(trace, plant.length > 0);
    const documentLanguage = process.env.RAG_DOCUMENT_LANGUAGE?.trim();
    const servers = research ? [...plant, research.server] : plant;
    const instructions = [
      MAINTENANCE_PROMPT,
      annotation && ANNOTATION_INSTRUCTIONS,
      plant.length > 0 && 'Os dados da planta LTQ são simulados. Para alarmes use status_clp, para leituras use status_maquina e para tendência use historico. Reaproveite o equipamento mencionado; se houver ambiguidade, pergunte. Antes de orientar, consulte consultar_documentacao_equipamento_ltq com o equipamento e o código, tag ou sintoma. Para convenções gerais use consultar_manual_clp. Use o manual SKF para questões de rolamentos. Se uma ferramenta falhar, informe a indisponibilidade e nunca invente leituras.',
      research ? DOCUMENT_INSTRUCTIONS : 'Nesta conversa a consulta ao manual SKF está indisponível. Quando a pergunta depender do manual, informe essa limitação e peça o trecho ou a identificação do equipamento para continuar a triagem.',
      research && documentLanguage && `O manual está no idioma ${documentLanguage}. Passe também search_terms nesse idioma ao chamar ${CONSULT_MAINTENANCE_MANUAL} e responda em português.`,
    ].filter(Boolean).join('\n');
    const agent = new Agent({
      client,
      instructions,
      greeting: GREETING,
      failureMessage: 'Um momento, por favor.',
      maxHistory: 50,
      // VAD controls how the agent detects the start and end of a user's turn.
      turnDetection: {
        config: {
          speech_threshold: 0.5,
          start_of_speech: {
            mode: 'vad',
            vad_config: {
              interrupt_duration_ms: 160, // ms of speech before interruption triggers
              prefix_padding_ms: 300, // audio captured before speech is detected
            },
          },
          end_of_speech: {
            mode: 'vad',
            vad_config: {
              silence_duration_ms: 480, // ms of silence before turn ends
            },
          },
        },
      },
      // RTM is required for transcript events in the browser client.
      advancedFeatures: { enable_rtm: true, enable_tools: Boolean(annotation || servers.length) },
      // Required for browser RTM events:
      // - data_channel: 'rtm' enables RTM delivery path for state/metrics/errors
      // - enable_error_message emits AGENT_ERROR payloads
      // - enable_metrics emits AGENT_METRICS latency payloads
      parameters: {
        // web client → ultra-low-latency chorus profile
        audio_scenario: 'chorus',
        data_channel: 'rtm',
        enable_error_message: true,
        enable_metrics: true,
      },
    })
      .withStt(
        new DeepgramSTT({
          model: 'nova-3',
          language: 'pt-BR',
        }),
        // BYOK: uncomment the following block and set NEXT_DEEPGRAM_API_KEY
        // new DeepgramSTT({
        //   apiKey: requireEnv('NEXT_DEEPGRAM_API_KEY'),
        //   model: 'nova-3',
        //   language: 'pt-BR',
        // }),
      )
      .withLlm(
        new OpenAI({
          model: 'gpt-4o-mini',
          inputModalities: ['text', 'image'],
          tools: annotation?.tools,
          mcpServers: servers.length ? servers : undefined,
          greetingMessage: GREETING,
          failureMessage: 'Um momento, por favor.',
          maxHistory: 15,
          params: {
            max_tokens: 1024,
            temperature: 0.7,
            top_p: 0.95,
          },
        }),
        // BYOK: uncomment the following block and set NEXT_LLM_API_KEY and NEXT_LLM_URL
        // new OpenAI({
        //   apiKey: requireEnv('NEXT_LLM_API_KEY'),
        //   url: requireEnv('NEXT_LLM_URL'),
        //   model: 'gpt-4o-mini',
        //   greetingMessage: GREETING,
        //   failureMessage: 'Um momento, por favor.',
        //   maxHistory: 15,
        //   maxTokens: 1024,
        //   temperature: 0.7,
        //   topP: 0.95,
        // }),
      )
      .withTts(
        new MiniMaxTTS({
          model: 'speech_2_6_turbo',
          voiceId: 'English_captivating_female1',
        }),
        // BYOK — ElevenLabs (set NEXT_ELEVENLABS_API_KEY; optional NEXT_ELEVENLABS_VOICE_ID)
        // new (await import('agora-agents')).ElevenLabsTTS({
        //   key: requireEnv('NEXT_ELEVENLABS_API_KEY'),
        //   modelId: 'eleven_flash_v2_5',
        //   voiceId: process.env.NEXT_ELEVENLABS_VOICE_ID ?? 'pNInz6obpgDQGcFmaJgB',
        //   sampleRate: 24000,
        // }),
      );

    // remoteUids restricts the agent to only process audio from this user
    const session = agent.createSession({
      channel: channel_name,
      agentUid,
      remoteUids: [requester_id],
      idleTimeout: 30,
      expiresIn: ExpiresIn.hours(1),
      debug: false, // enable debug to show restful API calls in the console
    });

    const agentId = await session.start();
    postmortem?.bindAgent(agentId);
    research?.bindDelivery((result) => session.think(
      `Retorno da pesquisa no manual: ${JSON.stringify(result)}`,
      {
        on_listening_action: 'append',
        on_thinking_action: 'append',
        on_speaking_action: 'append',
        metadata: { jobId: result.id },
      },
    ));
    traceCall(trace, {
      name: 'agora.invite', type: 'agent', root: true, startedAt,
      input: { operation: 'start_session', speechLanguage: 'pt-BR', imageInput: true, ragRequested: Boolean(process.env.RAG_DOCUMENT_PATH) },
      data: { status: 'running', plantConfigured: plant.length > 0, researchConfigured: Boolean(research), cameraToolConfigured: Boolean(annotation) },
    });

    return NextResponse.json({
      agent_id: agentId,
      create_ts: Math.floor(Date.now() / 1000),
      state: 'RUNNING',
      ...(postmortem && { postmortem_token: postmortem.token }),
      ...(annotation && { annotation_token: annotation.token }),
      ...(research && { research_token: research.token }),
    } as AgentResponse);
  } catch (error) {
    traceCall(trace, { name: 'agora.invite', type: 'agent', root: true, startedAt, error: true, input: { operation: 'start_session' } });
    postmortem?.discard();
    annotation?.discard();
    research?.discard();
    console.error('Error starting conversation:', error);
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Failed to start conversation',
      },
      { status: 500 },
    );
  }
}
