'use client';

import { useEffect, useRef, useState, type RefObject } from 'react';
import { isAnnotationBox, type AnnotationBox, type AnnotationRequest } from '@/lib/vision-annotation';

type Frame = { image: string; width: number; height: number };
type Annotation = Frame & { box: AnnotationBox; target: string };

function captureFrame(preview: HTMLDivElement | null): Frame | null {
  const video = preview?.querySelector('video');
  if (!video || video.readyState < 2 || !video.videoWidth || !video.videoHeight) return null;
  const scale = Math.min(1, 960 / Math.max(video.videoWidth, video.videoHeight));
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(video.videoWidth * scale);
  canvas.height = Math.round(video.videoHeight * scale);
  const context = canvas.getContext('2d');
  if (!context) return null;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  return { image: canvas.toDataURL('image/jpeg', 0.8), width: canvas.width, height: canvas.height };
}

export function useVisionAnnotation(token: string | undefined, preview: RefObject<HTMLDivElement | null>) {
  const [annotation, setAnnotation] = useState<Annotation | null>(null);
  const [status, setStatus] = useState('');
  const generation = useRef(0);

  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    const headers = { 'X-Annotation-Token': token };
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const request = await fetch('/api/vision-annotation', { headers, signal: controller.signal });
        if (request.status === 401) {
          controller.abort();
          return;
        }
        if (!request.ok) return;
        const { job }: { job: AnnotationRequest | null } = await request.json();
        if (!job || controller.signal.aborted) return;
        const frame = captureFrame(preview.current);
        const current = generation.current;
        setAnnotation(null);
        setStatus(frame
          ? job.mode === 'describe' ? 'Analisando o quadro da câmera…' : `Localizando ${job.target}…`
          : 'Compartilhe a câmera para que a assistente possa ver.');
        const response = await fetch('/api/vision-annotation', {
          method: 'PUT',
          headers: { ...headers, 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({ id: job.id, image: frame?.image ?? null }),
        });
        if (!frame || controller.signal.aborted || current !== generation.current) return;
        if (!response.ok) {
          setStatus('Não foi possível analisar a câmera.');
          return;
        }
        const { box, described } = await response.json();
        if (controller.signal.aborted || current !== generation.current) return;
        if (job.mode === 'describe' && described) {
          setStatus('');
        } else if (isAnnotationBox(box)) {
          setAnnotation({ ...frame, box, target: job.target });
          setStatus('');
        } else {
          setStatus(`Não localizei ${job.target} neste quadro.`);
        }
      } catch {
        if (!controller.signal.aborted) setStatus('Não foi possível consultar a marcação.');
      } finally {
        if (!controller.signal.aborted) timer = setTimeout(poll, 750);
      }
    }

    timer = setTimeout(poll, 0);
    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [preview, token]);

  function clearAnnotation() {
    generation.current += 1;
    setAnnotation(null);
    setStatus('');
  }

  return { annotation, status, clearAnnotation };
}
