# DSC-02 — Descarepador do acabador — documentação de referência

> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

O descarepador do acabador (finishing scale breaker, FSB) fica na entrada do trem acabador, logo antes do cilindro F1.

- Remove a carepa secundária. Ela se forma depois do descarepador primário, durante a espera e o transporte da barra pela mesa de rolos e pela tesoura/rolamento.
- A barra sai do laminador desbastador a cerca de 1000–1100 °C. Na atmosfera, forma-se uma nova camada de óxido (FeO, Fe3O4, Fe2O3).
- Se essa camada entra no F1–F2, ela é laminada para dentro da superfície da tira. O defeito é a carepa incrustada (rolled-in scale).
- A carepa também aumenta o desgaste e degrada a superfície dos cilindros de trabalho.
- Esta máquina é do mesmo tipo do DSC-01 (descarepador do desbastador), mas trabalha numa faixa de pressão de projeto menor e com a tira mais fina e mais fria.

Na Usina exemplo, o DSC-02 pertence à Linha 3 (Acabamento) e é controlado pelo CLP-DSC-02.

## 2. Princípio de funcionamento

A remoção é mecânica e térmica. Jatos de água em alta pressão incidem sobre a superfície quente.

1. O impacto do jato gera tensão local e trinca a camada de óxido, que é frágil.
2. A água que penetra pelas trincas vaporiza ao contato com o aço quente. A expansão do vapor descola a carepa do metal.
3. O fluxo lateral do jato arrasta os fragmentos para fora da tira.
4. Um segundo conjunto de jatos (ou uma segunda fileira) completa a limpeza. Patentes descrevem a primeira fileira soltando a carepa e a segunda terminando o trabalho, com pressão menor que a de uma fileira única.

O que define a eficiência é a força de impacto por unidade de área, não só a pressão.

- O impacto cresce com a pressão e com a vazão do bico.
- O impacto cai com a distância bico–tira (altura de spray). Menor altura dá mais impacto, mas menos cobertura por bico.
- Aumentar a pressão aumenta a turbulência no bico e acelera o desgaste do bico e do header.
- A relação vazão–pressão no sistema é aproximadamente quadrática, por causa da resistência de bicos e tubulação.

A pressão vem de bombas de alta pressão (de pistão ou multiestágio) que carregam um acumulador hidropneumático. O acumulador atende ao pico de vazão no momento em que a válvula do header abre. O descarepador só aplica água quando há barra na zona (sequência acionada pelos detectores de metal quente).

## 3. Componentes principais

| Componente | Função |
|---|---|
| Headers (coletores) superior e inferior | Distribuem a água às fileiras de bicos; cobrem a largura total da tira |
| Bicos de jato plano (descaling nozzles) | Geram o jato em leque estreito (ângulo típico de 20–30°), com inserto de metal duro em muitos modelos |
| Bombas de alta pressão 1 e 2 | Geram a pressão; uma costuma ser reserva da outra |
| Acumulador hidropneumático | Amortece a queda de pressão na abertura das válvulas; precisa de pré-carga de nitrogênio |
| Válvulas de abertura rápida | Liberam a água somente com a barra presente (economia de energia e de temperatura) |
| Filtros (autolimpantes ou de cartucho) | Protegem os bicos contra partículas; o ΔP indica saturação |
| Tanque e sistema de tratamento de água | Fornece água limpa; controla temperatura e sólidos |
| Guias e rolos de pinça (pinch rolls) | Mantêm a barra a uma altura estável sob o jato |
| Sensores de pressão, vazão, nível, corrente | Alimentam o CLP-DSC-02 |

Fabricantes de referência de mercado para bicos: Lechler (linha Scalemaster, 80–450 bar) e Spraying Systems (DescaleJet, até cerca de 400 bar). O sistema completo costuma ser fornecido por integradores como SMS group, Primetals ou Danieli.

