# DSC-01 — Descarepador primário — documentação de referência
> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

O descarepador primário fica logo após o forno de reaquecimento de placas, antes do laminador de desbaste (Linha 2 — Desbaste).

- Remove a carepa primária: óxido de ferro formado no forno, em geral de 0,5 a 3 mm de espessura na superfície da placa.
- Entrega superfície limpa ao desbaste, para a carepa não ser prensada no aço.
- Também esfria levemente a superfície da placa. Esse efeito é secundário e precisa ser considerado pelo modelo térmico.
- Atua em conjunto com os descarepadores do desbaste e com o quebrador de carepa na entrada do acabador (descarepação secundária).

Se a carepa primária não sai, ela pode ser laminada para dentro da tira. É o defeito conhecido como carepa incrustada (rolled-in scale).

## 2. Princípio de funcionamento

Descarepação hidráulica: jatos de água a alta pressão batem na superfície quente da placa.

Mecanismos que soltam a carepa:
1. **Impacto mecânico.** O jato em forma de leque transfere força por área (N/mm²). Essa força trinca a carepa frágil.
2. **Choque térmico.** A água fria contrai a carepa mais do que o metal, e a camada se desprende.
3. **Vapor sob a carepa.** A água entra nas trincas, vaporiza e levanta a camada.
4. **Arraste.** O fluxo lateral lava os fragmentos para fora da placa.

Variáveis que definem a eficiência:
- **Impacto específico.** É a principal medida de eficiência de um bico de descarepação. Depende da pressão, da vazão do bico e da distância bico–placa.
- **Pressão.** A vazão cresce com a raiz da pressão. A pressão, por sua vez, sobe com o quadrado da vazão total no circuito (resistência de bicos e tubos).
- **Distância.** O impacto cai quando a distância aumenta, pois o jato se abre e perde energia.
- **Ângulo de inclinação (lead angle).** O bico é inclinado cerca de 15° no sentido de avanço do jato. Isso evita que a água rebatida e a carepa soltas atrapalhem o jato direto.
- **Ângulo de leque.** Bicos de descarepação comerciais têm leque de cerca de 22° a 40°.
- **Ângulo de offset.** Cada bico é girado levemente em relação à linha transversal do header, para os leques vizinhos não interferirem.
- **Sobreposição dos leques.**
  - Excesso: a água de um jato bloqueia o seguinte e deixa faixas mal descarepadas.
  - Falta: deixa faixas sem jato.
- **Temperatura e composição da placa.** Aços com silício alto formam uma camada interna (fayalita) aderente, mais difícil de remover.

## 3. Componentes principais

| Componente | Descrição | Observação |
|---|---|---|
| Headers (superior e inferior) | 2 pares de headers, cerca de 25 bicos por header (Usina exemplo) | Tubos de aço com bicos rosqueados ou em cartuchos |
| Bicos de descarepação | Ponta de metal duro (carboneto de tungstênio) ou aço endurecido, leque plano | Referência de mercado: Lechler Scalemaster (80–450 bar), Spraying Systems DescaleJet |
| Bombas de alta pressão | Bombas de êmbolo (plunger) ou centrífugas multiestágio, normalmente 2 ou mais, com reserva | Acionamento por motor elétrico, às vezes com inversor |
| Acumulador | Vaso com colchão de nitrogênio e água | Amortece pulsação e cobre quedas curtas de vazão quando vários headers abrem juntos |
| Filtros | Filtros autolimpantes ou de cartucho antes das bombas e dos bicos | Evitam entupimento dos bicos |
| Válvulas de disparo | Válvulas de abertura rápida, comandadas pelo rastreamento da placa | Abrem só quando a placa passa |
| Válvulas de recirculação/alívio | Mantêm a pressão pronta e protegem as bombas | Recirculação em espera reduz o tempo de resposta |
| Tanque e tratamento de água | Água recirculada de fosso de carepa, decantação e resfriamento | Temperatura típica de 25–40 °C |
| Chapas de proteção e exaustão de vapor | Cabine de contenção | Reduz respingo e vapor sobre sensores |
| Instrumentação | Transmissores de pressão, medidor de vazão, nível do acumulador, ΔP do filtro, corrente das bombas | Ver seção 5 |

Referência: sistemas modernos podem usar bombas com inversor e controle antecipatório ligado ao rastreamento. Isso economiza energia e pode dispensar bomba reserva.

