# FRN-01 — Forno de reaquecimento 1 (viga caminhante) — documentação de referência

> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

- O forno de reaquecimento é o primeiro equipamento da Linha 1 (Reaquecimento). Ele recebe placas de lingotamento contínuo, frias ou mornas, e as entrega aquecidas ao descarepador e ao laminador de desbaste (R1).
- Objetivo: levar a placa inteira (superfície e núcleo) a cerca de 1.200–1.260 °C, com perfil de temperatura uniforme, para que ela seja deformável nas cadeiras seguintes.
- Na Usina exemplo, o forno é de viga caminhante (*walking beam*), com capacidade de 350–400 t/h e 5 zonas (8 malhas de controle topo/fundo).
- A temperatura de desenfornamento (AI007) tem alvo de 1.220 °C, definido pelo modelo de nível 2.
- O forno também é o maior consumidor de energia térmica da linha. Cada ponto de eficiência aparece direto no consumo específico de gás (AI014, GJ/t).
- Ele define o ritmo da usina: o ritmo de desenfornamento (AI016) é o ritmo de alimentação do laminador.
- Fabricantes de referência de mercado: Tenova, Fives Stein, Danieli Centro Combustion, Andritz/Maerz.

## 2. Princípio de funcionamento

**Transporte da placa**
- As placas ficam sobre vigas fixas (skids) refrigeradas a água. Um conjunto de vigas móveis faz um ciclo retangular: sobe, avança, desce e recua.
- Na subida, as placas saem das vigas fixas e ficam apoiadas nas móveis. Cada passo desloca a placa um pitch, e as faces de apoio se alternam.
- O acionamento é hidráulico (AI019, pressão hidráulica da viga caminhante). A frequência de passos regula o tempo de residência (AI015).
- Como a placa é levantada a cada passo, as marcas de apoio (skid marks) são menores do que num forno de empurrador. Mesmo assim ainda existem e exigem encharque.

**Transferência de calor**
- A placa recebe calor sobretudo por radiação das paredes, da abóbada e dos gases quentes. Parte vem por convecção.
- O núcleo é aquecido por condução. Placas grossas (250 mm) precisam de tempo: a Usina exemplo trabalha com cerca de 195 min (placa fria).
- O forno segue um perfil por zonas, a favor do fluxo de placas:
  1. **Pré-aquecimento** (aproveita os fumos, queima pouco ou nada): AI001.
  2. **Aquecimento 1 e 2**, com malhas de topo e de fundo: AI002 a AI005. É onde entra a maior potência.
  3. **Encharque**: AI006. Reduz o gradiente entre superfície e núcleo e apaga as marcas dos skids.
- Pelo caminho dos gases, os fumos saem pelo lado da carga fria e passam por um recuperador (trocador de calor) que pré-aquece o ar de combustão. A temperatura dos fumos após o recuperador é AI013.

**Combustão**
- Combustível: gás misto de coqueria e alto-forno (COG + BFG), com gás natural de reforço quando o poder calorífico cai.
- A relação ar/gás é controlada por malhas de cascata: a temperatura da zona comanda a vazão de gás, e o ar acompanha em proporção.
- O oxigênio residual dos fumos (AI011) faz o ajuste fino (trim). A pressão do forno (AI010) é mantida levemente positiva por damper de tiragem, para evitar entrada de ar falso.
- Queimadores regenerativos (pares que alternam entre queima e exaustão) pré-aquecem o ar a temperaturas muito altas e reduzem o consumo. A pesquisa pública mostra o ganho típico de 15% ou mais em relação a queimadores convencionais, mas exigem controle fino do excesso de ar. Queimadores recuperativos, com trocador separado, são mais simples e dominam em fornos de grande porte para gases pobres.
- O nível 2 calcula o perfil térmico da placa, prevê a temperatura de desenfornamento e ajusta os setpoints das zonas. O desvio entre o previsto e o medido é AI008.

**Carepa e atmosfera**
- A carepa (óxido de ferro) cresce rápido acima de ~900 °C. Depende da temperatura, do tempo e do oxigênio e vapor d'água na atmosfera.
- Estudos públicos mostram que reduzir o excesso de ar diminui bastante a perda de aço por oxidação. Mas falta de ar gera CO e queima incompleta.

## 3. Componentes principais