## 4. Parâmetros típicos de operação

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| Pressão no header | ~130–150 bar convencional; acima de 200 bar em instalações modernas; bicos de 80–450 bar | Projeto 150–200 bar; nominal ~200–205 bar; normal 180–215 bar; ideal 200 bar; alarme < 160 bar | AI001 |
| Vazão por ciclo | Depende do número de bicos e da largura da tira | Normal 150–250 m³/h; ideal 200 m³/h | AI002 |
| Nível do acumulador | Operar numa janela média a alta, com pré-carga de N2 conferida | Normal 70–90 %; ideal 80 % | AI003 |
| ΔP do filtro | Alarme quando o filtro satura (limite definido pelo fabricante do filtro) | Normal 0–1,0 bar; ideal 0; alarme > 1,5 bar | AI004 |
| Corrente da bomba 1 | Faixa estável em relação à nominal; desvio indica desgaste ou cavitação | Normal 80–95 % da nominal; ideal 87,5 %; alarme > 105 % | AI005 |
| Corrente da bomba 2 | Idem | Normal 80–95 % da nominal; ideal 87,5 %; alarme > 105 % | AI006 |
| Temperatura da água | Água de processo em temperatura ambiente a morna | Normal 25–40 °C; ideal 32,5 °C | AI007 |

Divergência a notar: a literatura cita 130–150 bar como pressão convencional e mais de 200 bar para casos mais exigentes. A Usina exemplo opera o DSC-02 em 180–215 bar, na parte alta dessa faixa, com alarme em 160 bar.

Outros parâmetros típicos (sem tag na Usina exemplo): distância bico–tira de 100–250 mm, ângulo de inclinação do jato de 10–20° contra o sentido de avanço e tempo de exposição de poucas centenas de milissegundos.

## 5. Instrumentação e sinais do CLP

O CLP-DSC-02 agrupa os sinais em áreas (bits da palavra de áreas do CLP). Quando o bit acende, a área tem um sinal fora da faixa.

| Área (bit) | Tags | O que mede | Leitura rápida |
|---|---|---|---|
| PRESSAO_FLUIDO (bit 13) | AI001 pressão no header, AI003 nível do acumulador, AI004 ΔP do filtro | Pressão disponível para o jato | Pressão baixa, acumulador fora da janela ou filtro saturado |
| AGUA (bit 3) | AI002 vazão por ciclo, AI007 T da água | Quantidade e temperatura da água aplicada | Vazão baixa com pressão estável aponta bico entupido |
| ACIONAMENTO (bit 0) | AI005 corrente da bomba 1, AI006 corrente da bomba 2 | Estado dos motores das bombas | Corrente anômala indica bomba degradada |

Lógica de diagnóstico combinada:

- **Pressão baixa e vazão alta:** vazamento, bico quebrado/desgastado (orifício maior) ou bomba fraca.
- **Pressão estável e vazão baixa:** bicos entupidos ou válvula parcialmente aberta.
- **Pressão baixa, vazão baixa, corrente alta:** cavitação, desgaste interno da bomba ou sucção restrita.
- **Pressão baixa e nível do acumulador estável:** problema na geração (bomba), não no acumulador.
- **ΔP do filtro subindo, pressão a jusante caindo:** filtro saturando.
- **Diferença grande entre AI005 e AI006:** uma bomba degradada; compare as duas.