## 4. Parâmetros típicos de operação

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| Pressão no header | cerca de 150–250 bar em sistemas convencionais; bicos de 80–450 bar | ideal 200 bar; normal 180–220 bar; alarme abaixo de 160 bar | AI001 |
| Vazão por ciclo | depende do número de bicos e do bico (centenas de m³/h no ciclo de disparo) | ideal 325 m³/h; normal 250–400 m³/h | AI002 |
| Nível do acumulador | depende do projeto; vaso mantido com colchão de gás | ideal 80 %; normal 70–90 % | AI003 |
| ΔP do filtro | baixo com filtro limpo; sobe com saturação | ideal 0; normal 0–1,0 bar; alarme acima de 1,5 bar | AI004 |
| Corrente da bomba 1 | 80–95 % da nominal em regime | ideal 87,5 %; normal 80–95 %; alarme acima de 105 % | AI005 |
| Corrente da bomba 2 | idem | ideal 87,5 %; normal 80–95 %; alarme acima de 105 % | AI006 |
| Temperatura da água | 25–40 °C (água recirculada) | ideal 32,5 °C; normal 25–40 °C | AI007 |
| Distância bico–placa | cerca de 100–200 mm | 100–200 mm (fixo, mecânico, sem tag) | — |
| Ângulo de inclinação | cerca de 15° (prática convencional) | 15° (fixo, sem tag) | — |
| Ângulo de leque | 22°–40° em bicos comerciais | não informado no manual do CLP | — |

Divergências a observar:
- A indústria não tem um valor único de pressão. Há sistemas convencionais de cerca de 200 bar e bicos que chegam a 450 bar. O valor de 200 bar da simulação está dentro da faixa convencional.
- Na simulação só existe limite inferior de alarme na pressão (160 bar). Na prática também se avisa pressão alta, por risco para tubos e bicos.

## 5. Instrumentação e sinais do CLP

CLP: CLP-DSC-01. As áreas usam os bits da palavra de falha/aviso do manual padrão do CLP.

### Bit 13 — PRESSAO_FLUIDO
- **AI001** `pressao_header`: pressão no header de bicos. É o sinal mais direto de capacidade de descarepação.
- **AI003** `nivel_acumulador`: nível do acumulador. Nível baixo indica pré-carga errada, fuga de gás ou vazamento.
- **AI004** `dp_filtro`: perda de carga no filtro. Alarme acima de 1,5 bar.
- Alarme típico: 1301 (abaixo do alarme, AI001), 1311 (abaixo da faixa normal), 1312 (acima da faixa normal), 1302 (ΔP do filtro alto, AI004).

### Bit 3 — AGUA
- **AI002** `vazao_ciclo`: vazão por ciclo de disparo.
- **AI007** `t_agua`: temperatura da água.
- Vazão baixa com pressão estável sugere bico entupido. Vazão baixa com pressão baixa sugere perda de pressão ou bomba fraca.

### Bit 0 — ACIONAMENTO
- **AI005** `corrente_bomba_1` e **AI006** `corrente_bomba_2`: corrente em % da nominal. Alarme acima de 105 %.
- Compare as duas correntes entre si. Uma bomba muito diferente da outra indica desgaste ou cavitação.

### Leitura combinada

