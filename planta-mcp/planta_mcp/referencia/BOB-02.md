# BOB-02 — Bobinadeira hidráulica 2 — documentação de referência

> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

- A bobinadeira (down coiler) é o último equipamento da linha de tira a quente.
- Ela recebe a tira após a mesa de resfriamento laminar (Linha 4 — Resfriamento e bobinamento).
- Enrola a tira em bobina, sob tensão controlada, para estocagem e transporte.
- Na Usina exemplo, a BOB-02 trabalha com mandril Ø 762 mm, 4 wrapper rolls, bobina até 35 t e velocidade de 8 a 20 m/s.
- Opera em alternância com a BOB-01: uma enrola enquanto a outra descarrega a bobina e se prepara.
- Referências de mercado: SMS (4 wrapper rolls, até 25,4 mm), Danieli (1,2–25,4 mm), Primetals (até 32 t).
- A qualidade da bobina (forma, bordas, aperto) define o que o cliente e as linhas seguintes recebem.

## 2. Princípio de funcionamento

Ciclo de uma bobina, resumido:

1. **Preparação.** O mandril está contraído e posicionado. Os wrapper rolls abrem. O pinch roll abre para a passagem da cabeça da tira.
2. **Threading (enfiamento).** A cabeça da tira sai do último castelo e passa pela mesa de saída. Entra no pinch roll e é guiada pela calha (apron) até o mandril.
3. **Captura.** Os wrapper rolls fecham e pressionam a cabeça contra o mandril. As primeiras voltas ficam presas. O mandril expande por pressão hidráulica.
4. **Tensão de bobinamento.** Com a cauda ainda no laminador, a bobinadeira tensiona a tira entre o último castelo e o mandril. Essa tensão é mantida durante o enrolamento.
5. **Step control.** Quando o degrau da cabeça (a espessura da tira sobre a primeira volta) passa sob cada wrapper roll, o rolo recua ou reduz a força por um instante. Isso evita marcas por sobreposição. Patentes descrevem reduzir a força do wrapper para valores baixos durante a passagem do degrau.
6. **Corpo da bobina.** Os wrapper rolls abrem à medida que o diâmetro cresce, ou são retirados após poucas voltas. O pinch roll controla a tensão entre ele e o mandril.
7. **Cauda.** O laminador solta a tira. O pinch roll segura a cauda e a tensão cai. Os wrapper rolls podem voltar a pressionar para fechar a bobina.
8. **Descarga.** O mandril contrai. O carro de bobinas (coil car) sobe, recebe a bobina e a leva para o transporte. O mandril expande de novo e a outra bobinadeira assume a próxima tira.

Ideias-chave:

- A tensão de bobinamento é o principal ajuste da forma da bobina. Tensão baixa solta a bobina. Tensão alta deforma o mandril e as camadas internas.
- O pinch roll é hidráulico. Sua inércia é grande e a força sozinha não elimina variações de tensão causadas pela excentricidade da bobina em formação. Alguns sistemas compensam a posição do pinch roll.
- O conjunto precisa de simetria entre lado operador (LO) e lado acionamento (LA). Qualquer assimetria empurra a tira para um lado.

## 3. Componentes principais

| Componente | Função | Pontos de desgaste / falha |
|---|---|---|
| Mandril expansível | Sustenta a bobina; expande por segmentos | Segmentos, chavetas cônicas (taper keys), selo do pistão de expansão, mancais |
| Cilindro hidráulico de expansão | Gera a pressão que abre os segmentos | Selo do pistão com bypass interno (vazamento lento) |
| Wrapper rolls (4) | Pressionam a cabeça contra o mandril nas primeiras voltas | Mancais, superfície (trincas, marcas), cilindros hidráulicos, mecanismo de ajuste de gap |
| Pinch roll (LO e LA) | Guia e segura a tira, controla tensão a montante do mandril | Retífica, cilindros, assimetria de gap, carepa aderida |
| Calha (apron) e guias laterais | Conduzem a cabeça ao mandril; centralizam a tira | Desgaste de placas curvas, gap de guia |
| Redutor e motor do mandril | Acionam o mandril e dão a tensão | Óleo do redutor, alinhamento, corrente do motor |
| Unidade hidráulica (HPU) | Alimenta mandril, wrapper rolls e pinch roll | Filtros, bombas, válvulas servo, acumuladores |
| Carro de bobinas (coil car) | Retira a bobina do mandril e a leva ao transporte | Cilindros de elevação, trilhos, posicionamento |
| Sistema de lubrificação | Mancais de wrapper, pinch e mandril | Bomba, linhas entupidas, graxa/óleo inadequado |