O código de alarme segue o formato AAKK (AA = bit da área, KK = tipo). Por exemplo, 1301 = valor analógico abaixo do limite de alarme na área PRESSAO_FLUIDO.

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Pressão do header abaixo de 160 bar | PRESSAO_FLUIDO / AI001 | Bomba degradada ou acumulador sem pré-carga | Comparar AI005/AI006; conferir pré-carga de N2 com acumulador despressurizado | Passar para a bomba reserva; programar manutenção da bomba |
| Pressão cai no início de cada barra | PRESSAO_FLUIDO / AI001, AI003 | Acumulador sem pré-carga ou com bexiga rompida | Observar queda do nível AI003 em cada abertura; medir pré-carga | Recarregar N2 ou trocar a bexiga |
| ΔP do filtro acima de 1,5 bar | PRESSAO_FLUIDO / AI004 | Filtro saturado por sólidos | Ver tendência de AI004 e a qualidade da água | Retrolavar ou trocar o filtro |
| Vazão baixa com pressão estável | AGUA / AI002 | Bico entupido | Inspeção visual do padrão de jato na parada; comparar vazão com a nominal | Inspecionar e limpar os bicos |
| Vazão alta com pressão baixa | AGUA / AI002, PRESSAO_FLUIDO / AI001 | Bico desgastado (orifício aumentado), bico perdido ou vazamento no header | Inspecionar o leque dos bicos; procurar vazamentos | Trocar bicos; reparar o header |
| Corrente de bomba acima de 105 % | ACIONAMENTO / AI005 ou AI006 | Desgaste da bomba, cavitação, sucção restrita | Comparar com a outra bomba; ouvir ruído e medir vibração | Inspecionar a bomba; passar para a reserva |
| Temperatura da água fora de 25–40 °C | AGUA / AI007 | Tanque ou trocador com problema; reposição de água quente | Verificar o circuito de resfriamento e o tanque | Corrigir a temperatura; água quente reduz a eficiência na bomba (risco de cavitação) |
| Carepa na tira com sinais normais | (sem alarme) | Desgaste progressivo dos bicos ou desalinhamento do header | Inspecionar bicos, altura e ângulo; conferir sequenciamento das válvulas | Ajustar a posição; trocar bicos |
| Marcas periódicas ou faixas de temperatura na tira | (sem alarme) | Sobreposição ruim dos jatos, bico entupido isolado | Inspeção do padrão de jato e termografia da tira | Corrigir espaçamento e ângulo; limpar bicos |

Ponto de atenção: o desgaste dos bicos muda o ângulo e a borda do leque, e muda a vazão. Pressão normal não garante bom descarepamento.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

Equipamentos a jusante:

- **Cilindros F1–F2:** carepa residual aumenta o desgaste e a rugosidade dos cilindros e antecipa a troca de campanha.
- **Cilindros seguintes:** a carepa solta pode contaminar o filme de óleo e o banho de refrigeração.
- **Trem acabador:** variação de atrito altera a força de laminação, o que pode afetar o controle de espessura.

Qualidade da tira:

- **Carepa incrustada (rolled-in scale):** manchas escuras, alongadas na direção de laminação. Vira defeito visível após decapagem, ou "carepa vermelha" (Fe2O3) em aços sensíveis.
- **Carepa secundária:** desenvolve-se com o tempo de exposição e a temperatura da superfície; descarepamento fraco aumenta a quantidade que entra no F1.
- **Temperatura da tira:** a água em alta pressão resfria a superfície. Um estudo japonês de 1991 relaciona a queda de temperatura ao volume de água, à pressão e à distância bico–aço. Mais distância com mais volume mantém a queda pequena. Em tira fina a queda é maior em relação à espessura, o que pode afetar a temperatura de acabamento (FT).
- **Efeito de excesso de água:** subresfriamento da superfície, bordas mais frias e variação de propriedades mecânicas.
- **Descarepamento desigual:** a distribuição irregular dos jatos pode gerar padrões periódicos de temperatura e de carepa secundária.

Em resumo, pouca pressão gera defeito de superfície; água demais ou aplicada fora de tempo derruba a temperatura de acabamento.

## 8. Manutenção preventiva e preditiva

As periodicidades abaixo são típicas e devem ser ajustadas ao histórico da planta.

| Atividade | Periodicidade típica |
|---|---|
| Inspeção visual dos bicos (padrão de jato, entupimento, erosão) | A cada parada programada (semanal ou por campanha de cilindros) |
| Troca de bicos desgastados | Por tonelagem ou estado do leque; verificar a cada campanha |
| Limpeza ou retrolavagem de filtros | Conforme ΔP (AI004); preventiva mensal |
| Conferência da pré-carga do acumulador (N2) | Mensal a trimestral |
| Inspeção do header (vazamentos, alinhamento, altura) | A cada campanha |
| Revisão das bombas (selos, válvulas, êmbolos) | Conforme horas de operação e fabricante |
| Análise de vibração e corrente das bombas | Contínua ou mensal |
| Qualidade da água (sólidos, temperatura) | Semanal |
| Teste das válvulas de abertura rápida | A cada campanha |

Manutenção preditiva:

