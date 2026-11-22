'use client';

import { useCallback, useEffect, useState } from 'react';
import { AgoraVoiceAI, ChatMessagePriority } from 'agora-agent-client-toolkit';
import type { ResearchResult } from '@/lib/document-research';
import { isMaintenanceTurn } from '@/lib/maintenance-query';
import { Button } from './ui/button';

function describe(result: ResearchResult) {
  if (result.status === 'done') {
    const sources = result.sources.map(({ source, reference }) => `${source}, ${reference}`);
    return `${result.answer} Fonte: ${sources.join('; ')}.`;
  }
  if (result.status === 'insufficient_evidence') return 'Os trechos recuperados não esclarecem a pergunta.';
  return result.status === 'not_found'
    ? 'Nenhum trecho foi localizado para esta consulta.'
    : 'Não foi possível concluir a consulta ao documento.';
}

export function DocumentResearchPanel({ token, agentUid, utterance }: {
  token: string;
  agentUid: string;
  utterance?: { turn: number; query: string; topic: string };
}) {
  const [results, setResults] = useState<(ResearchResult & { deliveryFailed?: boolean })[]>([]);
  const [playbackError, setPlaybackError] = useState(false);
  const turn = utterance?.turn;
  const query = utterance?.query;
  const topic = utterance?.topic;

  useEffect(() => {
    if (turn === undefined || !query || !isMaintenanceTurn(query, topic)) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      void fetch('/api/document-results', {
        method: 'POST',
        headers: { 'X-Research-Token': token, 'Content-Type': 'application/json' },
        body: JSON.stringify({ turn, query, topic: topic ?? '' }),
        signal: controller.signal,
      }).catch(() => undefined);
    }, 3700);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [token, turn, query, topic]);

  useEffect(() => {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout>;
    async function poll() {
      try {
        const response = await fetch('/api/document-results', {
          headers: { 'X-Research-Token': token },
          signal: controller.signal,
        });
        if (response.status === 401) return controller.abort();
        if (response.ok) {
          const payload: { results: ResearchResult[] } = await response.json();
          if (!controller.signal.aborted) setResults(payload.results);
        }
      } catch {
        // Resume polling after transient network failures.
      } finally {
        if (!controller.signal.aborted) timer = setTimeout(poll, 1200);
      }
    }
    timer = setTimeout(poll, 0);
    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [token]);

  const speak = useCallback(async (result: ResearchResult) => {
    setPlaybackError(false);
    try {
      await AgoraVoiceAI.getInstance().speak(agentUid, {
        text: describe(result),
        priority: ChatMessagePriority.APPEND,
        interruptable: true,
      });
    } catch {
      setPlaybackError(true);
    }
  }, [agentUid]);

  const latest = results.at(-1);
  if (!latest) return null;
  return (
    <section aria-label="Consulta ao documento" className="mx-auto mt-2 w-full max-w-md rounded-md border border-border bg-card p-2 text-xs">
      <p className="font-medium">Consulta ao documento</p>
      <div aria-live="polite" className="max-h-28 overflow-y-auto">
        <p className="text-muted-foreground">{latest.query}</p>
        <p>{latest.status === 'pending' ? 'Pesquisando…' : latest.status === 'done' ? latest.answer : describe(latest)}</p>
        {latest.status === 'done' && (
          <ul className="mt-1 text-muted-foreground">
            {latest.sources.map(({ source, reference }) => <li key={`${source}:${reference}`}>{source} · {reference}</li>)}
          </ul>
        )}
      </div>
      {latest.status === 'done' && <Button type="button" size="sm" variant="ghost" onClick={() => {
        void speak(latest);
      }}>Ouvir resposta</Button>}
      {latest.deliveryFailed && <p role="status">O Agora não confirmou o recebimento da pesquisa. Você pode pedir o resultado na chamada.</p>}
      {playbackError && <p role="status">O resultado está disponível acima. Não foi possível iniciar o áudio.</p>}
    </section>
  );
}
