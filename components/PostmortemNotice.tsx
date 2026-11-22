'use client';

import { useEffect, useState } from 'react';
import type { PostmortemStatus } from '@/types/postmortem';

export function PostmortemNotice({ token }: { token: string }) {
  const [report, setReport] = useState<PostmortemStatus>();
  const [unavailable, setUnavailable] = useState(false);
  const [retrying, setRetrying] = useState(false);
  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const response = await fetch('/api/postmortems', { headers: { 'X-Postmortem-Token': token }, cache: 'no-store' });
        if (!response.ok) throw new Error('status_unavailable');
        const status: PostmortemStatus = await response.json();
        if (cancelled) return;
        setReport(status);
        setUnavailable(false);
        if (['completed', 'partial', 'failed'].includes(status.status)) return;
      } catch { if (!cancelled) setUnavailable(true); }
      if (!cancelled) timer = setTimeout(poll, 2000);
    };
    void poll();
    return () => { cancelled = true; clearTimeout(timer); };
  }, [token, retrying]);

  const retry = async () => {
    setRetrying(true);
    try {
      const response = await fetch('/api/postmortems', {
        method: 'POST', headers: { 'X-Postmortem-Token': token, 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'retry' }),
      });
      if (!response.ok) { setUnavailable(true); return; }
      setReport(await response.json());
    } catch { setUnavailable(true); }
    finally { setRetrying(false); }
  };
  return (
    <div role="status" className="mx-auto mb-4 w-full max-w-xl rounded-lg border border-border bg-background p-3 text-sm">
      <p className="font-medium">{report?.status === 'completed' ? 'Postmortem salvo.' : report?.status === 'partial' ? 'Postmortem básico salvo.'
        : report?.status === 'failed' ? 'Falha ao salvar o postmortem.' : 'Gerando postmortem da chamada…'}</p>
      {report?.files && <p className="mt-1 break-all text-xs text-muted-foreground">{report.files.markdown}<br />{report.files.json}</p>}
      {report?.notice && <p className="mt-1 text-muted-foreground">{report.notice}</p>}
      {unavailable && <p className="mt-1 text-muted-foreground">Não foi possível atualizar o relatório. Verifique o servidor local.</p>}
      {report && ['partial', 'failed'].includes(report.status) && <button type="button" disabled={retrying} onClick={retry}
        className="mt-2 text-primary underline disabled:opacity-50">{retrying ? 'Solicitando…' : 'Tentar gerar novamente'}</button>}
    </div>
  );
}
