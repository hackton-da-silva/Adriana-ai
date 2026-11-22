# FRN-02 — Forno de reaquecimento 2 (viga caminhante) — documentação de referência

> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

- O forno aquece placas frias (250 mm na simulação) até cerca de 1.220 °C.
- Ele fica entre o pátio de placas e o desbaste (R1) da linha 1.
- A placa precisa sair quente e uniforme. Isso permite deformar o aço com força baixa.
- Na indústria, a temperatura de desenfornamento varia de 900 a 1.300 °C, conforme o aço e a espessura.
- O alvo de cada placa vem do modelo de nível 2, que parte da temperatura de acabamento (FDT) desejada.
- O forno também dá o ritmo da linha: placas/h desenfornadas.
- Na Usina exemplo: 350–400 t/h, 16 placas/h, residência ideal de 195 min.
- Fabricantes de referência de mercado: Tenova, Fives Stein, Danieli Centro Combustion, Andritz/Maerz.

## 2. Princípio de funcionamento

**Transporte.**
- A viga caminhante tem vigas fixas e vigas móveis.
- Um ciclo tem quatro movimentos: subir, avançar, descer e recuar.
- Ao subir, as vigas móveis levantam as placas das fixas. Ao avançar, levam-nas um passo. Ao descer, depositam-nas. Ao recuar, voltam.
- Cilindros hidráulicos sob a câmara fazem o movimento.
- Cada placa passa a descansar em pontos diferentes a cada passo. Isso é melhor que o forno de empurrar, que arrasta a placa sobre o skid.
- O ritmo é controlado pelo tempo de ciclo da viga.

**Aquecimento.**
- O calor vem da radiação das chamas, dos gases e das paredes de refratário.
- A placa avança contra o fluxo dos fumos, que seguem para o recuperador.
- Zonas típicas, da carga à saída: pré-aquecimento (não queimado ou com poucos queimadores), aquecimento 1, aquecimento 2 e encharque.
- As zonas de aquecimento têm malhas de topo e de fundo. A Usina exemplo tem 5 zonas e 8 malhas.
- No pré-aquecimento a placa ganha calor sensível dos fumos que saem.
- Nas zonas de aquecimento entra a maior potência. O gás é queimado com ar pré-aquecido.
- No encharque a potência é baixa. A temperatura se equaliza do núcleo à superfície, e a placa sai uniforme.

**Combustível e controle.**
- Usa-se gás misto: COG (gás de coqueria) e BFG (gás de alto-forno), com gás natural (GN) de reforço.
- O poder calorífico do gás misto varia. O controle compensa a vazão pelo Wobbe ou pelo poder calorífico.
- Cada zona tem um termopar, um controlador e uma relação ar/gás.
- O ar de combustão vem de ventiladores. Parte do ar é pré-aquecida no recuperador com o calor dos fumos.
- A pressão do forno é mantida levemente positiva (cerca de 10 Pa). O damper de fumos regula essa pressão.
- Pressão negativa suga ar falso. Pressão alta empurra chama e calor para fora pelas portas.
- O nível 2 calcula a temperatura da placa em tempo real e ajusta os setpoints das zonas.

**Skid marks.**
- A placa apoia em skids refrigerados a água. Nesses pontos ela perde calor por condução.
- O resultado é uma marca fria na face de baixo, chamada skid mark.
- Tubos isolados com refratário e botões ou hot riders reduzem o efeito. O encharque apaga parte da marca.
- Mais tempo no mesmo apoio e isolamento ruim aumentam a marca.

## 3. Componentes principais

| Componente | Função |
|---|---|
| Carcaça e refratário (abóbada, paredes, soleira) | Contêm o calor. Concreto refratário e fibra cerâmica. |
| Queimadores (topo, fundo, laterais) | Queimam o gás misto com ar. Têm piloto e detector de chama. |
| Detector de chama (UV ou IR) | Confirma a chama. Sem chama, a válvula de bloqueio fecha. |
| Sistema de segurança de queimadores (BMS) | Sequencia partida e parada, faz purga e supervisiona chama. |
| Ventiladores de ar de combustão | Fornecem ar aos queimadores. Pressostato ou fluxostato prova o ar. |
| Recuperador (trocador de calor) | Pré-aquece o ar com os fumos (fumos a 300–450 °C na saída). |
| Damper e chaminé | Controlam a pressão do forno e a saída de fumos. |
| Analisadores de O₂ e CO | Verificam a qualidade da combustão. |
| Viga caminhante (fixa e móvel) | Transporta as placas. Tubos refrigerados a água. |
| Skids, botões e hot riders | Apoio da placa. Os riders gastam e são trocados. |
| Isolamento dos tubos refrigerados | Reduz a perda de calor para a água e a skid mark. |
| Cilindros e central hidráulica | Movimentam a viga. Têm acumuladores e válvulas servo ou proporcionais. |
| Circuito de água dos skids | Bombas, trocador e tubulações. Retira calor dos tubos. |
| Termopares e pirômetros | Medem zonas e placa. Alimentam o nível 2. |
| Máquinas de enfornar e desenfornar | Carregam e retiram as placas. Dão o ritmo. |
| Modelo de nível 2 | Prevê a temperatura da placa e calcula os setpoints. |

