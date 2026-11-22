'use client';

import { useState } from 'react';
import { Box, ExternalLink, ScanLine } from 'lucide-react';
import { PersonDetectionTest } from './PersonDetectionTest';
import styles from './LtqWorkspace.module.css';

const MODEL_URL = 'https://studio.tripo3d.ai/3d-model/fef387fa-6acb-404c-9411-045e128f8754';

export function VisualWorkbench() {
  const [view, setView] = useState<'people' | 'ltq'>('people');

  return <section className={styles.modelPanel} aria-label="Laboratório visual">
    <div className={styles.panelHeader}>
      <div className={styles.viewTabs} aria-label="Escolher experiência visual">
        <button type="button" aria-pressed={view === 'people'} onClick={() => setView('people')}><ScanLine size={17} aria-hidden="true" />Teste de pessoas</button>
        <button type="button" aria-pressed={view === 'ltq'} onClick={() => setView('ltq')}><Box size={17} aria-hidden="true" />Modelo LTQ</button>
      </div>
      {view === 'ltq' && <a className={styles.externalLink} href={MODEL_URL} target="_blank" rel="noreferrer">Abrir no Tripo <ExternalLink size={15} aria-hidden="true" /></a>}
    </div>
    {view === 'people' ? <PersonDetectionTest /> : <>
      <div className={styles.modelViewport}>
        <video src="/models/ltq-cadeira-acabadora.mp4" aria-label="Gravação do modelo de cadeira acabadora de LTQ gerado no Tripo" className={styles.modelFrame} controls autoPlay loop muted playsInline preload="metadata">
          Seu navegador não reproduz este vídeo. <a href="/models/ltq-cadeira-acabadora.mp4">Abrir gravação do modelo</a>.
        </video>
      </div>
      <div className={styles.modelFooter}><span>Prévia em vídeo · modelo conceitual gerado por IA</span><span>Tripo H3.1</span></div>
    </>}
  </section>;
}
