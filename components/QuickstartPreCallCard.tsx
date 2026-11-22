'use client';

import { Loader2, Mic } from 'lucide-react';
import { Button } from '@/components/ui/button';

type QuickstartPreCallCardProps = {
  isLoading: boolean;
  error: string | null;
  onStartConversation: () => void;
};

export function QuickstartPreCallCard({
  isLoading,
  error,
  onStartConversation,
}: QuickstartPreCallCardProps) {
  return (
    <div
      className="mx-auto flex w-[min(92vw,26.25rem)] animate-fade-up flex-col items-center rounded-[20px] border border-[#2b2b2b] px-10 py-10 text-center shadow-[0_10px_24px_rgba(0,0,0,0.28)]"
      style={{
        backgroundImage:
          'linear-gradient(164.988deg, rgba(54,54,54,0.2) 1.0596%, rgba(0,0,0,0) 96.089%), linear-gradient(90deg, rgb(16,16,16) 0%, rgb(16,16,16) 100%)',
      }}
    >
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary"><Mic size={28} aria-hidden="true" /></div>
      <p className="mb-3 text-sm tracking-widest text-primary">UNMUTE / POC</p>
      <h1 className="text-[28px] font-medium leading-[1.2] text-white">
        Vamos conversar?
      </h1>
      <p className="mt-[14px] text-sm font-medium leading-6 text-muted-foreground">
        Fale pelo microfone e ouça a IA responder em tempo real, com transcrição ao vivo.
      </p>

      <Button
        onClick={onStartConversation}
        disabled={isLoading}
        className="mt-12 h-10 w-full rounded-lg border border-primary bg-primary text-sm font-medium text-black hover:border-white hover:bg-white hover:text-black disabled:hover:border-primary disabled:hover:bg-primary disabled:hover:text-black"
        aria-label={
          isLoading
            ? 'Iniciando conversa com a IA'
            : 'Iniciar conversa com a IA'
        }
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Conectando...
          </>
        ) : (
          'Iniciar conversa'
        )}
      </Button>
      <p className="mt-4 text-sm leading-6 text-muted-foreground">Permita o microfone quando solicitado. Você pode interromper a IA e continuar falando.</p>
      {error && <p role="alert" className="mt-3 text-sm text-destructive">{error}</p>}
    </div>
  );
}