## 4. Parâmetros típicos de operação

Faixas da indústria são ordens de grandeza de fontes públicas. Elas variam com o aço, a espessura e o projeto do forno.

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| T zona pré-aquecimento | 900–1.150 °C | ideal 1.120; normal 1.000–1.200; alarme 1.095 / 1.145 °C | AI001 |
| T aquecimento 1 topo | 1.200–1.350 °C | ideal 1.280; normal 1.200–1.320; alarme 1.255 / 1.305 °C | AI002 |
| T aquecimento 1 fundo | 1.200–1.350 °C | ideal 1.280; normal 1.200–1.320; alarme 1.255 / 1.305 °C | AI003 |
| T aquecimento 2 topo | 1.200–1.350 °C | ideal 1.280; normal 1.200–1.320; alarme 1.255 / 1.305 °C | AI004 |
| T aquecimento 2 fundo | 1.200–1.350 °C | ideal 1.280; normal 1.200–1.320; alarme 1.255 / 1.305 °C | AI005 |
| T encharque | 1.200–1.300 °C | ideal 1.255; normal 1.220–1.290; alarme 1.230 / 1.280 °C | AI006 |
| T de desenfornamento | 900–1.300 °C (conforme o aço) | alvo nível 2: 1.220; normal 1.180–1.260 °C | AI007 |
| Desvio do modelo nível 2 | poucos °C a 10–20 °C | ideal 0; normal 0–10; alarme alto 20 °C | AI008 |
| ΔT de skid mark | 15–50 °C (varia com o projeto) | ideal 15; normal 15–35 °C | AI009 |
| Pressão do forno | levemente positiva, 5–20 Pa | ideal 10; normal 5–15; alarme 0 / 25 Pa | AI010 |
| O₂ nos fumos | 1–3 % seco | ideal 2,0; normal 1,0–3,0; alarme 0,5 / 4,0 % | AI011 |
| CO nos fumos | baixo, abaixo de poucas centenas de ppm | ideal 0; normal 0–200; alarme alto 400 ppm | AI012 |
| T dos fumos pós-recuperador | 300–500 °C | ideal 375; normal 300–450 °C | AI013 |
| Consumo específico de gás | 1,1–1,6 GJ/t (varia muito com o projeto) | ideal 1,25; normal 1,1–1,5 GJ/t | AI014 |
| Tempo de residência (placa fria 250 mm) | 2–4 h | ideal 195; normal 150–240 min | AI015 |
| Ritmo de desenfornamento | conforme a capacidade (350–400 t/h aqui) | ideal 16; normal 12–20 placas/h | AI016 |
| Água dos skids: T de entrada | 30–45 °C | ideal 35; normal 30–40 °C | AI017 |
| Água dos skids: ΔT | 8–20 °C | ideal 11,5; normal 8–15; alarme alto 18 °C | AI018 |
| Pressão hidráulica da viga | 100–200 bar | ideal 150; normal 120–180 bar | AI019 |
| Queimadores em trip | 0 | ideal 0; alarme acima de 0,5 un | DI01 |

Divergência a notar: a literatura pública não fixa um GJ/t único. Os 1,1–1,5 GJ/t da simulação são plausíveis, mas dependem de carga a quente ou fria.

## 5. Instrumentação e sinais do CLP

O CLP é o CLP-FRN-02. Ele não diagnostica: acende a lanterna e liga bits de área.

| Área (bit) | Tags | O que indica |
|---|---|---|
| TERMICA (4) | AI001–AI007, AI009 | Temperaturas das zonas, do desenfornamento e skid mark. |
| INSTRUMENTACAO (8) | AI008 | Desvio entre a temperatura medida e a prevista pelo nível 2. |
| COMBUSTAO (5) | AI010–AI014, DI01 | Pressão, O₂, CO, fumos, consumo e trip de queimador. |
| MATERIAL_FLUXO (12) | AI015, AI016 | Tempo de residência e ritmo. |
| AGUA (3) | AI017, AI018 | Água de refrigeração dos skids. |
| HIDRAULICA (1) | AI019 | Pressão hidráulica da viga caminhante. |