| Combinação | Interpretação provável |
|---|---|
| Pressão baixa, vazão baixa, corrente baixa | Bomba degradada ou desarmada, perda de alimentação |
| Pressão baixa, nível do acumulador baixo | Pré-carga do acumulador fora, vazamento de gás |
| Pressão estável, vazão baixa | Bicos entupidos |
| Pressão baixa, ΔP do filtro alto | Filtro saturado restringindo a sucção ou o recalque |
| Corrente alta numa bomba, pressão normal | Desgaste mecânico, atrito, alinhamento |
| Corrente oscilando, ruído | Cavitação (NPSH baixo, água quente, filtro de sucção sujo) |

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Pressão do header abaixo de 180 bar (aviso) ou 160 bar (alarme) | PRESSAO_FLUIDO / AI001 | Bomba degradada; acumulador sem pré-carga | Comparar correntes das bombas; medir pré-carga de nitrogênio com o vaso despressurizado | Passar para a bomba reserva; recarregar o acumulador; programar manutenção da bomba |
| Nível do acumulador fora de 70–90 % | PRESSAO_FLUIDO / AI003 | Fuga de gás ou bexiga/pistão danificado; válvula de nível | Verificar pré-carga, vazamento de gás, instrumento de nível | Recarregar nitrogênio; reparar o vaso |
| ΔP do filtro acima de 1,0 bar (aviso) ou 1,5 bar (alarme) | PRESSAO_FLUIDO / AI004 | Filtro saturado por carepa fina ou sujeira | Ler a tendência do ΔP; inspecionar elemento | Retrolavar ou trocar o filtro |
| Vazão por ciclo baixa e pressão estável | AGUA / AI002 | Bico entupido ou desgastado | Observar o padrão do jato; inspecionar os bicos | Inspecionar e limpar os bicos |
| Vazão alta com pressão baixa | AGUA / AI002 e AI001 | Bico desgastado (furo alargado), vazamento em flange, mangueira rompida | Procurar jato fora da placa; inspecionar as conexões | Trocar bicos; corrigir o vazamento |
| Temperatura da água acima de 40 °C | AGUA / AI007 | Falha no resfriamento da água; recirculação excessiva | Verificar trocador/torre e nível do tanque | Restabelecer o resfriamento; reduzir recirculação |
| Corrente da bomba acima de 95 % (aviso) ou 105 % (alarme) | ACIONAMENTO / AI005, AI006 | Desgaste, cavitação, rolamento ruim | Comparar com a outra bomba; ouvir ruído; checar vibração e temperatura de mancal | Trocar para a reserva; inspecionar a bomba |
| Corrente baixa com pressão caindo | ACIONAMENTO / AI005, AI006 e AI001 | Bomba perdendo capacidade (folga interna, válvulas do êmbolo) | Comparar com histórico | Trocar para a reserva; revisar válvulas e vedações |
| Carepa residual na placa com todos os sinais normais | — (sem alarme) | Bicos desalinhados, ângulo ou distância fora do padrão, sobreposição ruim | Inspeção visual da superfície e do padrão de jato | Realinhar bicos; revisar o ajuste mecânico |

Procedimento resumido:
1. Veja qual área acendeu (bit 13, 3 ou 0).
2. Leia as tags e confira a faixa do manual.
3. Compare pressão, vazão, nível e corrente em conjunto (seção 5).
4. Confirme no histórico quando o desvio começou.
5. Passe para a bomba reserva se a pressão estiver em queda.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

- **Carepa residual ou incrustada.** Se a carepa primária não sai, ela é laminada para dentro da superfície da tira. Pode aparecer como manchas escuras, riscas ou marcas alongadas.
- **Defeito "carepa vermelha" (red scale).** Surge quando carepa aderente, em geral de aços com silício alto, sobrevive à descarepação. Aparece depois do bobinamento ou do resfriamento.
- **Desgaste dos cilindros.** No acabador, os cilindros F1–F2 se desgastam mais, pois a carepa dura é abrasiva. Pode haver marcas nos cilindros e queda na campanha.
- **Carepa secundária.** Se a espessura do óxido no acabador passar de poucos micrômetros (uma patente cita cerca de 5 μm no terceiro estágio), aumentam os defeitos.
- **Temperatura.** Pressão alta demais ou vazão excessiva esfria a placa em excesso, o que afeta a temperatura de saída do desbaste (esboço) e as forças de laminação.
- **Descarepação irregular em faixas.** Bicos entupidos ou sobreposição ruim deixam faixas com carepa. Isso causa defeitos em linhas ao longo da tira.
- **Efeito na decapagem a jusante.** Carepa mal removida torna a decapagem mais difícil e consome mais ácido.
- **Aspecto de superfície.** Para produtos expostos, o defeito leva a desclassificação ou reprocesso.

## 8. Manutenção preventiva e preditiva

Periodicidades típicas (ajustar à experiência da planta):

| Item | Periodicidade típica | Ação |
|---|---|---|
| Bicos | a cada parada programada ou campanha (semanal a mensal) | Inspeção visual do padrão de jato; limpeza; troca dos desgastados |
| Alinhamento dos bicos (ângulo, offset, distância) | a cada troca de bico e a cada parada | Conferir com gabarito |
| Filtros | conforme a tendência do ΔP (AI004); inspeção semanal | Retrolavar ou trocar o elemento |
| Pré-carga do acumulador | mensal a trimestral | Medir pré-carga com o vaso despressurizado; recarregar nitrogênio |
| Bombas — válvulas e vedações do êmbolo | por horas de operação, conforme o fabricante | Troca preventiva de vedações e válvulas |
| Bombas — rolamentos e alinhamento | trimestral a semestral | Análise de vibração, termografia, análise de óleo |
| Válvulas de disparo | a cada parada programada | Testar tempo de abertura e vedação |
| Tubulação, flanges, mangueiras | mensal | Procurar vazamento e trinca |
| Instrumentos (pressão, vazão, nível) | semestral | Calibrar |