Observação de mercado: fabricantes citam que cilindros hidráulicos, wrapper rolls e placas curvas da calha são peças de reposição periódica. Existem conceitos de troca rápida para encurtar essas paradas.

## 4. Parâmetros típicos de operação

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| Tensão de bobinamento | Depende de espessura, largura e aço; picos de até cerca de 200 kN são citados em fonte técnica | Ideal 110 kN; normal 20–200 kN | AI001 |
| Força do pinch roll, lado operador | Definida pelo modelo de bobinamento; deve ser igual entre os lados | Ideal 175 kN; normal 50–300 kN | AI002 |
| Força do pinch roll, lado acionamento | Idem | Ideal 175 kN; normal 50–300 kN | AI003 |
| Assimetria do gap do pinch | Fonte técnica cita deriva LO/LA acima de 0,5 mm causando telescopia | Ideal 0; normal 0–0,5 mm; alarme acima de 0,5 mm | AI004 |
| Erro de posição do wrapper no degrau | Fonte técnica cita variação do braço acima de 3 mm entre bobinas de mesma bitola como sinal de enrolamento inconsistente | Ideal 0; normal 0–2 mm; alarme acima de 3 mm | AI005 |
| Temperatura do mancal do wrapper | Alerta típico de 85 °C; tendência de alta em 10 bobinas seguidas também é alerta | Ideal 62,5 °C; normal 40–85 °C; alarme acima de 85 °C | AI006 |
| Diâmetro da bobina | Do diâmetro do mandril até cerca de 2 m ou mais | Normal 762–2100 mm (Ø do mandril 762 mm) | AI007 |
| Peso da bobina | Até 32 t em oferta de mercado; varia por projeto | Normal 10–35 t | AI008 |
| Pressão de expansão do mandril | Específica de cada projeto; não encontrei faixa pública | Ideal 150 bar; normal 100–200 bar; alarme abaixo de 90 bar | AI009 |
| Telescopia | Tolerância em mm definida por norma do cliente | Ideal 0; normal 0–5 mm; alarme acima de 10 mm | AI010 |
| Velocidade de entrada na bobinadeira | Até 20 m/s em fontes de fabricantes | 8–20 m/s (dado de projeto, sem tag) | — |

Divergências a lembrar: a fonte técnica trata 0,5 mm de assimetria como limite de problema, e a simulação usa 0,5 mm como alarme. A telescopia na simulação alarma só acima de 10 mm, mas já há aviso acima de 5 mm.

## 5. Instrumentação e sinais do CLP

CLP: CLP-BOB-02. Cada área é um bit nas palavras de falha e de aviso. Cores da lanterna: vermelho = alarme, amarelo = aviso, azul = manutenção, verde = produzindo.

| Área do CLP | Bit | Tags | O que mede |
|---|---|---|---|
| HIDRAULICA | 1 | AI009 | Pressão de expansão do mandril |
| LUBRIFICACAO | 2 | AI006 | Temperatura do mancal do wrapper |
| POSICAO_GEOMETRIA | 7 | AI004, AI005 | Simetria do gap do pinch; erro de posição do wrapper no degrau |
| QUALIDADE | 9 | AI010 | Telescopia da bobina |
| MATERIAL_FLUXO | 12 | AI007, AI008 | Diâmetro e peso da última bobina |
| FORCA_CARGA | 14 | AI001, AI002, AI003 | Tensão de bobinamento e forças do pinch roll LO e LA |

Códigos de alarme (AAKK): AA é o bit da área, KK é o tipo.

