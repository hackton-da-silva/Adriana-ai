# TES-01 — Tesoura de pontas (crop shear) — documentação de referência

> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

- A tesoura de pontas fica entre o laminador desbastador e o acabador, na entrada do acabamento (Linha 3 da Usina exemplo).
- Ela corta a cabeça (ponta dianteira) e a cauda (ponta traseira) do esboço (transfer bar).
- O objetivo da cabeça é entregar uma ponta reta e quadrada, que enfia bem no primeira cadeira do acabador.
- O objetivo da cauda é remover língua, rabo de peixe (fishtail) e bordas irregulares, que podem quebrar e danificar os cilindros.
- Cabeça ruim aumenta o risco de cobble (emboloamento da tira no acabador).
- Todo corte a mais vira sucata e reduz o rendimento metálico. Por isso o comprimento do desponte é otimizado.
- Na Usina exemplo o desponte normal é de 100 a 500 mm, com ideal de 300 mm (AI003).
- Fabricantes de mercado descrevem a tesoura de tambor entre desbastador e acabador, em geral com otimização do comprimento de corte para reduzir perdas.

## 2. Princípio de funcionamento

### 2.1 Tesoura de tambor (drum shear)
- Dois tambores giram em sentidos opostos, um acima e outro abaixo da linha de passe.
- Cada tambor leva uma faca (lâmina) fixada na periferia.
- A cada volta, as duas facas se encontram e cortam o esboço em uma passada.
- As facas descrevem um arco. Por isso o corte é levemente curvo, o que favorece o enfiamento da cabeça.
- O esboço passa continuamente. O corte é feito "em voo" (flying shear), sem parar o material.

### 2.2 Velocidade diferencial e sincronismo
- A velocidade periférica das facas é ajustada em relação à velocidade do esboço.
- Uma pequena diferença evita que o material seja puxado ou comprimido durante o corte.
- O acionamento mantém o tambor em espera (posição de repouso) e acelera para encontrar o esboço no ponto de corte.
- O sincronismo entre as duas facas (fase dos tambores) define se o corte é limpo.
- O ponto de corte é calculado a partir da posição da ponta, medida por detector de metal quente e tracking.

### 2.3 Cabeça e cauda
- Cabeça: pode ser cortada com esboço parado ou em movimento.
- Cauda: tem de ser cortada em movimento, porque a cabeça já está no acabador.
- O detector de metal quente indica presença ou ausência de material e separa corte de cabeça do corte de cauda.

### 2.4 Otimização do desponte (crop optimization)
- Uma câmera ou detector de forma mede o contorno da cabeça e da cauda.
- O software calcula o ponto de corte ideal: remove só o necessário para eliminar língua ou rabo de peixe.
- A tendência de mercado é reduzir o desponte de 200–300 mm para algo entre 30 e 100 mm, o que exige corte muito preciso.
- Fornecedores citam ganho de rendimento da ordem de décimos de ponto percentual. Trate como valor de fabricante.
- Um erro entre a posição-alvo e o ponto onde a faca realmente toca o esboço pode causar corte errado (cutting miss).

### 2.5 Tesoura de manivela (crank shear)
- É a alternativa mecânica à de tambor.
- É usada para esboços mais grossos ou aços de alta resistência.
- A Usina exemplo usa tambor (drum shear rotativa, velocidade diferencial).

## 3. Componentes principais

| Componente | Função |
|---|---|
| Tambores superior e inferior | Suportam as facas e giram em sentidos opostos |
| Facas (lâminas) | Cortam o esboço. Em aço-ferramenta endurecido, com mais de um fio de corte |
| Sistema de ajuste de folga | Regula o espaço lateral entre as facas e a sobreposição (lapping) |
| Acionamento (motor + redutor) | Aceleração, sincronismo e esforço de corte |
| Engrenagens de sincronismo | Mantêm a fase entre os tambores |
| Mancais e lubrificação | Suportam o esforço de corte |
| Detector de metal quente (HMD) | Detecta presença do esboço e dispara o ciclo |
| Câmera / detector de forma | Mede o contorno da ponta para otimização |
| Mesa de entrada e saída, guias | Posicionam o esboço e conduzem a sucata |
| Calha de sucata | Evacua o desponte para a caçamba |
| Descarepador secundário | Fica próximo, na entrada do acabador |
| CLP-TES-01 | Controla ciclo, posição das lâminas e alarmes |

