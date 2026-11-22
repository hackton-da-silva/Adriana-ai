# BOB-01 — Bobinadeira hidráulica 1 — documentação de referência

> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

- A bobinadeira (down coiler) é a última máquina da linha de tira a quente. Fica depois da mesa de resfriamento (Linha 4 — Resfriamento e bobinamento).
- Ela recebe a tira laminada e resfriada e a enrola em bobina, para transporte e processamento posterior.
- Também mantém tração na tira entre o último cadeira do acabamento e a bobinadeira. Essa tração ajuda a estabilizar a tira na mesa.
- A bobina precisa sair com enrolamento justo e alinhado, para não "telescopar", não ovalizar e não marcar a superfície.
- Na Usina exemplo: mandril Ø 762 mm, 4 wrapper rolls, bobina até 35 t, velocidade de 8 a 20 m/s.
- A BOB-02 é a outra bobinadeira, documentada à parte. Este documento trata do funcionamento geral e do pinch roll.

## 2. Princípio de funcionamento

Sequência de um ciclo de bobinamento:

1. **Pré-posição.** Mandril expandido e girando em velocidade ligeiramente acima da tira (leading). Pinch roll e wrapper rolls abertos, guias e aventais posicionados.
2. **Cabeça da tira.** A ponta passa pelo pinch roll. O pinch fecha em controle de posição e, depois que a tira entra, passa a controle de força de aperto (hidráulico). Gira um pouco mais rápido que a tira, o que dá uma tração leve.
3. **Início do enrolamento.** A tira é guiada pelo avental até o mandril. Os wrapper rolls pressionam as primeiras voltas contra o mandril para formar o núcleo da bobina.
4. **Salto dos wrapper rolls (AJC).** Na primeira volta há um degrau entre a ponta da tira e a segunda camada. O wrapper roll que encontra o degrau levanta ("salta") um pouco acima da espessura da tira e volta a descer depois que o degrau passa. Isso evita marcas e pico de força. Os fabricantes chamam o controle de automatic jump control (AJC) ou step control.
5. **Tração de bobinamento.** Com a tira presa no mandril, o mandril passa a controlar torque. A tração é definida por referência de torque, conforme grau e temperatura de bobinamento. O pinch roll ajuda a isolar a tração do resto da linha.
6. **Cauda.** Perto do fim, a tração do pinch é elevada para igualar a do mandril. Quando a cauda sai da última cadeira, o pinch assume a tira e a bobina termina de enrolar em velocidade reduzida. Os wrapper rolls fecham na cauda para prender as últimas voltas.
7. **Extração.** O mandril contrai (colapsa), o carro de bobina (coil car) sobe, retira a bobina e a entrega ao transportador. Depois o mandril volta a expandir.

Observações de mecanismo:

- Os wrapper rolls geram um torque que freia o mandril. Isso pode afrouxar a tira entre pinch e wrapper e causar excesso de tira (folga). O controle compensa.
- As tensões normais na bobina vêm de três fontes: tração de bobinamento, pressão dos wrapper rolls e expansão/contração do mandril. Oscilação do mandril contribui para o colapso da bobina (sagging).
- Telescopagem aumenta quando a mesa desacelera na cabeça e na cauda da bobina, porque a bobinadeira perde parte da capacidade de manter o enrolamento justo.

## 3. Componentes principais

| Componente | Função | Observação |
|---|---|---|
| Pinch roll (rolo superior e inferior) | Guia e tensiona a tira na entrada da bobinadeira | Hidráulico, um cilindro por lado (lado operador e lado acionamento) |
| Avental / guias laterais | Conduzem a ponta da tira ao mandril | Posição ajustada por largura |
| Wrapper rolls (4 na Usina exemplo) | Pressionam as primeiras voltas contra o mandril | Cada um com cilindro hidráulico e controle de posição/força |
| Mandril expansível | Eixo de enrolamento, expande e contrai | Eixo central + segmentos; acionado por cilindro hidráulico |
| Acionamento do mandril | Motor, redutor e inversor | Controle de velocidade e torque |
| Unidade hidráulica | Pressão para pinch, wrapper e mandril | Bombas, acumuladores, servoválvulas |
| Lubrificação | Mancais dos wrapper rolls, pinch e mandril | Graxa ou óleo-ar |
| Carro de bobina (coil car) | Extrai a bobina do mandril | Ponta de apoio e elevação |
| Sensores | Força, posição, pressão, temperatura, diâmetro, peso | Ver seção 5 |

Materiais de referência de mercado: a SMS group cita 4 wrapper rolls e espessuras até 25,4 mm; a Danieli, 1,2 a 25,4 mm; a Primetals, bobinas até 32 t. A SMS também destaca que cilindros hidráulicos, wrapper rolls e placas curvas do avental são itens de desgaste e precisam de troca periódica.