| Componente | Função |
|---|---|
| Carcaça e refratário (paredes, abóbada, soleira) | Contém o calor. Concreto ou tijolo refratário e fibra cerâmica. A degradação aumenta perda e gera pontos frios |
| Vigas fixas e móveis (skids) com água | Tubos refrigerados e revestidos de isolamento refratário |
| Hot riders (botões de apoio) | Peças de liga sobre as vigas, em contato com a placa. Gastam e geram skid marks |
| Sistema hidráulico da viga caminhante | Cilindros, bomba e acumuladores para o ciclo de levantar e avançar |
| Queimadores de topo, fundo e laterais | Por zona. Com piloto, detector de chama e válvulas de bloqueio |
| Sistema de gás misto (COG, BFG, GN) | Misturador, válvulas de controle e válvulas de segurança |
| Ventilador de ar e recuperador | Ar de combustão e pré-aquecimento com os fumos |
| Chaminé e damper de tiragem | Controla a pressão do forno (AI010) |
| Termopares e pirômetros por zona | Base das malhas de temperatura |
| Analisadores de O₂ e CO | Nos fumos: AI011 e AI012 |
| Máquinas de carga e descarga, balança e pirômetro de saída | Entrada e saída das placas |
| Circuito de água de refrigeração dos skids | Bombas, trocador e instrumentos: AI017, AI018 |
| Nível 2 (modelo térmico) | Previsão da temperatura da placa e setpoints |

## 4. Parâmetros típicos de operação

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| T zona pré-aquecimento queimado | 1.000–1.150 °C | ideal 1.120; normal 1.000–1.200; alarme 1.095 / 1.145 °C | AI001 |
| T zona aquecimento 1 (topo) | 1.200–1.300 °C | ideal 1.280; normal 1.200–1.320; alarme 1.255 / 1.305 °C | AI002 |
| T zona aquecimento 1 (fundo) | 1.200–1.300 °C | ideal 1.280; normal 1.200–1.320; alarme 1.255 / 1.305 °C | AI003 |
| T zona aquecimento 2 (topo) | 1.200–1.320 °C | ideal 1.280; normal 1.200–1.320; alarme 1.255 / 1.305 °C | AI004 |
| T zona aquecimento 2 (fundo) | 1.200–1.320 °C | ideal 1.280; normal 1.200–1.320; alarme 1.255 / 1.305 °C | AI005 |
| T zona de encharque | 1.220–1.280 °C | ideal 1.255; normal 1.220–1.290; alarme 1.230 / 1.280 °C | AI006 |
| T de desenfornamento da placa | 1.150–1.280 °C (depende do aço e do R1) | ideal 1.220; normal 1.180–1.260 °C; sem limite de alarme | AI007 |
| Desvio do modelo nível 2 | poucos °C a ~15 °C | ideal 0; normal 0–10; alarme acima de 20 °C | AI008 |
| ΔT de skid mark após encharque | 15–40 °C (fornos de viga caminhante) | ideal 15; normal 15–35 °C | AI009 |
| Pressão do forno | +5 a +20 Pa (levemente positiva) | ideal 10; normal 5–15; alarme 0 / 25 Pa | AI010 |
| O₂ nos fumos | 1–3 % seco (queima de gás misto) | ideal 2,0; normal 1,0–3,0; alarme 0,5 / 4,0 % | AI011 |
| CO nos fumos | abaixo de ~200 ppm | ideal 0; normal 0–200; alarme 400 ppm | AI012 |
| T dos fumos após o recuperador | 300–500 °C | ideal 375; normal 300–450 °C | AI013 |
| Consumo específico de gás | 1,0–1,6 GJ/t em fornos modernos de viga caminhante (fontes públicas citam acima de 1,0 GJ/t) | ideal 1,25; normal 1,1–1,5 GJ/t | AI014 |
| Tempo de residência (placa fria 250 mm) | 150–240 min | ideal 195; normal 150–240 min | AI015 |
| Ritmo de desenfornamento | 12–20 placas/h para ~350–400 t/h | ideal 16; normal 12–20 placas/h | AI016 |
| Água dos skids: T de entrada | 30–40 °C | ideal 35; normal 30–40 °C | AI017 |
| Água dos skids: ΔT | 8–15 °C | ideal 11,5; normal 8–15; alarme 18 °C | AI018 |
| Pressão hidráulica da viga caminhante | 120–200 bar | ideal 150; normal 120–180 bar | AI019 |
| Queimadores em trip | 0 | ideal 0; alarme em 0,5 (qualquer trip) | DI01 |