**Alarmes por código (AAKK).** O código é a área mais o tipo.
- 0402: temperatura de zona acima do limite de alarme (área TERMICA, bit 4).
- 0401: temperatura de zona abaixo do limite de alarme (por exemplo AI006 abaixo de 1.230 °C).
- 0501 e 0502: pressão do forno ou O₂ abaixo ou acima do alarme (COMBUSTAO, bit 5).
- 0550: DI01 ativo, queimador em trip (entrada digital de falha).
- 0302: ΔT da água dos skids acima de 18 °C (AGUA, bit 3).
- 0802: desvio do modelo nível 2 acima de 20 °C (INSTRUMENTACAO, bit 8).
- Avisos usam 11 (abaixo da faixa) e 12 (acima da faixa).

**Leitura prática.**
- Uma zona fria com DI01 em 1 aponta para queimador em trip.
- Zona fria com DI01 em 0 aponta para ritmo alto ou gás fraco.
- O₂ alto com DI01 em 1 sugere ar sem chama no queimador em trip.
- AI007 baixo junto de AI008 alto indica placa fria que o modelo não previu.
- ΔT dos skids subindo com T de entrada normal indica vazão baixa ou entupimento.
- Os limites de AI007, AI009 e AI015 a AI019 (exceto AI018) não têm alarme na simulação. Só geram aviso fora da faixa.

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Zona abaixo do setpoint | TERMICA (4); AI001–AI006 | Queimador em trip, ritmo alto ou gás com poder calorífico baixo | DI01; carga da zona; poder calorífico do gás misto | Rearmar queimador; segurar placas para dar mais residência |
| Trip de queimador ou falha de chama | COMBUSTAO (5); DI01 | Detector sujo ou fora de alinhamento, válvula, piloto, ar baixo, pressão de gás baixa | Código do trip no BMS; sinal do detector; pressão de gás e de ar | Verificar queimador e detector; rearmar; reduzir ritmo até a zona voltar |
| Vários queimadores caem juntos | COMBUSTAO (5); DI01; AI011 | Perda de ar de combustão (ventilador), queda de pressão do gás ou desbalanço do gás misto | Estado do ventilador, fluxostato, corrente do motor, pressão do gás | Religar o ventilador reserva; esperar purga; religar por etapas |
| Ventilador de ar com falha | COMBUSTAO (5); AI011, AI010 | Rolamento, desbalanceamento, damper de ar preso, inversor, acoplamento | Vibração, corrente, temperatura de mancal, posição do damper | Trocar para o reserva; programar reparo |
| O₂ alto | COMBUSTAO (5); AI011 | Deriva do analisador, ar falso (portas), ar sem chama de queimador em trip | Calibração do analisador; pressão do forno; DI01 | Calibrar; corrigir relação ar/gás; fechar entradas de ar |
| O₂ baixo ou CO alto | COMBUSTAO (5); AI011, AI012 | Falta de ar, queimador entupido, relação ar/gás fora | Curva ar/gás; fluxos de ar e gás; analisador de CO | Ajustar a relação; limpar queimador; reduzir carga |
| Pressão do forno baixa ou alta | COMBUSTAO (5); AI010 | Damper de fumos, malha de tiragem ou ventilador de exaustão | Posição do damper; sensor de pressão | Conferir damper e malha de pressão |
| Consumo específico alto | COMBUSTAO (5); AI014, AI013 | Excesso de ar, zona compensando trip, placa fria, recuperador sujo | O₂; T fumos pós-recuperador; DI01 | Corrigir O₂; rearmar queimador; limpar o recuperador |
| Placa fria no desenfornamento | TERMICA (4); AI007 | Ritmo alto, trip, residência curta, termopar com erro | AI015, AI016, DI01; termopares vs. modelo | Aumentar residência ou reduzir ritmo; validar termopares |
| Desvio do modelo nível 2 alto | INSTRUMENTACAO (8); AI008 | Termopar com deriva, emissividade, dados de carga errados, trip não informado | Comparar com pirômetro de saída e data logger | Validar sensores; corrigir dados; recalibrar o modelo |
| Skid mark acentuada | TERMICA (4); AI009 | Isolamento do skid danificado, hot riders gastos, encharque curto | Termografia e inspeção na parada; histórico de AI009 | Aumentar o encharque; programar a troca de riders e do isolamento |
| ΔT de água dos skids alto | AGUA (3); AI018, AI017 | Vazão baixa, bomba degradada, entupimento ou incrustação | Vazão, pressão e corrente da bomba; filtros | Verificar bomba e vazão imediatamente; risco de parada de emergência |
| Pressão hidráulica da viga fora da faixa | HIDRAULICA (1); AI019 | Bomba com desgaste, acumulador sem pré-carga, vazamento, filtro saturado | Pré-carga do acumulador, filtros, temperatura do óleo | Corrigir a pré-carga; trocar filtros; reparar vazamento |
| Viga lenta ou parada | HIDRAULICA (1); AI019, AI016 | Falha de válvula servo, travamento mecânico, cilindro com fuga | Tempo de ciclo; posição da viga | Parar o avanço de forma controlada; chamar manutenção |