## 4. Parâmetros típicos de operação

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| Tensão de bobinamento | Definida por grau e temperatura; ajustada por torque no mandril. Faixa depende do projeto | Ideal 110 kN; normal 20–200 kN | AI001 |
| Força do pinch roll, lado operador | Depende de espessura e grau; controle de força após a entrada da tira | Ideal 175 kN; normal 50–300 kN | AI002 |
| Força do pinch roll, lado acionamento | Igual ao lado operador (simetria entre lados) | Ideal 175 kN; normal 50–300 kN | AI003 |
| Assimetria do gap do pinch | Quanto menor, melhor; poucas décimas de mm | Ideal 0 mm; normal 0–0,5 mm; alarme 0,5 mm | AI004 |
| Erro de posição do wrapper no degrau | Poucos mm no salto do AJC | Ideal 0 mm; normal 0–2 mm; alarme 3 mm | AI005 |
| Temperatura do mancal do wrapper | Mancais de rolo com graxa em geral operam abaixo de cerca de 80–90 °C | Ideal 62,5 °C; normal 40–85 °C; alarme 85 °C | AI006 |
| Diâmetro da bobina | Do diâmetro do mandril até cerca de 2 m | Normal 762–2100 mm (valor da última bobina) | AI007 |
| Peso da bobina | Até 32 t (referência Primetals); alguns projetos vão além | Normal 10–35 t (última bobina) | AI008 |
| Pressão de expansão do mandril | Depende do projeto hidráulico | Ideal 150 bar; normal 100–200 bar; alarme baixo 90 bar | AI009 |
| Telescopia | Idealmente zero; tolerâncias de poucos mm | Ideal 0 mm; normal 0–5 mm; alarme 10 mm | AI010 |
| Velocidade de bobinamento | Varia muito conforme a linha | 8–20 m/s | (sem tag) |
| Diâmetro do mandril | Valores comuns na faixa de 600–800 mm | 762 mm | (sem tag) |

Nota: as fontes públicas encontradas não trazem valores de tensão em kN nem de pressão de mandril. As faixas "na indústria" acima são ordens de grandeza gerais ou dependem do projeto de cada fabricante. Para a planta, vale a simulação.

## 5. Instrumentação e sinais do CLP

CLP: CLP-BOB-01. Cada tag pertence a uma área (bit das palavras de falha e de aviso). Alarmes seguem o código AAKK (AA = bit da área, KK = tipo).

| Tag | Variável | Área (bit) | O que indica |
|---|---|---|---|
| AI001 | tensao_bobinamento | FORCA_CARGA (14) | Tração aplicada à tira; baixa gera bobina frouxa, alta gera esforço no mandril |
| AI002 | forca_pinch_lo | FORCA_CARGA (14) | Força de aperto do pinch no lado operador |
| AI003 | forca_pinch_la | FORCA_CARGA (14) | Força de aperto do pinch no lado acionamento |
| AI004 | assimetria_gap_pinch | POSICAO_GEOMETRIA (7) | Diferença de abertura entre os lados do pinch |
| AI005 | erro_posicao_wrapper | POSICAO_GEOMETRIA (7) | Erro de posição do wrapper no degrau (AJC) |
| AI006 | t_mancal_wrapper | LUBRIFICACAO (2) | Temperatura do mancal do wrapper |
| AI007 | diametro_bobina | MATERIAL_FLUXO (12) | Diâmetro da última bobina |
| AI008 | peso_bobina | MATERIAL_FLUXO (12) | Peso da última bobina |
| AI009 | pressao_expansao_mandril | HIDRAULICA (1) | Pressão que mantém o mandril expandido |
| AI010 | telescopia | QUALIDADE (9) | Deslocamento axial entre espiras da bobina |

Como ler:

