import Image from 'next/image';
import Link from 'next/link';
import { Headphones, ScanLine, Waves } from 'lucide-react';
import { VisualWorkbench } from './VisualWorkbench';
import styles from './LtqWorkspace.module.css';

export function LtqWorkspace() {
  return (
    <main className={styles.workspace}>
      <header className={styles.header}>
        <Link href="/" className={styles.brand} aria-label="Unmute, início">
          <span className={styles.brandMark}><Waves size={24} aria-hidden="true" /></span>
          <span>unmute<span className={styles.brandDot}>.</span></span>
        </Link>
        <span className={styles.divider} />
        <span className={styles.headerTitle}>Assistência industrial</span>
        <span className={styles.pocBadge}>POC</span>
        <a className={styles.agoraBrand} href="https://www.agora.io/" target="_blank" rel="noreferrer">
          <span>Voz em tempo real com</span>
          <Image src="/agora-logo-rgb-blue.svg" width={85} height={25} alt="Agora" priority />
        </a>
      </header>

      <section className={styles.intro} aria-labelledby="workspace-title">
        <div>
          <p className={styles.eyebrow}>LABORATÓRIO DE ASSISTÊNCIA VISUAL</p>
          <h1 id="workspace-title">A visão em teste.<br className={styles.mobileBreak} /> A conversa ao lado.</h1>
          <p className={styles.description}>Detecte pessoas na câmera e veja as marcações acompanharem a imagem.</p>
        </div>
        <div className={styles.equipmentTag}><ScanLine size={18} aria-hidden="true" /> Teste visual · pessoas</div>
      </section>

      <div className={styles.panels}>
        <VisualWorkbench />

        <section className={styles.voicePanel} aria-labelledby="voice-heading">
          <div className={styles.panelHeader}>
            <div className={styles.panelTitle}><Headphones size={18} aria-hidden="true" /><h2 id="voice-heading">Assistente por voz</h2></div>
            <Image src="/agora-logo-mark.svg" width={24} height={24} alt="Agora" />
          </div>
          <iframe
            src="/voice"
            title="Conversa por voz com Agora e transcrição ao vivo"
            className={styles.voiceFrame}
            allow="microphone; camera; autoplay"
          />
          <p className={styles.voiceFooter}>Na chamada, use Compartilhar câmera para a IA ver o vídeo.</p>
        </section>
      </div>
    </main>
  );
}