Observações:
- Faixas da indústria são ordens de grandeza de fontes públicas e variam com o aço, a espessura e o fabricante.
- O consumo de gás tem grande dispersão. Um caso público (substituição de empurradores por viga caminhante) mostrou queda de 19,5% de gás no primeiro trimestre, com meta de 30%.
- O ΔT de skid mark e a faixa de O₂ da simulação são compatíveis com a prática. A sugestão da indústria para O₂ é a menor possível sem gerar CO.

## 5. Instrumentação e sinais do CLP

O CLP do forno é o CLP-FRN-01. Ele liga bits de área nas palavras de falha e aviso e registra alarmes (código AAKK, em que AA é o bit da área).

| Área (bit) | Tags | O que indica |
|---|---|---|
| TERMICA (4) | AI001–AI006, AI007, AI009 | Temperatura de zonas, da placa na saída e marca de skid |
| INSTRUMENTACAO (8) | AI008 | Desvio do modelo nível 2 contra a medição |
| COMBUSTAO (5) | AI010–AI014, DI01 | Pressão do forno, O₂, CO, fumos, consumo e trip de queimador |
| MATERIAL_FLUXO (12) | AI015, AI016 | Tempo de residência e ritmo de desenfornamento |
| AGUA (3) | AI017, AI018 | Água de refrigeração dos skids |
| HIDRAULICA (1) | AI019 | Pressão do sistema hidráulico da viga caminhante |

Como ler os códigos:
- 0402 = zona de temperatura acima do alarme; 0401 = abaixo do alarme (bit 4, TERMICA).
- 0502 = acima do alarme na combustão (por exemplo, O₂ ou pressão); 0501 = abaixo (por exemplo, O₂ baixo ou pressão baixa).
- 0550 = DI01 ativo, ou seja, queimador em trip ou falha de chama.
- 0302 = ΔT da água dos skids acima de 18 °C (AGUA, bit 3).
- 0802 = desvio do modelo acima de 20 °C.
- Avisos (tipo 11 e 12) indicam valor fora da faixa normal, sem chegar ao alarme.

Observações de instrumentação:
- Termopares derivam com o envelhecimento, e a carepa pode cobrir o pirômetro de saída. Por isso o desvio do nível 2 (AI008) é o primeiro indício de sensor ruim.
- O analisador de O₂ não detecta CO ou hidrocarbonetos não queimados. O O₂ e o CO (AI011 e AI012) devem ser lidos juntos.
- Fontes públicas lembram que o excesso de ar real muda com obstrução do regenerador e vazamento de ar para os fumos. O analisador sozinho pode enganar.
- Na simulação, AI007 e AI009 não têm limite de alarme. Eles geram avisos via faixa normal e entram no diagnóstico da área TERMICA.

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Zona abaixo do setpoint | TERMICA: AI001–AI006 | Queimador em trip, ritmo alto ou variação do poder calorífico do gás misto | DI01, vazão de gás, poder calorífico (COG/BFG), ritmo AI016 | Rearmar queimador, corrigir mistura ou reforçar com GN; segurar placas no forno (mais residência) |
| Zona acima do setpoint | TERMICA: AI001–AI006 | Compensação de outra zona ou malha de controle com problema | Malha da zona, distribuição de carga entre zonas, termopar | Ajustar a malha e a distribuição de carga |
| Placa saindo fria | TERMICA: AI007 (e AI008) | Ritmo alto, trip de queimador ou residência curta | AI015, AI016, DI01, termopares e modelo nível 2 | Aumentar residência ou reduzir ritmo; validar termopares |
| Skid mark acentuada | TERMICA: AI009 | Isolamento do skid danificado ou hot riders gastos | Inspeção dos skids na parada; tempo de encharque | Programar reparo; aumentar tempo de encharque |
| Desvio do modelo acima de 20 °C | INSTRUMENTACAO: AI008 | Termopar com deriva, pirômetro sujo ou modelo desajustado | Comparar com pirômetro e data logger | Calibrar ou trocar o sensor; reajustar o modelo |
| Pressão do forno fora da faixa | COMBUSTAO: AI010 | Damper de tiragem ou controle de pressão | Posição do damper e malha de pressão | Corrigir damper e malha. Pressão baixa puxa ar falso; alta vaza chama pelas portas |
| Combustão fora da relação ar/gás (O₂ baixo, CO alto) | COMBUSTAO: AI011, AI012 | Falta de ar, queimador sujo ou analisador de CO com problema | Curva ar/gás, analisador de CO, estado dos queimadores | Ajustar a relação ar/gás; conferir o analisador |
| Excesso de ar (O₂ alto) | COMBUSTAO: AI011 | Deriva do analisador de O₂ ou ar sem chama (queimador em trip) | Calibração com gás padrão, DI01 | Calibrar o analisador e corrigir a relação ar/gás. Sobe o GJ/t e a carepa |
| Consumo específico de gás alto | COMBUSTAO: AI013, AI014 | Excesso de ar, zona compensando queimador em trip ou placa fria; recuperador sujo | O₂, DI01, T dos fumos | Corrigir O₂, rearmar o queimador, limpar o recuperador |
| Queimador em trip / falha de chama | COMBUSTAO: DI01 (código 0550) | Detector de chama, válvula, falta de gás ou ar | Detector de chama, pressões de gás e ar, intertravamento | Verificar e rearmar com segurança; reduzir o ritmo até a zona voltar ao setpoint |
| ΔT da água dos skids alto, ou T de entrada alta | AGUA: AI017, AI018 | Bomba, vazão baixa ou entupimento do circuito | Vazão, pressão da bomba, filtros e trocador | Verificar bomba e vazão na hora. Risco de parada de emergência |
| Viga caminhante lenta ou travada | HIDRAULICA: AI019 | Pressão baixa, vazamento ou bomba hidráulica | Nível do óleo, filtros, cilindros, pressão do acumulador | Corrigir antes de perder o ciclo da viga |
| Placas esperando, ritmo caindo | MATERIAL_FLUXO: AI015, AI016 | Parada a jusante ou problema de carga | Estado do R1, da mesa e do descarregador | Ajustar carga e manter as zonas em modo de espera |