- 01 e 02: valor abaixo ou acima do limite de alarme.
- 11 e 12: valor abaixo ou acima da faixa normal (aviso).
- 50: entrada digital de falha. 60: parada por material (cobble). 61: parada operacional. 70: manutenção requerida.
- Exemplos nesta máquina: queda de pressão do mandril (AI009) gera 0101; mancal do wrapper quente (AI006) gera 0202; assimetria do pinch acima do limite (AI004) gera 0702.

Dicas de leitura:

- Compare AI002 e AI003. A diferença entre as duas é o primeiro indício de pinch assimétrico.
- Se AI004 sobe e AI010 sobe depois, a causa provável é o pinch. Se AI009 cai e a bobina ovaliza, a causa provável é o mandril.
- AI007 e AI008 são valores da última bobina. Servem para datar o início do problema, não para alarme.

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Bobina telescopada (borda deslocada) | QUALIDADE (bit 9) / AI010; POSICAO_GEOMETRIA / AI004 | Pinch assimétrico: gap diferente entre LO e LA | Comparar AI004 por turno; comparar AI002 e AI003; medir gap com a máquina parada | Ajustar o gap do pinch roll; checar cilindros e drift de pressão |
| Telescopia com guia lateral aberta ou tira fora de largura | AI010 | Gap entre tira e guia maior que a largura; variação de largura | Conferir ajuste da guia e a largura da tira | Fechar a guia; informar o laminador sobre a largura |
| Bobina frouxa nas voltas internas | FORCA_CARGA (bit 14) / AI001 | Tensão baixa na cabeça e cauda | Ver AI001 no início e fim da tira | Ajustar tensão; revisar o modelo de bobinamento |
| Bobina ovalizada / voltas internas soltas | HIDRAULICA (bit 1) / AI009 | Falha do mandril: bypass no selo do pistão, vazamento, colapso parcial sob o peso | Teste de vazamento do mandril; observar queda de AI009 durante a bobina | Testar vazamento do mandril; trocar selo; programar parada |
| Pressão de expansão baixa (alarme 0101) | HIDRAULICA / AI009 | Vazamento externo, selo gasto, bomba ou válvula fora de ajuste, acumulador descarregado | Nível e temperatura do óleo, filtros, pressão da HPU, vazamento visível | Corrigir a HPU; isolar o cilindro; parar para vedação |
| Marcas de wrapper na tira (padrão de passo) | POSICAO_GEOMETRIA (bit 7) / AI005 | Pico de força no degrau; step control mal ajustado | Ver AI005 por bobina; olhar marcas na cabeça da bobina | Revisar o step control dos wrapper rolls; checar posição e resposta dos cilindros |
| Mancal do wrapper quente (aviso acima de 62,5 °C de referência; alarme 0202 acima de 85 °C) | LUBRIFICACAO (bit 2) / AI006 | Falta de lubrificante, linha entupida, desalinhamento, carga lateral por gap mal ajustado | Tendência de AI006 por bobina; fluxo de lubrificante; mecanismo de ajuste de gap | Inspecionar a lubrificação; corrigir alinhamento; trocar mancal se necessário |
| Falha de threading: a cabeça não entra no mandril | MATERIAL_FLUXO (bit 12); código 60 | Calha desgastada, guia mal centrada, pinch fechando tarde, cabeça levantada ou arqueada, segmento do mandril alto ou baixo | Conferir sequência da cabeça; folga da calha; posição dos segmentos | Corrigir a causa; limpar a mesa; reiniciar o ciclo |
| Cobble na entrada da bobinadeira | MATERIAL_FLUXO / código 60 | Cabeça não capturada; wrapper fechando fora do tempo | Câmera, registro de tempos da sequência | Limpar a sucata; revisar o tempo de captura; verificar o pinch |
| Alternância falha (bobinadeira seguinte não pronta) | MATERIAL_FLUXO | Descarga lenta, carro de bobinas fora de posição, mandril não expandido | Estados da BOB-01 e da BOB-02; tempo do ciclo de descarga | Acelerar a descarga; corrigir o carro; intertravar a sequência |
| Carro de bobinas lento ou desalinhado | POSICAO_GEOMETRIA / MATERIAL_FLUXO | Cilindro de elevação com vazamento, trilho sujo, sensor de posição | Inspeção visual, teste de posição | Reparar cilindro; limpar trilho; calibrar sensor |
| Forças do pinch diferentes entre lados | FORCA_CARGA / AI002 e AI003 | Cilindro com vazamento ou válvula descalibrada | Diferença AI002 − AI003; drift de pressão com a linha parada | Ajustar o gap; reparar o cilindro ou a válvula |