**Cadeia de uma falha de queimador.**
1. O queimador cai. A zona perde potência.
2. As zonas vizinhas compensam e o consumo sobe.
3. Se o ritmo não cai, a placa perde temperatura (AI007).
4. A placa fria chega ao R1 e a força sobe.

Em cada caso, confirme nos dados antes de agir: `verificar_parametros` e `historico`.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

**Placa fria.**
- Fontes de mercado indicam que, se a placa sai fria, a força necessária pode passar do que a gaiola entrega.
- Na simulação, a força e o torque do R1 sobem 15–25 %.
- A temperatura de acabamento (FDT) fica baixa. O acabador compensa com mais força.
- Há risco de cobble no desbaste ou no acabador, e de a FDT sair da janela.
- FDT baixa piora as propriedades mecânicas e a planicidade da tira.

**Placa quente demais.**
- Mais carepa e maior consumo de gás.
- Risco de superaquecimento e de queima do grão.

**Skid mark.**
- A zona fria na face inferior varia de força ao longo do comprimento da placa.
- No acabador isso vira variação de espessura e de largura.
- A marca fria é a razão pela qual há encharque no fim do forno.

**Placa não uniforme (topo contra fundo, borda contra centro).**
- Gera variação de perfil, de camber e de planicidade.

**Excesso de ar.**
- Mais O₂ forma mais carepa. A carepa laminada para dentro da superfície gera defeito.
- Mais fumos para o recuperador também elevam o consumo (GJ/t).

**Falha da água dos skids.**
- Os tubos podem superaquecer e deformar. Na simulação, é parada de emergência.
- A parada do forno derruba a produção de toda a linha.

**Ritmo e fluxo.**
- Forno parado ou lento deixa o desbaste sem material.
- Placas paradas muito tempo no forno oxidam mais e aumentam a skid mark.

## 8. Manutenção preventiva e preditiva

Periodicidades são típicas. Confirme no manual do fabricante.

| Item | Periodicidade típica | Atividade |
|---|---|---|
| Queimadores e detectores de chama | Turno / semanal | Inspeção visual, limpeza dos detectores, teste de bloqueio |
| Analisadores de O₂ e CO | Turno | Verificar leitura; calibrar com gás padrão |
| Termografia da carcaça | Semanal | Procurar pontos quentes e falhas de refratário |
| Curvas ar/gás e termopares | Mensal | Verificar a relação ar/gás; aferir termopares |
| Ventiladores de ar | Mensal | Vibração, corrente, temperatura de mancal, lubrificação |
| Acumuladores hidráulicos | A cada 2 meses (vendor) | Pré-carga de nitrogênio |
| Filtros e óleo hidráulico | Mensal a trimestral | Análise de óleo, troca de filtro |
| Riders e botões dos skids | A cada 4 semanas (vendor) | Medir o desgaste. Um limite de 3 mm é citado por um fabricante |
| Espessura dos tubos de skid | 8 a 12 semanas (vendor) | Medida ultrassônica |
| Bomba e filtros da água dos skids | Mensal | Vazão, pressão, limpeza, qualidade da água |
| Válvulas de bloqueio de gás | Anual | Teste de estanqueidade |
| Paradas programadas | Anual ou campanha | Refratário, isolamento dos skids, recuperador, data logger para validar o nível 2 |

**Preditiva.**
- Tendência de ΔT da água, pressão hidráulica, vibração dos ventiladores e do sinal do detector de chama.
- Tendência de O₂ e de consumo por zona para achar um queimador degradado antes do trip.
- Comparar o desvio do modelo nível 2 (AI008) com ensaios do data logger.

As periodicidades de fabricantes citadas são material comercial. Elas não são norma.

## 9. Segurança (bloqueio/LOTO, riscos específicos)