- Detalhe de projeto: algumas tesouras deslocam as facas lateralmente para variar a região de contato. Isso distribui o desgaste, pois a mesma parte da faca corta sempre a borda do esboço.

## 4. Parâmetros típicos de operação

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| Ciclos de corte | Depende do ritmo da linha (2 cortes por esboço) | 40–70 cortes/h (ideal 55) | AI001 |
| Tempo de corte | Poucas centenas de ms por corte | 150–300 ms (ideal 225) | AI002 |
| Comprimento do desponte | 200–300 mm clássico; 30–100 mm com otimização | 100–500 mm (ideal 300) | AI003 |
| Desvio de posição das lâminas | Folga da ordem de poucos % da espessura; sem faixa pública única | 0–2 mm (ideal 0; alarme acima de 3 mm) | AI004 |
| Corrente do motor | 40–85 % da nominal em operação normal | 40–85 % nominal (ideal 62,5) | AI005 |
| Espessura do esboço | 30–60 mm típico | 30–45 mm | sem tag |
| Velocidade do esboço | 0,5–2 m/s no corte | 0,5–2 m/s | sem tag |
| Esforço de corte | Centenas de toneladas | cerca de 300 t | sem tag |

- Divergência: o desponte da indústria pode chegar a 30–100 mm com otimização. Na Usina exemplo o mínimo é 100 mm.
- Não achei fonte pública com tolerância numérica de folga para tesouras de pontas. A faixa de AI004 vem da simulação.

## 5. Instrumentação e sinais do CLP

CLP: CLP-TES-01. Alarmes seguem o código AAKK (AA = bit da área, KK = tipo), como no manual do CLP.

| Tag | Variável | Unidade | Área (bit) | O que indica |
|---|---|---|---|---|
| AI001 | Ciclos de corte (`ciclos_corte`) | cortes/h | MATERIAL_FLUXO (12) | Ritmo de corte e fluxo de esboços |
| AI002 | Tempo de corte (`tempo_corte`) | ms | ACIONAMENTO (0) | Duração do ciclo. Sobe com lâmina gasta ou acionamento fraco |
| AI003 | Comprimento do desponte (`comprimento_desponte`) | mm | POSICAO_GEOMETRIA (7) | Quanto material foi cortado |
| AI004 | Desvio de posição das lâminas (`desvio_posicao_laminas`) | mm | POSICAO_GEOMETRIA (7) | Erro de posição ou folga das facas |
| AI005 | Corrente do motor (`corrente_motor`) | % nominal | ACIONAMENTO (0) | Carga do acionamento durante o corte |

- Só AI004 tem limite de alarme (acima de 3 mm). Os outros geram aviso ao sair da faixa normal.
- Aviso de AI004 acima de 2 mm: código 0712. Alarme acima de 3 mm: código 0702.
- Aviso de AI005 acima de 85 %: código 0012. Aviso de AI002 acima de 300 ms: 0012.
- Aviso de AI001 abaixo de 40 ou acima de 70 cortes/h: 1211 ou 1212.
- Lanterna: amarela para aviso, vermelha para alarme, azul para manutenção requerida.
- No manual gerado, as três áreas (MATERIAL_FLUXO, ACIONAMENTO, POSICAO_GEOMETRIA) têm a mesma causa listada: lâmina gasta ou corte fora de posição.
- Por isso é preciso cruzar as tags para separar o caso.

