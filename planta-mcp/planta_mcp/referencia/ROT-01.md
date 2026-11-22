# ROT-01 — Mesa de resfriamento laminar — documentação de referência

> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

- A mesa de resfriamento laminar (ROT, run-out table) fica entre o último cadeira de acabamento (FDT) e as bobinadeiras.
- Ela resfria a tira de cerca de 800–900 °C até a temperatura de bobinamento (CT, coiling temperature).
- A CT é a variável de controle principal. Ela define a microestrutura final: ferrita, perlita, bainita e precipitados.
- Portanto a CT define resistência, ductilidade, tamanho de grão e conformabilidade da bobina.
- Na Usina exemplo, o CLP é o CLP-ROT-01, na linha 4 (resfriamento e bobinamento).
- Alvos de CT da usina: baixo carbono 600–680 °C, IF 680–740 °C, HSLA 500–600 °C.
- A mesa tem 100–120 m, 4 headers intensivos e 20 bancos laminares.
- Cada banco laminar tem 4 headers em cima e 4 embaixo.
- A vazão total fica entre 8.000 e 12.000 m³/h.
- Referências de mercado: Primetals (Power Cooling), SMS (headers de vazão uniforme) e TMEIC (modelo de controle de CT).

## 2. Princípio de funcionamento

### 2.1 Troca de calor
- A água cai sobre a tira em colunas contínuas (jatos laminares) de baixa pressão.
- Em cima, a água sai de tubos em U (U-tubes) ou bicos tipo cortina. Embaixo, usam-se bicos de jato ascendente.
- Um jato laminar rompe a película de vapor que se forma sobre a tira quente. Por isso ele resfria mais que um jato turbulento.
- Em tiras quentes ocorre ebulição em filme e depois ebulição nucleada. O coeficiente de troca muda com a temperatura da superfície.
- A água fria e a tira ficam em contato, e a água aquecida escorre pelas bordas.
- A taxa de resfriamento depende da espessura: tiras finas esfriam bem mais rápido que tiras grossas.

### 2.2 Seção intensiva (resfriamento acelerado)
- Os headers intensivos operam com pressão bem maior (3–10 bar na simulação).
- Eles aumentam a pressão de impacto da água e alcançam taxas de 100–300 °C/s.
- Fabricantes publicam taxas de até 400 K/s para tiras finas em sistemas de alta pressão de impacto.
- Uso típico: refinar grão logo após a última cadeira e produzir aços de fase dupla e HSLA de alta resistência.

### 2.3 Estratégias de resfriamento
- **Normal (frontal):** os primeiros bancos ficam abertos. A tira esfria cedo e fica mais fina em grão.
- **Final (back-loaded):** os últimos bancos ficam abertos. Há tempo de recuperação do grão austenítico antes de resfriar.
- **Duas etapas:** resfriamento intensivo, pausa em ar e resfriamento final. É usado para aços HSLA e multifásicos.
- Os bancos são ligados e desligados em grupos (válvulas on/off) para ajustar a quantidade de água.
- O ajuste fino é feito por bancos de trim com válvula de vazão controlada.

### 2.4 Controle de CT (níveis 1 e 2)
- **Setup (pré-cálculo):** o modelo de nível 2 recebe espessura, velocidade, FDT e CT alvo e calcula quantos bancos abrir.
- **Feedforward:** corrige o padrão durante a passagem, com base na FDT medida e na aceleração do trem.
- **Feedback:** compara a CT medida pelo pirômetro de bobinamento com a CT visada e ajusta bancos de trim.
- **Autoaprendizado:** o modelo adapta o coeficiente de troca de calor entre bobinas. É o parâmetro de ajuste mais sensível.
- A mesa acelera durante o enfiamento. Com a aceleração, o tempo sob água cai e a CT sobe se o modelo não compensar.
- Controladores clássicos usam modelo de zona a zona, com predição da queda de temperatura por banco.

## 3. Componentes principais