- **LOTO.** Bloqueie e etiquete gás (COG, BFG, GN), ar, energia dos ventiladores, hidráulica, água e energia das máquinas de carga.
- **Gás tóxico.** O COG e o BFG têm CO. Use detector de CO portátil e fixo. O BFG não tem cheiro.
- **Explosão.** A mistura gás e ar em forno frio é explosiva. Respeite a purga e a prova de ar do BMS antes de acender.
- **Reacender.** Não reacenda um queimador com o forno quente sem sequência de segurança. Use a partida do BMS.
- **Espaço confinado.** Entrar no forno exige permissão de trabalho, ventilação, medição de gás e vigia.
- **Calor.** Superfícies a mais de 1.000 °C. Use roupa aluminizada e distância das portas.
- **Água.** Vazamento de água de skid dentro do forno quente gera vapor e risco de explosão.
- **Hidráulica.** Alivie a pressão e os acumuladores antes de abrir linhas. A viga pode cair. Trave-a mecanicamente.
- **Normas.** Em furnaces industriais, aplica-se a NFPA 86 (verifique a edição vigente) ou a norma local equivalente.
- **Sistema de segurança.** Nunca anule o BMS, o detector de chama nem o intertravamento de ar.

## 10. Perguntas frequentes do operador

**1. O que fazer quando um queimador cai?**
Verifique o detector de chama e rearme. Reduza o ritmo até a zona voltar ao setpoint. Isso evita placa fria no R1.

**2. Por que a força do R1 subiu?**
Provavelmente a placa saiu fria. Veja AI007 e AI008. Uma placa fria eleva a força de 15 a 25 %.

**3. O O₂ está alto. O que significa?**
Excesso de ar. Pode ser deriva do analisador ou um queimador em trip com ar sem chama. Calibre o analisador e confira DI01.

**4. O que é skid mark?**
É uma marca fria onde a placa apoia nos skids. A água leva calor da placa. O encharque apaga parte dela.

**5. A água dos skids está aquecendo demais. É grave?**
Sim. ΔT acima de 18 °C é alarme. Confira bomba e vazão na hora. Há risco de parada de emergência.

**6. Posso aumentar o ritmo para recuperar produção?**
Só se as zonas estiverem no setpoint. Ritmo alto reduz a residência e a placa sai fria.

**7. O que um ventilador de ar parado causa?**
Perde-se o ar de combustão e os queimadores caem. Passe para o ventilador reserva e religue pela sequência do BMS.

**8. O que é desvio do modelo nível 2?**
É a diferença entre a temperatura medida e a prevista. Acima de 20 °C é alarme. Valide termopares e dados de carga.

## Fontes

- [Skid mark erasure system, US 5,007,824 (Google Patents)](https://patents.google.com/patent/US5007824) — skid marks, causas e apagamento.
- [Method of controlling a reheat furnace to control skid mark effects, US 4,330,263](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4330263) — marca fria e força de laminação.
- [Skid beam for heating furnaces of walking beam type, US 4,747,775](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4747775) — botões, tubo refrigerado e refratário.
- [Water-cooled, workpiece-supporting members for a heating furnace, US 5,284,440](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5284440) — riders e refrigeração.
- [Furnace rider bar assembly, US 5,897,310](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5897310) — cilindros hidráulicos da viga.
- [Reheating Furnace PdM: Burner, Roll & Skid Monitoring (iFactory)](https://ifactoryapp.com/industries/steel-plant/reheating-furnace-predictive-monitoring-burner-roll) — monitoramento de queimadores e skid (material de fornecedor).
- [Reheat Furnace Maintenance for Rolling Mill Steel Plants (Oxmaint)](https://oxmaint.com/industries/steel-plant/reheat-furnace-maintenance-rolling-mill-steel-plant) — periodicidades de manutenção (material de fornecedor).
- [Numerical Simulation of a Pusher-Type Reheat Furnace (Purdue)](https://docs.lib.purdue.edu/dissertations/AAI10618578) — skid marks e uniformidade da placa.
- [Modelling of slab heating in walking beam furnace with skidmarks (RWTH Aachen)](https://www.iob.rwth-aachen.de/en/research/high-temperature-flows/simplified-process-modeling-for-technical-processes/modelling-of-slab-heating-in-walking-beam-furnace-with-skidmarks) — modelo de aquecimento da placa.
- [Burner Management Systems white paper (Siemens)](https://assets.new.siemens.com/siemens/assets/api/uuid:252e2a91-d027-4fa3-a49e-2692e557b5de/2018-BMS-White-Paper-V2.pdf) — BMS, chama e perda de ar.
- [Adaptive control for reheat furnace, US 5,873,959](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5873959) — temperatura de desenfornamento e controle.
