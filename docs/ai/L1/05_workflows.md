# 05 Workflows

> Repeatable task recipes for common quickstart changes and validation loops.

## Run Locally

1. `pnpm install`
2. `agora login`
3. `agora project use <your-project>`
4. `agora project env write .env.local`
5. `pnpm run doctor`
6. `pnpm run dev`

Open `/` for the person-detection test and Agora panel, or `/voice` for the standalone voice quickstart. Use **Usar exemplo** to validate detection without camera permission; use **Ativar câmera** for live video on localhost/HTTPS. Use **Usar traseira** or **Usar frontal** to select the lens before starting or switch in a live preview. Toggle **Caixa/Círculo**, adjust confidence, then **Parar** to clear annotations and release the camera. **Modelo LTQ** switches to the local MP4 and also releases the camera, without remounting voice. The detector needs no credentials. Start the conversation, click **Compartilhar câmera**, allow video and ask what the agent sees. Switch lens in the conversation controls, or click **Parar vídeo** and continue talking. Sharing releases the local camera first. If camera permission is blocked in the embedded panel, try `/voice` directly and check site permissions. Local annotations stay in the visual test. Validate at least one detection on the sample, both annotation shapes, stop, and tab switching in the browser.

If start fails, run `agora project doctor --deep`.

## Change Agent Behavior

Target file: `app/api/invite-agent/route.ts`.

Typical edits:

- System prompt (`ADA_PROMPT`).
- Greeting default (`GREETING`).
- Shared agent UID (`DEFAULT_AGENT_UID` in `lib/agora.ts`).
- VAD (`turnDetection.config.*`).
- STT/LLM/TTS model/provider blocks.

Validation path:

1. `pnpm run lint`
2. `pnpm run typecheck`
3. `pnpm run verify:api`
4. `pnpm run build`

## Change Token or Session Bootstrap

Token behavior:

- Edit `app/api/generate-agora-token/route.ts`.
- Preserve RTM-capable token generation.

Bootstrap behavior:

- Edit `components/LandingPage.tsx`.
- Keep invite + RTM setup parallelized before conversation mount.

## Change Transcript Rendering

1. Update transforms in `lib/conversation.ts`.
2. Update wiring in `components/ConversationComponent.tsx`.
3. Ensure `IN_PROGRESS` is separated from history, `INTERRUPTED` retained in history.
4. Re-check [transcript_pipeline.md](L2/transcript_pipeline.md) for consistency.

## Ship-Readiness Workflow

1. Run `pnpm run verify`.
2. Confirm docs alignment (`README`, guides, `AGENTS`, `docs/ai`).
3. Use conventional commit and branch naming.

## Progressive Disclosure Doc Workflow

- `generate docs`: create `docs/ai/` tree when absent.
- `update docs`: refresh after workflow/interface/security changes.
- `test docs`: execute question-based validation and write `docs/ai/test-results.md`.
- `fix docs`: close findings from `docs/ai/test-results.md` or a docs review.

## Workflow: Implement a Baseline Recipe Repo

1. Treat this repo as the official Agora Next.js quickstart baseline.
2. Do not recreate Agora ConvoAI integration from memory.
3. Follow [from_scratch_bootstrap.md](L2/from_scratch_bootstrap.md) for the implementation map and checklist.
4. Preserve the recipe invariants in `docs/ai/RECIPE.md`.
5. Run the verification commands before publishing a derivative.

## Workflow: Add a New API Route

1. Add route under `app/api/<route-name>/route.ts`.
2. Define payload types in `types/conversation.ts` if shared with client.
3. Add/update contract verification in `scripts/verify-api-contracts.ts`.
4. Run `pnpm run verify:api` and `pnpm run typecheck`.
5. Update `README.md` and `docs/ai/L1/06_interfaces.md`.

## Workflow: Modify Transcript UX

1. Update transforms in `lib/conversation.ts`.
2. Update render usage in transcript/layout components.
3. Validate edge states (`IN_PROGRESS`, `INTERRUPTED`, empty history).
4. Reconcile guidance in [transcript_pipeline.md](L2/transcript_pipeline.md).
5. Run `pnpm run lint` and `pnpm run build`.

## Workflow: Enable BYOK Provider Path

1. Uncomment relevant provider block in invite route.
2. Add the provider variables shown in the lower README BYOK section to your local environment.
3. Keep default no-key path intact for baseline quickstart behavior.
4. Keep provider variables out of `env.local.example`; they are not part of the base contract.
5. Re-run `pnpm run verify` before shipping.

## Workflow: Docs Refresh After Runtime Changes

1. Update L1 files matching changed subsystem.
2. Update or add L2 deep dives if L1 explanation exceeds concise bounds.
3. Bump `Last Reviewed` in `L0_repo_card.md`.
4. Re-run docs test and append retest notes for any fixes.

## Related Deep Dives

- [conversation_lifecycle.md](L2/conversation_lifecycle.md) — Full runtime sequence for bootstrap and teardown tasks.
- [from_scratch_bootstrap.md](L2/from_scratch_bootstrap.md) — Baseline implementation checklist for recipe consumers.
- [transcript_pipeline.md](L2/transcript_pipeline.md) — Required checks when editing transcript flow.

## Unmute local POC

This checkout is a local Portuguese voice conversation POC. The invite route uses pt-BR STT, Portuguese instructions/greeting, and the original managed LLM/TTS. Tool invocation is disabled. Fill the two Agora variables in `.env.local` before starting a real conversation; no provider keys are required. Main pre-call/transcript/end controls are localized. API contracts and RTC/RTM lifecycle are unchanged.

### Mobile tunnel demo

Build with `pnpm run build`, serve with `pnpm start --hostname 127.0.0.1 --port 3002`, then run `ngrok http 3002`. Use the emitted HTTPS URL on the phone, accept the ngrok informational page, and grant camera/microphone only through their separate controls. Keep both processes running; rebuild/restart after code changes. Local development remains on its original port (3001 in this session). This path avoids tunneling the dev runtime, which may block resources for an unconfigured origin. Tunnel URLs are temporary; do not hardcode one into the app.

To test voice annotation, configure the optional OpenAI key and public HTTPS origin, restart the server, start a fresh call and share the camera. Say “circule a garrafa” and check that the annotation appears on the frozen frame. Stop or leave the call to end sharing.

In a fresh call, verify the maintenance greeting with and without retrieval. The assistant should start with the operator’s report and suggest sharing the camera only when an unresolved visual detail matters. With retrieval disabled, verify that it explains the limitation before advising on a manual-dependent question.

To test document retrieval, configure `RAG_DOCUMENT_PATH`, optionally set `RAG_DOCUMENT_TITLE` and `RAG_DOCUMENT_LANGUAGE`, restart Next.js, and open a fresh call. Describe a relevant maintenance symptom naturally, without saying “manual” or requesting the tool. Check that the agent starts a research job and can continue the conversation while the work is pending. Verify the result and source in the panel and the queued voice playback. Also ask a question with insufficient evidence.

To diagnose missing research, filter the Langfuse project for the current call. Confirm microphone readiness and final transcript events, then compare MCP initialize, tools list and tool invocation. Inspect transcript fallback status and RAG spans if a request was queued. For camera problems, inspect browser.camera for capture, publication and outbound frames, then vision.observar_camera for the explicit visual request.