| Componente | Função |
|---|---|
| Bancos laminares (20 na simulação) | Conjuntos de headers superiores e inferiores que aplicam a água. |
| Headers superiores | Tubos distribuidores com U-tubes ou bicos de cortina, alimentados por caixa de nível. |
| Headers inferiores | Bicos de jato ascendente entre os rolos da mesa. |
| Headers intensivos (4) | Seção de alta pressão logo após a última cadeira. |
| Válvulas de banco | Válvulas on/off ou proporcionais, comandadas pelo CLP. |
| Medidores de vazão | Eletromagnéticos ou ultrassônicos por banco e na adução. |
| Tanque elevado / caixa de nível | Garante carga hidrostática estável para o fluxo laminar. |
| Bombas e torre de resfriamento | Fornecem a água e mantêm a temperatura da água. |
| Filtros e sistema de tratamento | Retiram carepa e partículas que entopem os bicos. |
| Resfriamento lateral (side sprays) | Jatos de água ou ar que limpam e deslocam a água das bordas. |
| Máscaras de borda (edge masks) | Cobrem as bordas e evitam super-resfriamento lateral. |
| Pirômetro de FDT | Mede a temperatura na entrada da mesa. |
| Pirômetro de CT | Mede a temperatura na saída, antes da bobinadeira. |
| Rolos da mesa | Transportam a tira. Sincronizados com a velocidade do trem. |
| Modelo de CT (nível 2) | Calcula e adapta o padrão de bancos. |

## 4. Parâmetros típicos de operação

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| Vazão por banco laminar | Depende do projeto: centenas de m³/h por banco | Setpoint 200 m³/h, faixa 0–250, alarme baixo < 160 | AI001–AI020 |
| Vazão total (laminar + intensivo) | Milhares de m³/h, conforme comprimento da mesa | Ideal 10.000 m³/h, faixa 8.000–12.000 | AI021 |
| Pressão do header laminar | Baixa pressão, dezenas a centenas de mbar na saída do bico | Ideal 0,75 bar, faixa 0,5–1,0 bar | AI022 |
| Pressão do header intensivo | Alta pressão (alguns bar até dezenas de bar) | Ideal 6,5 bar, faixa 3–10 bar | AI023 |
| Temperatura da água | Cerca de 25–40 °C | Ideal 31,5 °C, faixa 28–35, alarme alto > 38 | AI024 |
| Taxa de resfriamento laminar | 10–50 °C/s, conforme espessura | Ideal 25 °C/s, faixa 10–40 | AI025 |
| Taxa de resfriamento intensivo | 100–400 °C/s | Ideal 200 °C/s, faixa 100–300 | AI026 |
| CT visada | Baixo carbono 600–720 °C; HSLA 500–650 °C | 500–740 °C (por bobina em processo) | AI027 |
| CT medida | Idem | 500–740 °C | AI028 |
| Erro de CT (medida − visada) | Tolerância comum de ±10 a ±25 °C | Ideal 0, faixa −20 a +20, alarme ±30 °C | AI029 |

Divergências e observações:
- A simulação usa um setpoint único de 200 m³/h por banco. Na indústria, a vazão varia por banco e por receita.
- 20 bancos x 200 m³/h dão 4.000 m³/h. O restante do total de 10.000 m³/h seria o intensivo e outros consumos.
- A pressão de 0,5–1,0 bar no header laminar é de pressão de alimentação. Na saída dos bicos é bem menor.
- CT visada e CT medida não têm limite de alarme próprio. O alarme é dado pelo erro de CT (AI029).

## 5. Instrumentação e sinais do CLP

O CLP acende bits de área na palavra de falha ou de aviso. O diagnóstico vem do manual e dos dados.

### Bit 3 — AGUA
- Tags: AI001–AI020 (vazão por banco), AI021 (vazão total) e AI024 (temperatura da água).
- Alarme baixo de vazão por banco em 160 m³/h. Código de alarme 0301 (abaixo do limite).
- Alarme alto da temperatura da água em 38 °C. Código 0302 (acima do limite).
- Fora da faixa normal gera aviso: 0311 (abaixo) ou 0312 (acima).
- Causa no manual: banco entupido, com CT +20 a +50 °C e propriedades fora da especificação.
- Causa no manual: água fora do ideal (torre de resfriamento e bombas).