- Acompanhe a tendência de AI001, AI002 e AI004 por barra, não só os limites.
- Compare AI005 e AI006 entre as duas bombas para achar degradação cedo.
- Medir a razão vazão/pressão ao longo do tempo mostra o desgaste dos bicos.
- Termografia da tira na saída do FSB ajuda a achar bicos entupidos.

## 9. Segurança

- **LOTO:** bloqueie e etiquete as bombas (elétrico), as válvulas de bloqueio do header e o suprimento de água. Despressurize o header e o acumulador antes de abrir qualquer conexão.
- **Alta pressão:** jatos acima de 150 bar causam ferimentos graves por injeção. Nunca procure vazamento com a mão.
- **Acumulador:** vaso com nitrogênio pressurizado. Só despressurize a parte do gás e do fluido seguindo o procedimento do fabricante e a norma de vasos de pressão (NR-13 no Brasil).
- **Superfícies quentes e vapor:** a zona fica junto à barra a 1000 °C; há risco de queimadura, vapor e fragmentos de carepa projetados.
- **Escorregamento:** água e carepa no piso. Mantenha a drenagem limpa.
- **Ruído:** bombas e jatos exigem proteção auditiva.
- **Espaço confinado:** a caixa do descarepador pode exigir permissão de entrada.
- **Teste de bicos:** só com a barra ausente e a área isolada; use proteção facial.

## 10. Perguntas frequentes do operador

**1. Por que a pressão do header caiu?**
Bomba degradada, acumulador sem pré-carga ou filtro saturado. Olhe a corrente das bombas e o ΔP do filtro. Se uma bomba está pior, passe para a reserva.

**2. A vazão caiu mas a pressão está boa. O que é?**
Provavelmente bico entupido. Programe a limpeza dos bicos na próxima parada.

**3. Qual a pressão normal do DSC-02?**
Perto de 200 bar, com faixa normal de 180 a 215 bar. O alarme dispara abaixo de 160 bar.

**4. Por que importa o descarepador se a tira parece boa?**
Carepa não removida é laminada para dentro da tira e desgasta os cilindros F1 e F2. O defeito só aparece depois.

**5. O que fazer se a corrente de uma bomba passa de 105 %?**
Compare com a outra bomba, passe para a reserva e peça inspeção. Pode ser desgaste ou cavitação.

**6. Água demais também é problema?**
Sim. Resfria a tira e pode baixar a temperatura de acabamento. O ideal é o jato certo, só quando há barra.

**7. O que o ΔP do filtro indica?**
Quanto o filtro está sujo. Acima de 1,5 bar é hora de retrolavar ou trocar.

**8. Posso olhar o bico com o sistema ligado?**
Não. Bloqueie, despressurize e só então inspecione.

## Fontes

- [Lechler — Descaling (aplicação de descarepamento)](https://lechler.com/my-en/applications/descaling)
- [Spraying Systems — Descaling Impact](https://www.spray.com/applications/descaling-impact)
- [Spraying Systems — Steel mills, hot rolling mills (catálogo C44B)](https://www.Spray.com/en-ph/-/media/dam/industrial/usa/sales-material/catalog/c44b_steel-mills_hot-rolling-mills_c.pdf)
- [Spraying Systems — Optimizing descaling (boletim B628B)](https://www.Spray.com/-/media/dam/industrial/usa/sales-material/product-market-bulletin/b628b_optimizing_descaling.pdf)
- [US 10378115 — Economic secondary descaling (patente)](https://patents.google.com/patent/US10378115)
- [US 5996200 — Descaling device and method (patente)](https://patents.google.com/patent/US5996200)
- [US 7181943 — Descaling method for strip-rolling mill (patente)](https://patents.google.com/patent/US7181943B2/cs)
- [US 4617815 — Apparatus for descaling hot strip in a rolling mill (patente)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4617815)
- [Tetsu-to-Hagané, 1991, vol. 77, nº 9, p. 1458–1464 — queda de temperatura no descarepamento hidráulico](https://www.jstage.jst.go.jp/article/tetsutohagane1955/77/9/77_9_1458/_article/-char/en)