Observações de campo (fonte técnica):

- Um selo de pistão com vazamento lento pode colapsar parcialmente o mandril sob o peso da bobina. O defeito só aparece depois de a bobina ser descarregada.
- Um mecanismo de gap desalinhado em um wrapper gerou falhas repetidas de mancal sempre na mesma posição.
- Deriva LO/LA do pinch acima de 0,5 mm produziu bobinas telescopadas em um caso relatado.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

- **Bobina telescopada.** Bordas expostas e danificadas; risco de dano no transporte e no armazém. Pode virar sucata de borda ou reprovação por cliente.
- **Marcas de wrapper.** Marcas repetidas no corpo da bobina. Aparecem como defeito de superfície em decapagem e laminação a frio.
- **Ovalização.** A bobina ovalizada é difícil de pegar no mandril da linha seguinte (decapagem). Pode travar o desbobinamento.
- **Cobble na entrada.** Segundo o manual da planta, a tira bloqueia a saída e pode parar a linha por cerca de 4 h.
- **Tensão incorreta.** Tensão baixa gera bobina frouxa e riscos por atrito entre camadas. Tensão alta marca as voltas internas.
- **A montante.** Tensão e pinch instáveis podem puxar a tira no laminador acabador e afetar a espessura da cabeça e da cauda.
- **Alternância.** Atraso da bobinadeira seguinte obriga reduzir o ritmo do laminador.
- **Metalurgia.** A temperatura de bobinamento (CT) vem da mesa de resfriamento. A bobinadeira deve estar pronta para aços de alta resistência, que exigem mais força e maior tensão.

## 8. Manutenção preventiva e preditiva

Periodicidade usada na simulação, mais referências de mercado:

| Item | Periodicidade | Inspeção ou ação |
|---|---|---|
| Mancais do wrapper e pressão do pinch | A cada bobina | Registrar AI006 e as forças; alertar em tendência de alta em 10 bobinas seguidas |
| Gap do pinch (LO e LA) | A cada turno | Registrar os dois lados; alerta automático de assimetria |
| Vazamento do mandril (bypass do cilindro de expansão) | Trimestral | Teste de vazamento do selo do pistão; checar chavetas cônicas |
| Retífica de pinch e wrapper rolls | A cada 2–4 semanas | Retificar, medir trincas e desgaste |
| Segmentos do mandril | Por contagem de bobinas | Medir a folga com o mandril totalmente expandido; muitas usinas trocam o segmento com cerca de 2 mm de desgaste na sede |
| Mecanismo de gap dos wrapper rolls | Por parada programada | Verificar função, alinhamento e carga lateral |
| Redutor do mandril | Por condição | Análise de partículas no óleo, corrente do motor, alinhamento |
| Calha (apron) e placas curvas | Por condição | Medir desgaste; trocar no reparo |
| HPU | Por condição | Filtros, nível, temperatura, qualidade do óleo, acumuladores |
| Carro de bobinas | Mensal sugerido | Cilindros, trilhos, sensores de posição |

Preditiva:

- Tendência por bobina de AI004, AI005, AI006 e AI009.
- Correlação entre AI010 e AI004.
- Fontes de mercado relatam que bobinadeiras trocam mancais com mais frequência que o resto do laminador, pelo ciclo de carga.
- Falhas de bobinadeira ocorrem muitas vezes no momento da captura da tira. Reserve atenção ao ciclo de threading.
- Fabricantes oferecem monitoramento da área da bobinadeira por software.

## 9. Segurança