Como separar as causas com as tags:
- AI004 alto e AI003 alto: posição das facas ou ajuste do corte.
- AI002 alto e AI005 alto: lâmina gasta ou folga excessiva (esforço maior e corte mais lento).
- AI001 fora da faixa: problema de fluxo, e não da tesoura em si.

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Desponte acima de 500 mm | POSICAO_GEOMETRIA / AI003 | Ajuste do ponto de corte errado, otimizador com falha ou erro de tracking | Comparar AI003 com o valor calculado pelo otimizador. Ver sinal do detector de forma | Corrigir o ponto de corte. Recalibrar tracking e detector |
| Desvio de posição das lâminas alto | POSICAO_GEOMETRIA / AI004 | Folga mal ajustada, desgaste do ajuste, fase dos tambores deslocada | Medir folga e sobreposição com a tesoura parada. Conferir referência de posição | Reajustar folga. Ressincronizar tambores |
| Alarme 0702 (AI004 acima de 3 mm) | POSICAO_GEOMETRIA / AI004 | Facas muito deslocadas ou gastas | Inspeção visual das facas e do ajuste | Parar para ajuste ou troca |
| Corte lento (tempo de corte alto) | ACIONAMENTO / AI002 | Lâmina cega, folga grande, acionamento com perda de torque | Ver AI005 junto. Inspecionar fio da faca | Girar ou trocar facas |
| Corrente do motor alta | ACIONAMENTO / AI005 | Esforço de corte alto por faca gasta, esboço frio ou grosso | Ver temperatura do esboço (área TERMICA de outras máquinas) e espessura | Trocar facas. Avisar a montante se esboço estiver frio |
| Corte incompleto ou rasgado | ACIONAMENTO e POSICAO_GEOMETRIA | Folga excessiva ou pouca sobreposição | Inspecionar a ponta cortada e a faca | Ajustar folga. Trocar facas |
| Rebarba em forma de agulha na ponta | POSICAO_GEOMETRIA / AI004 | Folga larga com faca gasta | Olhar a borda cortada | Trocar facas, ajustar folga. Rebarba pode colar nos cilindros do acabador |
| Cabeça com língua ou forma ruim após o corte | POSICAO_GEOMETRIA / AI003 | Desponte curto demais ou otimizador errado | Ver imagem da câmera | Aumentar o desponte. Rever o otimizador |
| Ritmo de cortes fora da faixa | MATERIAL_FLUXO / AI001 | Linha parada, esboços atrasados ou falha de tracking | Ver status da linha e do desbastador | Normalizar o fluxo a montante |
| Corte feito fora do tempo | MATERIAL_FLUXO e ACIONAMENTO | Erro entre posição-alvo e contato da faca | Verificar sinais do detector de metal quente e do encoder | Recalibrar sensores e sincronismo |
| Esboço não cortado e travado | MATERIAL_FLUXO | Falha de ciclo ou emergência | Ver DI de falha e estado PackML (Aborted) | Liberar com bloqueio e retomar |

Roteiro rápido para o agente:
1. Ver qual bit acendeu (12, 0 ou 7).
2. Ler a tag que saiu da faixa.
3. Cruzar AI002, AI004 e AI005 para decidir entre lâmina gasta e fora de posição.
4. Confirmar no histórico quando o desvio começou.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

- Cabeça mal cortada aumenta o risco de cobble no primeira cadeira do acabador.
- Cobble para a linha e danifica cilindros, guias e mesa de saída.
- Cauda com rabo de peixe pode quebrar e danificar os cilindros do acabador.
- Rebarba em forma de agulha pode ser laminada para dentro da tira ou grudar nos cilindros, e gerar marca superficial.
- Desponte longo reduz o rendimento metálico. Cada centímetro a mais vira sucata.
- Desponte curto demais deixa língua ou largura irregular, com risco de enfiamento ruim.
- Corte fora de posição pode gerar ponta assimétrica, que contribui para camber e desvio lateral na entrada do acabador.
- Corte rasgado ou fora de posição: desponte longo e menor rendimento, como descreve o manual da máquina.
- Sucata de ponta ruim pode gerar parada na calha, que trava o fluxo.

## 8. Manutenção preventiva e preditiva

| Item | Periodicidade típica | Observação |
|---|---|---|
| Girar ou trocar facas | 2–6 semanas na Usina exemplo | Valor do manual da máquina. Depende do tonelado cortado e do aço |
| Medir folga e sobreposição | A cada troca de facas | Registrar para acompanhar o desgaste |
| Conferir fixação das facas | Em toda parada programada | Parafusos e calços |
| Inspeção do fio e de trincas | Semanal | Procurar lascas, microtrincas, rebarba |
| Lubrificação de mancais e engrenagens | Conforme plano, em geral semanal | Ver pontos de graxa |
| Alinhamento e fase dos tambores | Mensal ou após troca | Sincronismo |
| Calibração do detector de metal quente e câmera | Mensal | Garante ponto de corte correto |
| Inspeção do acionamento (motor, redutor) | Trimestral | Termografia e análise de óleo |