Observação: o manual gerado não lista causas para as áreas MATERIAL_FLUXO e HIDRAULICA. A leitura acima é de referência.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

- **Placa fria:** a força e o torque do R1 sobem de 15% a 25%. A temperatura final de acabamento (FDT) fica baixa e há risco de cobble.
- **Skid mark:** a região fria da placa gera variação de espessura e de força no acabador. A marca pode virar defeito de perfil e de planicidade na tira.
- **Gradiente superfície/núcleo:** placa mal encharcada deforma de modo desigual e causa camber e variação de largura.
- **Excesso de ar e carepa:** mais perda de aço por oxidação (rendimento metálico). A carepa grossa ou mal descamada deixa defeitos de superfície. Estudos públicos reportam até 35% menos perda por carepa ao baixar o excesso de ar de 70% para 20%.
- **Superaquecimento:** acima do alvo, aumenta o consumo, a carepa e o risco de crescimento de grão e de placa queimada.
- **Falha da água dos skids:** pode exigir parada de emergência da viga e do forno. Ela danifica o skid e o refratário.
- **Ritmo:** se o forno não segue o laminador, a linha para (Suspended). Se segura placas demais, o consumo sobe.
- Tudo isso aparece, na ordem do fluxo, em: temperatura de saída (AI007), descarepador, R1, FDT e planicidade.

## 8. Manutenção preventiva e preditiva

| Item | Periodicidade típica | Inspeção / ação |
|---|---|---|
| Queimadores e detectores de chama | Por turno | Verificar chama, trips e rearmes |
| Analisadores de O₂ e CO | Por turno | Verificar leitura e deriva; calibrar com gás padrão conforme o procedimento |
| Termografia da carcaça | Semanal | Pontos quentes que indicam refratário danificado |
| Curvas ar/gás | Mensal | Conferir relação e linearidade das válvulas |
| Termopares | Mensal | Comparar com padrão; trocar os com deriva |
| Sistema hidráulico da viga | Mensal | Óleo, filtros, vazamentos, pressão |
| Água dos skids | Mensal | Filtros, bombas e ΔT (AI018) |
| Skids, hot riders e isolamento | Nas paradas | Medir desgaste e trocar. O isolamento fica quebradiço com o tempo |
| Refratário (abóbada, paredes, soleira) | Nas paradas | Reparar trincas, blocos e fibra |
| Recuperador / regeneradores | Nas paradas | Limpeza, vazamentos e obstrução |
| Data logger e modelo nível 2 | Nas paradas | Validar o modelo com a placa instrumentada |

Preditiva:
- Acompanhar tendência de AI008 (desvio do modelo), AI009 (skid mark), AI013 (fumos) e AI014 (GJ/t). A alta lenta de qualquer um indica sujeira, desgaste ou deriva.
- Monitorar o ΔT da água dos skids (AI018): subida gradual sugere incrustação.