- **Bit 14 (FORCA_CARGA)** com diferença entre AI002 e AI003 aponta pinch assimétrico. Compare os dois lados antes de olhar a tração.
- **Bit 7 (POSICAO_GEOMETRIA)** pode ser gap do pinch (AI004) ou wrapper no degrau (AI005). O tag diz qual.
- **Bit 2 (LUBRIFICACAO)** é aquecimento do mancal do wrapper. Alarme em 85 °C (código 0202 se acima do limite).
- **Bit 1 (HIDRAULICA)** com AI009 abaixo de 90 bar gera alarme de valor baixo (código 0101). Indica risco de o mandril não segurar a bobina.
- **Bit 9 (QUALIDADE)** com AI010 acima de 10 mm gera alarme (código 0902). É o resultado final de falhas a montante dentro da máquina.
- **Bit 12 (MATERIAL_FLUXO)** vale para diâmetro e peso; sem limites de alarme na simulação. Uma parada por cobble usa o código 1260.
- Lanterna: vermelho = alarme, amarelo = aviso, azul = manutenção requerida, verde = produzindo. Em cobble o estado é Aborted.

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Bobina telescopada | QUALIDADE (9) / AI010; FORCA_CARGA (14) / AI002, AI003 | Pinch assimétrico: gap diferente entre lados, força desigual | Comparar AI002 com AI003; ler AI004 | Ajustar o gap do pinch roll; confirmar centralização da tira |
| Gap do pinch assimétrico | POSICAO_GEOMETRIA (7) / AI004 | Desgaste ou folga em cilindro, calibração de posição fora, calço ou guia | Ler AI004 e histórico; checar transdutores de posição | Recalibrar posição; revisar cilindros e guias |
| Marcas de wrapper | POSICAO_GEOMETRIA (7) / AI005 | Pico de força no degrau; salto do wrapper atrasado ou fora de posição | Ler AI005; ver sequência do AJC | Revisar o step control dos wrapper rolls; checar servoválvulas |
| Mancal do wrapper aquecendo | LUBRIFICACAO (2) / AI006 | Falta de graxa, bomba ou linha entupida, mancal desgastado | Ler AI006 e tendência; inspecionar graxa e linhas | Inspecionar a lubrificação; trocar mancal se persistir |
| Bobina ovaliza ou colapsa | HIDRAULICA (1) / AI009 | Pressão de expansão baixa, vazamento no cilindro ou no sistema do mandril | Ler AI009 contra 90 bar; testar vazamento | Testar vazamento do mandril; trocar vedações |
| Tensão fora da faixa | FORCA_CARGA (14) / AI001 | Erro de referência de torque, acionamento do mandril, deslizamento da tira | Ler AI001; comparar com referência de grau | Verificar acionamento e referência; ajustar tensão |
| Cobble na entrada da bobinadeira | MATERIAL_FLUXO (12); código 1260 | Tira que não entra no pinch ou no avental; guia desalinhada | Ver posição do avental; ler AI004 | Limpar sucata, revisar guias. Parada de cerca de 4 h na simulação |
| Bobina fora de peso ou diâmetro | MATERIAL_FLUXO (12) / AI007, AI008 | Erro de comprimento de tira, cortes fora de sequência | Ler AI007 e AI008; comparar com programa | Revisar programa de laminação e medição |

Ordem prática de diagnóstico:

1. Ver a lanterna e a palavra de falha. Anotar os bits ligados.
2. Ler os alarmes e as tags da área.
3. Comparar os dois lados do pinch (AI002 contra AI003, AI004).
4. Comparar com o histórico para datar o início do desvio.
5. Seguir o fluxo a montante e a jusante.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

- **Telescopagem.** A bobina sai com bordas desalinhadas. Pode ser rejeitada ou exigir corte de borda e reprocesso. Dificulta a pega em laminação a frio e decapagem.
- **Marcas de wrapper.** Marcas periódicas nas primeiras e últimas voltas. Perdem-se metros de tira nas pontas. Podem transferir marca para voltas vizinhas.
- **Ovalização.** A bobina ovalizada não encaixa bem no desbobinador. Pode cair no transporte e atrasar a extração.
- **Cobble.** Para a linha, pode causar parada de cerca de 4 h na simulação, com perda de produção e risco para a mesa e a cadeira final.
- **Tração instável.** Afeta a tração na mesa de resfriamento e o controle da última cadeira. Pode afetar largura e espessura nas pontas.
- **Temperatura da bobina.** A bobina quente resfria lentamente; enrolamento frouxo muda a transferência de calor e as propriedades mecânicas locais.
- **Equipamentos seguintes.** Estação de cintagem, balança, transportador de bobinas e pátio recebem a bobina. Bobina fora de forma causa problemas de manuseio.

## 8. Manutenção preventiva e preditiva

| Item | Periodicidade típica | Inspeção ou ação |
|---|---|---|
| Mancais e pressão do pinch | A cada bobina (monitoramento) | Acompanhar AI006, AI002 e AI003 |
| Gap do pinch | A cada turno | Verificar simetria (AI004) e calibração |
| Vazamento do mandril | Trimestral | Teste de vazamento, vedações, pressão (AI009) |
| Retífica de pinch e wrapper rolls | A cada 2–4 semanas | Retificar ou trocar rolos; medir desgaste e rugosidade |
| Lubrificação | Conforme plano do fabricante | Conferir pontos de graxa, linhas e distribuidores |
| Segmentos e articulações do mandril | Em paradas programadas | Medir desgaste, folgas, pinos e buchas |
| Cilindros hidráulicos | Em paradas programadas | Vedações, hastes, vazamentos externos |
| Servoválvulas e filtros | Conforme plano hidráulico | Trocar filtros; testar resposta da servoválvula |
| Avental e guias | Em paradas programadas | Placas de desgaste, alinhamento |