Manutenção preditiva:
- Acompanhar a tendência de AI002 (tempo de corte) e AI005 (corrente). A subida lenta indica desgaste da faca.
- Acompanhar AI004. Deriva gradual indica desgaste do ajuste.
- Registrar o tonelado ou número de cortes por jogo de facas para prever a troca.
- Girar a faca para usar outro fio antes de o fio atual ficar cego.
- Vibração do redutor e dos mancais ajuda a achar falha mecânica cedo.

## 9. Segurança

- Bloqueio e etiquetagem (LOTO): isolar o motor, o acionamento e a energia armazenada antes de qualquer intervenção. Seguir a NR-10 (elétrica) e a NR-12 (máquinas).
- Parar os tambores e travar mecanicamente a posição antes de entrar na área das facas.
- Facas são afiadas e pesadas. Usar içamento adequado na troca e luvas anticorte.
- O esforço de corte é alto (cerca de 300 t). Nunca entrar na zona de corte com o ciclo habilitado.
- Esboço quente (cerca de 1000 °C): risco de queimadura e radiação térmica. Manter distância.
- Calha de sucata: sucata quente pode travar e se mover sozinha. Esperar resfriar.
- Intertravamentos de segurança (bit 10, SEGURANCA) não devem ser anulados.
- Confirmar a ausência de esboço na linha antes de liberar o bloqueio.
- Fechar as proteções e testar o ciclo a vazio antes de voltar a produzir.

## 10. Perguntas frequentes do operador

**1. A tesoura acendeu amarela. O que olho primeiro?**
Veja qual tag saiu da faixa. Se foi o desvio das lâminas, a posição está errada. Se foi tempo de corte ou corrente, a lâmina pode estar gasta.

**2. Qual o desponte normal?**
De 100 a 500 milímetros, com ideal em 300.

**3. Quando troco as facas?**
Em geral de 2 a 6 semanas. Troque antes se o tempo de corte e a corrente subirem juntos.

**4. Por que cortar menos ponta é melhor?**
Porque cada milímetro cortado é sucata. Mas cortar de menos deixa língua ou rabo de peixe, e isso pode causar cobble.

**5. A corrente do motor subiu. É a tesoura?**
Pode ser faca gasta ou esboço frio ou grosso. Confira a temperatura do esboço e a espessura antes de parar a máquina.

**6. Quando o desvio das lâminas vira alarme?**
Quando passa de 3 milímetros. O aviso começa acima de 2 milímetros.

**7. A ponta saiu com rebarba. E agora?**
Rebarba vem de folga grande ou faca gasta. Ela pode grudar nos cilindros do acabador. Ajuste a folga ou troque as facas.

**8. Posso entrar para olhar as facas com a máquina parada?**
Só com bloqueio LOTO aplicado, tambores travados e sem esboço na linha.

## Fontes

- [Danieli Automation — Q-Crop (otimização de desponte por câmera)](https://www.dca.it/media/download/q-crop.pdf)
- [SMS group — Hot strip mills (tesoura de tambor e de manivela, otimização do desponte)](https://www.sms-group.com/en-es/hot-strip-mills-new62fcbed8f10b3564707974/download)
- [US 4527243 — Crop shear control (patente: corte de cabeça e cauda, controle por forma)](https://patents.google.com/patent/US4527243)
- [US 4112798 — Drum type flying shear (patente: folga, sobreposição e rebarba)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4112798)
- [US 5260541 — Crop shear apparatus and crop shear equipment (patente: deslocamento lateral das facas, desgaste)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5260541)
- [Primetals Technologies — Steel strip width camera (câmera de largura com otimização de desponte)](https://www.primetals.com/en/portfolio/solutions/hot-rolling/hot-strip-mills/automation/steel-strip-width-camera/)
- [SPIE 1993 — Research on profile tracing and recognition for hot strip ends](https://journals.spiedigitallibrary.org/conference-proceedings-of-spie/2101/0000/Research-on-profile-tracing-and-recognition-for-hot-strip-ends/10.1117/12.156371.full)
- [US 3386321 — Automatic control system for hot strip mill crop shear (patente: rabo de peixe)](https://patents.google.com/patent/US3386321A/en)