- **LOTO.** Bloquear energia elétrica, hidráulica e pneumática antes de qualquer intervenção. Aliviar a pressão do acumulador e despressurizar o circuito do mandril.
- **Energia armazenada.** Segmentos do mandril, cilindros e wrapper rolls podem se mover com a pressão residual. Calçar ou travar mecanicamente.
- **Peso.** Bobina de até 35 t no mandril ou no carro. Nunca entrar sob bobina suspensa.
- **Pontos de esmagamento.** Pinch roll, wrapper rolls, carro de bobinas e calha.
- **Tira quente.** A cabeça pode sair em arco em cobble. Manter distância e guardas na área de threading.
- **Óleo hidráulico.** Vazamento sob pressão pode perfurar a pele e iniciar incêndio perto de tira quente. Usar fluido resistente a fogo conforme o projeto.
- **Superfícies quentes.** Mandril e mancais ficam quentes. Aguardar o resfriamento.
- **Espaço confinado.** Tratar fossos e áreas sob o carro de bobinas conforme a norma da planta.
- **Cobble.** Só entrar na área após a confirmação da parada e do bloqueio. A remoção de sucata é tarefa com permissão de trabalho.

## 10. Perguntas frequentes do operador

1. **Por que a bobina saiu telescopada?**
   O mais comum é o pinch roll assimétrico. Compare as forças dos dois lados e o gap. Ajuste o gap do pinch.

2. **A pressão do mandril caiu. O que faço?**
   Abaixo de 90 bar é alarme. Veja vazamento visível e o nível do óleo. Se a bobina ovalizar, programe o teste de vazamento e a troca do selo.

3. **O mancal do wrapper passou de 85 graus. É grave?**
   É alarme. Verifique a lubrificação e a tendência das últimas bobinas. Se continuar subindo, pare para inspeção.

4. **O que causa marca de wrapper?**
   Pico de força no degrau. O erro de posição do wrapper acima de 3 mm indica o problema. Revise o step control.

5. **A cabeça não entrou no mandril. E agora?**
   Confirme que o laminador está parado ou segurando. Cheque guias, calha e pinch. Depois de limpar a sucata, reinicie a sequência.

6. **Quanto tempo para uma retífica de pinch e wrapper?**
   A planta usa de 2 a 4 semanas entre retíficas. A retífica em si exige parada programada.

7. **Por que a outra bobinadeira não assumiu?**
   Veja o estado da bobina anterior, o carro de bobinas e se o mandril voltou expandido. Corrija e libere a sequência.

8. **Tensão de bobinamento fora do ideal, é problema?**
   O ideal é 110 kN, e o normal vai de 20 a 200 kN. Fora disso, a bobina pode soltar ou marcar. Avise a automação.

## Fontes

- [SMS group — novo conceito de downcoiler de fácil manutenção](https://sms-group.com/insights/all-insights/new-easy-to-maintain-concept-for-downcoilers)
- [Oxmaint — Coiler & Tension Reel Maintenance for Hot Strip Mill Steel](https://oxmaint.com/industries/steel-plant/coiler-tension-reel-maintenance-hot-strip-mill-steel)
- [Oxmaint — Hot Strip Mill Maintenance: Stands, Rolls & Coiler Management](https://oxmaint.com/industries/steel-plant/hot-strip-mill-maintenance-stands-rolls)
- [Danieli — Powerful Downcoiler](https://www.danieli.com/en/products/technological-packages/powerful-downcoiler_29_69.htm)
- [Danieli — HS-Coiling](https://www.danieli.com/en/products/technological-packages/hs-coiling_29_70.htm)
- [Patente US 6648264 — Method and apparatus for coiling a metal strip](https://patents.google.com/patent/US6648264)
- [Patente US 6588245 — Roll gap control for coiler](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6588245)
- [Patente JP3459957B2 — Wrapper roll control method](https://patents.google.com/patent/JP3459957B2/en)
- [Patente US 6810706 — Apparatus for reducing tension variations in a metal strip](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6810706)
- [Patente US 3763684 — Downcoiler mandrel of the toggle link type](https://patents.google.com/patent/US3763684A/en)
- [SMS group — reparo de emergência de mandril de downcoiler](https://sms-group.com/insights/news/news-detail/emergency-repair-of-downcoiler-mandrel-in-record-time)

Nota: valores de fontes comerciais (Oxmaint) são indicativos e não foram validados contra norma de engenharia.