## 9. Segurança

- **LOTO:** bloquear e etiquetar energia elétrica, hidráulica (e despressurizar acumuladores), gás (válvulas de bloqueio duplo com sangria), ar e água antes de qualquer intervenção.
- **Gás misto:** o COG e o BFG são tóxicos (CO) e inflamáveis. O BFG tem muito CO e é inodoro. Usar detector de CO portátil e ventilar antes de entrar.
- **Explosão no forno:** nunca reacender em forno frio com atmosfera desconhecida. Seguir purga e sequência de partida com teste de estanqueidade. Trip de queimador exige purga antes de nova tentativa, conforme o intertravamento.
- **Espaço confinado:** entrada no forno só com permissão, vigia, medição de gases e resfriamento prévio.
- **Altas temperaturas e radiação:** acima de 1.200 °C. Usar EPI adequado. Cuidado com chama pelas portas se a pressão (AI010) subir.
- **Água:** vazamento de água do skid dentro do forno gera vapor e risco de explosão e dano ao refratário.
- **Hidráulica:** óleo sob alta pressão (até ~180 bar). Risco de injeção e de movimento inesperado da viga.
- **Placa presa ou caída:** nunca entrar sem bloquear a viga caminhante e as máquinas de carga.

## 10. Perguntas frequentes do operador

1. **Por que a placa está saindo fria?** Ritmo alto, queimador em trip ou pouco tempo no forno. Reduza o ritmo e confira o DI01.
2. **O que faz o O₂ subir?** Ar demais, em geral por deriva do analisador ou queimador apagado soprando ar. Calibre e corrija a relação ar/gás.
3. **E se o CO subir?** Falta de ar ou queima ruim. Confira o analisador de CO e a curva ar/gás.
4. **Por que o consumo de gás aumentou?** Excesso de ar, zona compensando um trip ou recuperador sujo. Veja o O₂ e a temperatura dos fumos.
5. **O que é skid mark?** É a marca fria que fica onde a placa apoia nas vigas refrigeradas. Mais encharque ajuda; se piorar, inspecione o isolamento e os hot riders.
6. **A água dos skids esquentou demais. E agora?** Verifique bomba e vazão de imediato. Se não normalizar, o forno pode parar por emergência.
7. **A pressão do forno saiu da faixa. O que olho?** O damper de tiragem e a malha de pressão. Pressão baixa puxa ar falso; alta empurra chama para fora.
8. **O desvio do modelo ficou alto. Posso confiar no forno?** Não totalmente. Confira termopares e pirômetro; o nível 2 pode estar errado.

## Fontes

- [Tenova — Walking Beam Furnace for Slabs](https://tenova.com/technologies/walking-beam-furnace-slabs): visão geral de fornos de viga caminhante de mercado, queimadores para gases de baixo poder calorífico.
- [Cleveland-Cliffs — Heating Steel with State-of-the-Art, Energy-Efficient Furnaces (DOE Better Buildings)](https://betterbuildingssolutioncenter.energy.gov/showcase-projects/cleveland-cliffs-heating-steel-state-art-energy-efficient-furnaces/printpdf): caso de substituição de fornos de empurrador por viga caminhante e redução do consumo de gás.
- [Fives — SSAB seleciona a Fives para atualizar o controle de fornos (Steel Times)](https://www.steeltimesint.com/news/fives-digital-technology-to-upgrade-ssabs-furnace-control): controle de nível 2 e otimizador térmico em fornos de reaquecimento.
- [Projeto CORDIS EE.-00100-86](https://cordis.europa.eu/project/id/EE.-00100-86): demonstração de queimadores regenerativos cerâmicos em forno de viga caminhante.
- [Tese da McGill sobre formação de carepa em fornos de reaquecimento](https://escholarship.mcgill.ca/downloads/6m311q38b): sensibilidade da carepa ao oxigênio, tempo e temperatura.
- [Patente US 4936771 — Skid mark erasure system](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4936771): origem das marcas dos skids e do encharque.
- [Patente US 5897310 — Furnace rider bar assembly](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5897310): hot riders, isolamento e desgaste.
- [Patente US 8845324 — Device for controlling regenerative burners](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8845324): princípio dos queimadores regenerativos e válvulas.
- [Patente US 5938423 — Controlling combustion using an oxygen sensor](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5938423): controle da relação ar/combustível por sensor de O₂.