- Itens de desgaste (rolos, cilindros, placas curvas do avental) são trocados periodicamente. Conceitos modernos buscam acesso fácil e troca rápida.
- Preditivo: tendência de temperatura do mancal, vibração do acionamento, queda lenta de pressão do mandril, aumento do erro do wrapper no degrau.
- Os intervalos acima da Usina exemplo (por bobina, turno, trimestral, 2–4 semanas) vêm do manual gerado. Outros intervalos são referência geral.

## 9. Segurança

- **Bloqueio e etiquetagem (LOTO).** Antes de qualquer intervenção: bloquear acionamento do mandril, bombas hidráulicas e energia elétrica. Despressurizar e drenar acumuladores. Zerar energia armazenada.
- **Energia hidráulica.** Cilindros podem se mover com pressão residual. Travar mecanicamente pinch, wrapper rolls e carro de bobina com calços ou pinos.
- **Pontos de esmagamento.** Entre pinch rolls, wrapper e mandril; entre carro de bobina e estrutura.
- **Mandril expandindo ou contraindo.** Nunca entrar na área com o mandril em movimento. Bobina pode deslizar ou cair ao contrair.
- **Tira e bobina quentes.** Risco de queimadura e radiação. A cauda solta da tira pode chicotear.
- **Cobble.** Remoção de sucata só com a linha bloqueada e a tira fria ou resfriada. Usar ferramentas e EPI adequados.
- **Intertravamentos.** Não anular proteções ou barreiras. Falha de segurança aparece na área SEGURANCA (bit 10).
- **Trabalho em altura e espaço confinado.** Pode ocorrer dentro da fossa do carro de bobina.

## 10. Perguntas frequentes do operador

**1. O que é telescopagem e qual a causa mais comum?**
É quando as espiras da bobina deslizam de lado e formam uma saliência. Na Usina exemplo, a causa mais comum é o pinch assimétrico. Confira o gap e a força dos dois lados.

**2. A luz vermelha acendeu com FORCA_CARGA. O que olho primeiro?**
Compare a força do pinch do lado operador com a do lado acionamento. Se forem diferentes, ajuste o gap do pinch.

**3. O que é o salto do wrapper roll?**
O wrapper levanta um pouco quando passa o degrau da primeira volta da tira. Evita marcas e pico de força. Se o erro de posição passar de 3 mm, revise o step control.

**4. Por que a pressão do mandril importa?**
Ela mantém o mandril expandido. Abaixo de 90 bar dispara alarme. Pode ovalizar ou soltar a bobina. Teste vazamento.

**5. Qual a temperatura máxima do mancal do wrapper?**
O alarme é em 85 °C. A faixa normal é de 40 a 85 °C, com valor ideal em torno de 62 °C. Inspecione a lubrificação.

**6. Qual o limite de telescopia?**
Normal até 5 mm. Alarme em 10 mm.

**7. Quanto tempo dura uma parada por cobble?**
Na simulação, cerca de 4 horas, com a linha em Aborted.

**8. Com que frequência se retificam os rolos?**
A cada 2 a 4 semanas para pinch e wrapper rolls.

## Fontes

- [US6648264 — Method and apparatus for coiling a metal strip (sinal de wrapper no fim da tira, wrapper roll e degrau)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6648264)
- [US6604663 — Control method of hydraulic pinch roll and control unit thereof (troca de controle de posição para controle de força)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6604663)
- [US6301946 — Strip coiling method (wrapper rolls, mandril e tração)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6301946)
- [US5950476 — Method and apparatus to tension hot strip during coiling (tração do pinch roll e do mandril)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5950476)
- [US4107969 — Hot strip coiling mandrel (mandril de bobinadeira de tira a quente)](https://patents.google.com/patent/US4107969A/Direct)
- [US3763684 — Downcoiler mandrel of the toggle link type for hot strip mills (mandril articulado, desgaste)](https://patents.google.com/patent/US3763684A/en)
- [SMS group — New easy-to-maintain concept for downcoilers (marcas no início do bobinamento, itens de desgaste)](https://sms-group.com/insights/all-insights/new-easy-to-maintain-concept-for-downcoilers)
- [AIST — artigo sobre controle de coil sagging, Nov. 2025 (tensões normais na bobina: tração, wrapper rolls, mandril)](https://www.aist.org/getmedia/46c30e09-22f0-4ae8-886f-a305425a6584/November-2025-044-052.pdf)
- [US4773245 — Strip guiding apparatus for downcoilers (guias e avental)](https://patents.google.com/patent/US4773245)