Manutenção preditiva:
- Acompanhar a tendência de AI001, AI002 e AI004.
- Comparar sempre as correntes AI005 e AI006. Divergência crescente indica desgaste.
- Acompanhar a queda lenta do nível do acumulador (AI003), que indica fuga de gás.
- Fazer vibração e termografia nas bombas.
- Trocar bicos por vida útil estimada (horas ou toneladas), não só por falha.

## 9. Segurança (bloqueio/LOTO, riscos específicos)

- **Alta pressão.** Jato de 200 bar corta pele e causa injeção de fluido. Nunca teste o jato com a mão.
- **Energia armazenada.** O acumulador guarda pressão de água e de gás. Despressurize e confirme zero no manômetro antes de abrir qualquer conexão.
- **LOTO.** Bloqueie e etiquete: disjuntores das bombas, válvulas de disparo, válvulas de isolamento do acumulador e fontes de nitrogênio. Teste a ausência de energia.
- **Placa quente.** Risco de queimadura e de radiação térmica. Só entre na cabine com a linha parada e a placa fora da zona.
- **Vapor.** O jato sobre a placa gera vapor e respingo. Mantenha a exaustão funcionando.
- **Nitrogênio.** Há risco de asfixia em espaço confinado. Use só nitrogênio para o acumulador, nunca oxigênio ou ar.
- **Carepa.** Fragmentos quentes e cortantes no fosso. Use EPI completo.
- **Ruído.** As bombas e o jato geram alto nível de ruído. Use protetor auricular.
- **Espaço confinado.** O fosso de carepa e os tanques exigem permissão de trabalho específica.

## 10. Perguntas frequentes do operador

1. **Por que a pressão do header caiu?**
   Em geral é a bomba, o acumulador ou o filtro. Veja a corrente das bombas, o nível do acumulador e o ΔP do filtro.

2. **A vazão caiu, mas a pressão está normal. O que é?**
   Provavelmente bico entupido. Peça inspeção e limpeza dos bicos.

3. **Posso continuar laminando com a pressão no limite de alarme?**
   Só por pouco tempo. Passe para a bomba reserva. Com pressão baixa fica carepa na placa e o risco de carepa incrustada sobe.

4. **A corrente de uma bomba está mais alta que a da outra. E agora?**
   Indica desgaste ou cavitação. Passe para a reserva e programe a inspeção da bomba.

5. **O que o nível baixo do acumulador significa?**
   Pré-carga de nitrogênio fora ou fuga de gás. Peça a verificação com o vaso despressurizado.

6. **Por que o ΔP do filtro sobe?**
   O filtro está sujo de carepa fina ou impurezas. Retrolave ou troque o elemento.

7. **Que defeito aparece se a descarepação falha?**
   Carepa incrustada na tira, marcas e mais desgaste dos cilindros do acabador, em especial F1 e F2.

8. **A água quente atrapalha?**
   Acima de 40 °C aumenta o risco de cavitação nas bombas e reduz o choque térmico. Verifique o resfriamento da água.

## Fontes

- [Lechler — Descaling (aplicação)](https://lechler.com/my-en/applications/descaling): impacto em N/mm² como critério de eficiência do bico; faixa de 80–450 bar.
- [Lechler — Nozzles for descaling](https://www.lechler.com/my-en/products/metallurgy/nozzles-for-descaling): bicos Scalemaster, leques de 22°–40°, até 450 bar, ponta de metal duro.
- [Spraying Systems — DescaleJet Ultra nozzles (boletim B827)](https://www.spray.com/lv-lv/-/media/dam/industrial/usa/sales-material/product-market-bulletin/b827-descalejet-ultra-nozzles.pdf): bicos de descarepação, impacto e uniformidade do jato.
- [US 5996200 — Descaling device and method](https://patents.google.com/patent/US5996200): relação entre vazão, pressão e impacto.
- [US 5661884 — Offset high-pressure water descaling system](https://patents.google.com/patent/US5661884): headers superior e inferior, energia das bombas, interferência entre jatos.
- [US 9174256 — Hot rolling high-pressure fluid descaling method and descaling apparatus](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9174256): ângulo de inclinação (cerca de 15°), offset e sobreposição dos leques.
- [US 10695810 — Descaling system and control method](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10695810): acumulador, bombas múltiplas e operação em espera.
- [US 6257034 — System and method for preventing scale defects during hot rolling](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6257034): defeitos de carepa e espessura do óxido.
- [Machinemfg — Defects in hot rolled steel strips](https://machinemfg.com/defects-in-hot-rolled-steel-strips): causas de carepa incrustada, pressão baixa e bicos entupidos.