### Bit 13 — PRESSAO_FLUIDO
- Tags: AI022 (header laminar) e AI023 (header intensivo).
- Sem limites de alarme na simulação. Só aviso fora da faixa normal.
- Causa no manual: água de resfriamento fora do ideal. Conferir torre e bombas.

### Bit 4 — TERMICA
- Tags: AI025 (taxa laminar), AI026 (taxa intensiva), AI027 (CT visada), AI028 (CT medida).
- Causa no manual: CT fora do alvo por banco entupido, pirômetro de CT sujo ou aceleração do trem.
- Ação: conferir a vazão por banco e limpar o pirômetro de CT.

### Bit 9 — QUALIDADE
- Tag: AI029 (erro de CT = medida − visada).
- Alarme em ±30 °C. Códigos 0901 (abaixo) e 0902 (acima). Aviso fora de ±20 °C.
- É o sinal de qualidade principal da mesa. Ele liga mais cedo ou mais tarde que os outros bits.

### Leitura combinada
- Vazão baixa em um banco (AGUA) e erro de CT positivo (QUALIDADE): banco entupido ou válvula travada.
- Erro de CT sem queda de vazão: suspeitar do pirômetro, do modelo ou da aceleração do trem.
- Pressão dos headers fora da faixa (PRESSAO_FLUIDO) com vazão total baixa: problema de bomba ou de adução.
- Temperatura da água alta (AGUA) e erro de CT positivo: troca de calor reduzida, ver torre.

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Vazão de um banco abaixo de 160 m³/h | AGUA / AI001–AI020 (código 0301) | Bicos ou U-tubes entupidos por carepa; válvula do banco travada | Comparar vazão do banco com os vizinhos; ver posição da válvula; inspecionar bicos | Desentupir o header, conferir a válvula e compensar com bancos vizinhos no modelo |
| Erro de CT positivo (> +20 °C) | QUALIDADE / AI029 (0902) | Pouca água efetiva: banco entupido, aceleração do trem, água quente | Ver vazão por banco, T da água (AI024) e taxa (AI025) | Corrigir o banco; conferir parâmetros do modelo e a aceleração |
| Erro de CT negativo (< −20 °C) | QUALIDADE / AI029 (0901) | Excesso de água, válvula presa aberta, FDT baixa | Conferir válvulas abertas e FDT | Fechar o banco extra; revisar o setup |
| CT medida oscila sem queda de vazão | TERMICA / AI028 | Pirômetro de CT sujo, vapor ou água sobre a lente | Comparar com a CT de outra bobina; limpar a lente | Limpar o pirômetro, soprar ar de purga e aferir |
| Vazão total baixa | AGUA / AI021 | Falha de bomba, filtro saturado, nível baixo | Ver pressão dos headers e corrente das bombas | Trocar ou limpar o filtro; partir bomba reserva |
| Pressão do header intensivo fora da faixa | PRESSAO_FLUIDO / AI023 | Bomba desgastada, vazamento, válvula reguladora | Conferir bomba, manômetro e válvula | Ajustar ou reparar a bomba; corrigir o vazamento |
| Pressão do header laminar fora da faixa | PRESSAO_FLUIDO / AI022 | Nível da caixa elevada, adução obstruída | Ver nível e válvula de adução | Corrigir o nível; liberar a adução |
| Temperatura da água acima de 38 °C | AGUA / AI024 (0302) | Torre de resfriamento com baixo rendimento, recirculação quente | Ver ventiladores, bacia da torre e vazão de make-up | Limpar a torre e reduzir a carga térmica |
| Taxa de resfriamento fora da faixa | TERMICA / AI025, AI026 | Vazão e pressão fora do ideal; espessura fora do previsto | Cruzar com AI021–AI023 e a espessura da tira | Ajustar o padrão de bancos |
| Bobina com CT fora do alvo de ponta a ponta | QUALIDADE / AI029 | Modelo desajustado (coeficiente de troca de calor) | Ver erros de várias bobinas seguidas | Revisar o autoaprendizado do modelo |
| Bordas mais frias que o centro | QUALIDADE / AI029 | Água escorrendo sobre as bordas; máscaras ou side sprays desajustados | Ver perfil de CT ao longo da largura | Ajustar máscaras e side sprays |

Fluxo curto de diagnóstico:
1. Ver qual bit acendeu e qual tag disparou o alarme.
2. Comparar a vazão do banco com os vizinhos.
3. Conferir erro de CT e CT medida da bobina.
4. Verificar a pressão dos headers e a temperatura da água.
5. Só então suspeitar do pirômetro e do modelo.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

### 7.1 Propriedades mecânicas
- CT menor tende a dar grão mais fino e mais bainita. A resistência sobe.
- Estudos de laboratório em aços HSLA Ti-V mostram o máximo de resistência perto de 550 °C.
- No mesmo estudo, o melhor tamanho de precipitado apareceu perto de 650 °C.
- Em aços ao Nb, a contribuição do Nb em solução à resistência é maior perto de 600 °C.
- Por isso, o mesmo erro de CT tem efeito diferente conforme o aço. Em HSLA, ±20 °C já muda o limite de escoamento.
- O efeito da taxa de resfriamento é, em geral, maior que o da própria CT na microestrutura.

### 7.2 Bobinadeira e bobina
- CT alta em aços de baixo teor de Ar1 pode causar colapso da bobina (coil collapse) no resfriamento em ar.
- CT baixa aumenta a carga e o torque de bobinamento, pela maior resistência da tira.
- Variação de CT ao longo da bobina dá propriedades desiguais entre ponta, corpo e cauda.
- A bobina desclassificada vira sucata ou reprocesso.

### 7.3 Planicidade e geometria
- Resfriamento desigual entre centro e bordas gera tensões térmicas e transformação de fase em tempos distintos.
- O resultado são ondas de borda, ondas de centro ou camber.
- Um banco entupido de um lado causa assimetria na largura.
- O resfriamento por cima e por baixo desigual causa curvatura da tira (cobra).
- Água sobre a tira entre bancos aumenta o resfriamento lateral. Máscaras e side sprays reduzem esse efeito.

### 7.4 Superfície
- Água suja deixa marcas e pode manchar a superfície.
- O tempo de contato afeta a carepa que forma.

## 8. Manutenção preventiva e preditiva

Periodicidades abaixo são típicas e devem ser ajustadas ao histórico da usina.

| Atividade | Periodicidade típica |
|---|---|
| Inspeção visual dos jatos (padrão e alinhamento) | A cada turno ou diária |
| Limpeza do pirômetro de CT e do ar de purga | Diária a semanal |
| Verificar vazão por banco contra o setpoint | Diária (tendência no CLP) |
| Limpeza de bicos e U-tubes (flushing, escova) | Semanal a mensal, conforme carepa |
| Limpeza ou troca de filtros de água | Semanal a mensal |
| Aferição do pirômetro de CT com fonte de referência | Mensal a trimestral |
| Teste de abertura e fechamento das válvulas de banco | Mensal |
| Calibração dos medidores de vazão | Semestral a anual |
| Inspeção de headers, suportes e máscaras de borda | Em parada programada |
| Revisão da torre e das bombas | Conforme plano de manutenção rotativa |
| Revisão do modelo de CT (coeficientes, histórico de erro) | Mensal |

Manutenção preditiva:
- Acompanhar a tendência da vazão de cada banco. A queda lenta indica entupimento.
- Acompanhar o erro de CT médio por produto. Deriva indica problema de modelo ou pirômetro.
- Acompanhar a pressão dos headers e a corrente das bombas.
- Monitorar a temperatura da água e a eficiência da torre.
- O manual gerado resume: limpeza de headers e bicos; aferição do pirômetro de CT.

## 9. Segurança

- **Bloqueio (LOTO):** bloquear e etiquetar bombas, válvulas de adução e válvulas de banco antes de entrar na mesa.
- Despressurizar e drenar os headers antes de abrir bicos ou tubos.
- Confirmar que não há tira, cobble ou material quente sobre a mesa. A mesa só fica livre com a linha parada e bloqueada.
- Rolos da mesa podem partir. Bloquear os acionamentos.
- Risco térmico: superfícies, água e vapor quentes. Água acima de 38 °C ainda causa queimadura no tempo longo.
- Risco de vapor e de explosão de vapor se água cair sobre metal muito quente ou escória.
- Risco de queda e de escorregamento: piso molhado e passarelas sobre a mesa.
- Espaço confinado: fossos e canais sob a mesa exigem permissão de entrada e monitoramento de gás.
- Risco de ruído e de projeção de partículas na limpeza dos bicos. Usar EPI completo.
- Não limpar o pirômetro com a linha em operação.

## 10. Perguntas frequentes do operador

**1. O que a mesa de resfriamento faz?**
Ela esfria a tira com água até a temperatura de bobinamento, que define as propriedades do aço.

**2. Qual a CT alvo?**
Baixo carbono 600–680 °C, IF 680–740 °C e HSLA 500–600 °C na Usina exemplo.

**3. A vazão de um banco caiu para 150. O que isso significa?**
O alarme é abaixo de 160 m³/h. Provável banco entupido ou válvula travada. Compare com os bancos vizinhos.

**4. O erro de CT está em +25 °C. Devo parar?**
Ainda é aviso, pois o alarme é em 30 °C. Confira a vazão dos bancos, a água e o pirômetro e corrija logo.

**5. Por que a CT sobe quando o trem acelera?**
A tira passa mais rápido, fica menos tempo sob a água e esfria menos. O modelo deve abrir mais bancos.

**6. A temperatura da água subiu. E agora?**
O alarme é acima de 38 °C. Confira a torre de resfriamento e as bombas.

**7. O pirômetro de CT pode estar errado?**
Pode. Vapor e sujeira na lente dão leitura falsa. Se a vazão está normal e só a CT oscila, limpe o pirômetro.

**8. Uma CT errada estraga a bobina?**
Sim. A resistência e a ductilidade saem da especificação, e a bobina pode ser desclassificada.

## Fontes

- [Springer — Online control of coiling temperature on a run-out table (modelo e autoaprendizado)](https://link.springer.com/article/10.1016/S1006-706X(07)60050-8)
- [ISIJ International — Modelo de CT com resfriamento ultrarrápido e laminar](https://www.jstage.jst.go.jp/article/isijinternational/60/1/60_ISIJINT-2019-104/_html/-char/en)
- [Atlantis Press — Controle da temperatura de bobinamento: setup e feedforward](https://download.atlantis-press.com/article/25898787.pdf)
- [IFAC 2002 — Controle inteligente do resfriamento laminar](https://skoge.folk.ntnu.no/prost/proceedings/ifac2002/data/content/02526/2526.pdf)
- [Sādhanā — Otimização do resfriamento na mesa para evitar colapso de bobina](https://link.springer.com/content/pdf/10.1007/s12046-021-01629-w.pdf)
- [Univ. de Pretória — Efeito da CT em aço HSLA Ti-V (Gleeble)](https://repository.up.ac.za/items/9ff3ce0e-d7c8-4fd0-8a03-59bfa5f800d5/full)
- [Springer — Efeito da CT em aço microligado ao Nb](https://link.springer.com/content/pdf/10.1007/s11661-012-1270-x.pdf)
- [Primetals — Seção de resfriamento intensivo (Power Cooling)](https://www.primetals.com/en/news/primetals-technologies-extends-intensive-cooling-section-on-thyssenkrupp-hot-strip-mill/)
- [Patente US6178768 — Dispositivo de resfriamento de tira com jato laminar](https://patents.google.com/patent/US6178768)
- [Spray Systems — Strip cooling (headers e bicos para mesa)](https://spray.com/applications/strip-cooling)
- [USPTO US4497180 — Resfriamento de tira e fluxo de água para as bordas](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4497180)
