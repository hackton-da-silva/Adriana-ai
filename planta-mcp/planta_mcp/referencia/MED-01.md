# MED-01 — Medidores na saída do acabador — documentação de referência

> Usina exemplo (dados fictícios). Conteúdo técnico de referência baseado em fontes públicas; valores numéricos da planta vêm da simulação.

## 1. Função no processo

Os medidores ficam logo após a última cadeira do trem acabador, antes da mesa de resfriamento (run-out table). Eles são os "olhos" do nível 1 e do nível 2 na saída do acabador.

O conjunto mede, na tira que sai a cerca de 10 a 20 m/s:

- espessura no centro (sinal principal do AGC);
- perfil transversal de espessura: coroa (C40), cunha e queda de borda;
- largura (e sobrelargura em relação ao alvo);
- planicidade (calculada a partir do perfil);
- temperatura de acabamento (FDT) e gradiente borda–centro.

Para que serve cada medida:

- **Espessura:** fecha a malha do monitor AGC e valida o modelo de setup.
- **Perfil e planicidade:** alimentam o controle de bending, shifting e resfriamento de cilindros.
- **FDT:** alimenta o controle da mesa de resfriamento e a previsão da temperatura de bobinamento.
- **Largura:** valida o modelo de espalhamento e a eficácia do controle de largura.

Na Usina exemplo, o equipamento é um conjunto multifunção de referência de mercado: raio-X multicanal (tipo IMS XR SMC), medidores tipo Thermo Fisher RM 215 HM / SIPRO e pirômetros tipo AMETEK Land SPOT+. Fabricante aqui é só referência, não é a identidade da planta.

## 2. Princípio de funcionamento

### 2.1 Espessura por raio-X
- Um tubo de raio-X emite um feixe que atravessa a tira. Um detector (câmara de ionização ou cintilador) mede a intensidade que passa.
- A atenuação cai de forma exponencial com a espessura (lei de Beer–Lambert). O sistema inverte essa relação para obter a espessura.
- A atenuação depende também da liga. Por isso há um coeficiente de compensação de liga, informado pelo nível 2 para cada tira.
- Temperatura e vapor no caminho também influenciam. Há correção por temperatura e proteção física do feixe.
- O raio-X tem resposta rápida (milissegundos), o que permite filtrar o ruído e ainda atender ao AGC.
- Alternativa: fonte de isótopo (por exemplo Am-241 ou Cs-137). Ela é mais simples e não tem alta tensão, mas é menos rápida e exige gestão de fonte radioativa.

### 2.2 Perfil, coroa e cunha
- Um medidor de perfil simultâneo usa duas fontes em C-frame. Os dois ângulos de visão são combinados com o ângulo da tira. Assim o perfil não depende da posição nem da inclinação da tira.
- Coroa C40 é a espessura no centro menos a espessura a 40 mm da borda. Cunha é a diferença de espessura entre os dois lados.
- Queda de borda (edge drop) é o afinamento perto da borda.
- A atualização do perfil é da ordem de dezenas de ms. A resolução transversal típica é de cerca de 5 mm.

### 2.3 Largura
- Câmeras ópticas (estéreo ou de varredura) veem as duas bordas, que brilham por causa do calor.
- A largura vem da distância entre bordas, corrigida pela altura da tira na mesa.

### 2.4 Planicidade
- A planicidade não é medida diretamente nessa posição. Ela é calculada a partir do perfil de alta resolução, comparando o comprimento relativo das fibras da tira.
- A unidade I-unit vale 0,01 % de diferença de comprimento. Ou seja, 1 % de diferença equivale a 1000 I-units.

### 2.5 Temperatura de acabamento (FDT)
- O pirômetro mede a radiação infravermelha emitida pela superfície. A temperatura sai da lei de Planck, usando a emissividade ajustada.
- Pirômetro de duas cores (razão entre dois comprimentos de onda) reduz a influência de água, vapor e variação de emissividade.
- Um pirômetro de varredura mede o perfil transversal. As bordas são mais frias que o centro. Essa leitura também corrige a atenuação de raio-X por temperatura.

### 2.6 Uso em malha fechada
- **Monitor AGC:** usa o desvio de espessura medido na saída para corrigir o gap ou a velocidade da última cadeira (ou das últimas).
- Existe um tempo morto, porque o medidor fica a alguma distância das cadeiras e a tira precisa percorrer esse trecho. O tempo morto limita a velocidade da malha. Compensadores de tempo morto (Smith predictor, PI com compensação) são comuns.
- **Gaugemeter AGC** (estimativa pela força e pelo gap) não tem esse atraso, mas depende de modelo. O medidor de raio-X corrige a deriva desse modelo.
- Por isso um medidor descalibrado leva o AGC a corrigir um erro que não existe. Esse é o risco central desta máquina.

## 3. Componentes principais

| Componente | Função |
|---|---|
| Tubo de raio-X e gerador de alta tensão | Emite o feixe; tensão e corrente são monitoradas |
| Detectores (câmara de ionização / cintilador) | Medem a intensidade transmitida em um ou vários canais |
| C-frame com camisa refrigerada a água | Estrutura que sustenta fonte e detector em torno da tira |
| Cabeçote (sensor) com purga de ar | Protege a janela contra vapor, poeira e respingos |
| Obturador (shutter) de segurança | Bloqueia o feixe quando o medidor sai da linha |
| Padrões de calibração (cunhas, folhas) e câmara de referência | Calibração diária e verificação de ganho |
| Câmeras de largura | Medem a largura e a posição lateral da tira |
| Pirômetros (um ou de varredura) com lente e purga | Medem a FDT e o perfil de temperatura |
| Unidade de processamento (computador do medidor) | Filtra, compensa liga/temperatura e calcula perfil e planicidade |
| Interface com CLP e nível 2 | Envia sinais ao AGC e recebe dados da tira (liga, alvo) |

## 4. Parâmetros típicos de operação

| Parâmetro | Faixa típica na indústria | Valor/faixa na Usina exemplo | Tag |
|---|---|---|---|
| Desvio de espessura (amostra) | Tolerância de poucos % da espessura; em tiras de 2 a 4 mm, cerca de ±30 a ±60 µm | Normal −50 a 50 µm (ideal 0) | AI001 |
| Amplitude de oscilação da espessura | Abaixo de cerca de 30 µm em regime | Normal 0 a 30 µm; alarme acima de 50 µm | AI002 |
| Coroa C40 | Dezenas de µm (cerca de 20 a 80 µm, conforme largura e espessura) | Normal 20 a 80 µm (ideal 50) | AI003 |
| Cunha | Poucas dezenas de µm | Normal −20 a 20 µm (ideal 0) | AI004 |
| Sobrelargura | Alvo de largura mais folga para cortes | Normal 0 a 15 mm (ideal 7,5) | AI005 |
| Planicidade | Abaixo de cerca de 20 I-units em produto comum | Normal 0 a 20 I-units; alarme acima de 30 | AI006 |
| Temperatura de acabamento (FDT) | Cerca de 820 a 920 °C, conforme o aço | Normal 850 a 920 °C (ideal 885) | AI007 |
| Gradiente de temperatura borda–centro | Poucas dezenas de °C | Normal 0 a 20 °C; alarme acima de 30 °C | AI008 |
| Tensão do tubo de raio-X | Faixa do fabricante (dezenas a 150 kV) | Normal 140 a 160 kV (ideal 150) | AI009 |
| Corrente do tubo | Poucos a dezenas de mA | Normal 5 a 15 mA (ideal 10) | AI010 |
| Temperatura do cabeçote | Mantida baixa pela refrigeração | Normal 20 a 40 °C (ideal 30) | AI011 |
| Desvio desde a última calibração | Baixo; recalibração quando passa de poucos µm | Normal 0 a 10 µm; alarme acima de 20 µm | AI012 |

Outros valores de referência de fabricantes:

- Faixa de temperatura de tira do medidor de perfil: cerca de 600 a 1200 °C.
- Largura de tira: cerca de 0,5 a 2,8 m.
- Atualização do centro: milissegundos.
- Espessura máxima do medidor de centro: da ordem de dezenas de mm.

## 5. Instrumentação e sinais do CLP

CLP: CLP-MED-01, Linha 3 (Acabamento). As lanternas seguem a IEC 60073 e as palavras de falha e aviso usam os bits do manual do CLP.

### Área QUALIDADE (bit 9)
- AI001 desvio de espessura, AI002 oscilação, AI003 coroa C40, AI004 cunha, AI005 sobrelargura, AI006 planicidade.
- AI002 acima de 50 µm gera alarme (código 0902). AI006 acima de 30 I-units gera alarme (0902).
- Fora da faixa normal, mas dentro do limite, gera aviso (0912 ou 0911).

### Área TERMICA (bit 4)
- AI007 FDT e AI008 gradiente borda–centro.
- AI008 acima de 30 °C gera alarme (0402). FDT fora de 850 a 920 °C gera aviso (0411 ou 0412).

### Área INSTRUMENTACAO (bit 8)
- AI009 tensão do tubo, AI010 corrente do tubo, AI011 temperatura do cabeçote, AI012 desvio de calibração.
- AI012 acima de 20 µm gera alarme (0802). Acima de 10 µm gera aviso (0812).

Como ler: os bits 9, 4 e 8 acesos juntos indicam a mesma raiz. Se a área INSTRUMENTACAO está acesa, desconfie do medidor antes de culpar o processo. Se só QUALIDADE ou TERMICA acende e a saúde do medidor está normal, o problema provavelmente é real, no processo.

Os sinais de saúde (AI009, AI010, AI011) são marcados [E] no manual gerado. Servem para diagnóstico indireto, não para controle.

## 6. Modos de falha e diagnóstico

| Sintoma | Área do CLP / tag | Causa provável | Verificação | Ação |
|---|---|---|---|---|
| Desvio de espessura com deriva lenta, sem mudança de força ou gap | INSTRUMENTACAO (bit 8) / AI012, AI001 | Descalibração do medidor (deriva do ganho, envelhecimento do tubo ou do detector) | Comparar AI012 com o histórico; checar liga informada; medir padrões | Calibrar com os padrões; validar com amostra medida fora da linha |
| Oscilação de espessura crescente | QUALIDADE (bit 9) / AI002, AI001 | Chatter ou looper instável (F4 a F6); AGC no limite | Cruzar com vibração e looper; ver se a oscilação segue a rotação de cilindros | Investigar vibração das cadeiras e dos loopers; rever ganhos do AGC |
| Coroa ou cunha fora da faixa | QUALIDADE / AI003, AI004 | Setup de coroa/bending errado; desgaste de cilindro; desalinhamento | Comparar com a campanha e com o setup; ver simetria entre lados | Revisar o setup e a campanha; trocar cilindro se preciso |
| Sobrelargura fora da faixa | QUALIDADE / AI005 | Erro de modelo de largura ou de controle lateral a montante | Comparar com o medidor de largura do desbaste | Ajustar o modelo; checar guias e esboço |
| Planicidade alta | QUALIDADE / AI006 | Perfil inadequado, desgaste de cilindro, resfriamento desigual | Cruzar com coroa, cunha e gradiente de temperatura | Revisar o setup de bending e o resfriamento |
| FDT abaixo do alvo | TERMICA (bit 4) / AI007 | Placa ou esboço frio a montante; velocidade baixa | Ver temperatura de saída do forno e do desbaste | Investigar o forno de origem e o desbaste |
| FDT baixa só no pirômetro, com o processo normal | TERMICA / AI007; INSTRUMENTACAO | Vapor ou água na linha de visada; lente suja; emissividade errada | Comparar com pirômetro vizinho; olhar a lente; checar purga de ar | Limpar a lente; revisar purga e posição; recalibrar |
| Gradiente borda–centro alto | TERMICA / AI008 | Borda fria (placa), cobertura de borda, resfriamento irregular | Ver perfil de varredura e histórico do forno | Investigar o aquecimento e o desbaste; checar o pirômetro de varredura |
| Tensão ou corrente do tubo fora da faixa | INSTRUMENTACAO / AI009, AI010 | Tubo envelhecendo, gerador instável | Ver tendência; comparar com ganho do detector | Programar a troca do tubo; recalibrar |
| Cabeçote quente | INSTRUMENTACAO / AI011 | Falha de água de refrigeração da camisa; vazão baixa | Ver vazão e temperatura da água da camisa | Restabelecer a refrigeração; tirar o medidor da linha se subir |
| Espessura e FDT "ruins" ao mesmo tempo | QUALIDADE + TERMICA | Placa fria a montante (espessura e FDT mudam juntas) | Ver o forno e o desbaste | Tratar a causa a montante |

Dicas de diagnóstico:
- Se AI001 e AI012 crescem juntos e a força de laminação e o gap estão estáveis, suspeite do medidor.
- Se a oscilação tem período ligado à rotação dos cilindros, suspeite de excentricidade ou de chatter.
- Vapor e água atenuam a radiação do pirômetro, e a leitura sai mais baixa que a real. O pirômetro de duas cores é bem menos sensível a isso.
- Raio-X é pouco afetado por vapor, mas o vapor pesado ou o acúmulo de água na janela podem alterar a leitura. Mantenha a purga e a camisa em dia.

## 7. Efeito nos equipamentos a jusante e na qualidade da tira

- **AGC e cadeiras:** um medidor descalibrado leva o AGC a corrigir errado. Na simulação, a deriva é de 10 a 30 µm por semana sem mudança de força ou gap. A tira sai fora da tolerância, mesmo com o medidor "dizendo" que está certa.
- **Monitor AGC:** o tempo morto do medidor limita a rapidez. Ruído ou erro de medição entra na malha e é amplificado.
- **Mesa de resfriamento e bobinadeiras:** a FDT errada leva o modelo a errar a vazão de água. A temperatura de bobinamento sai fora do alvo.
- **Propriedades mecânicas:** FDT fora do alvo muda o tamanho de grão e a resistência (aços de alta resistência e microligados são os mais sensíveis).
- **Perfil e planicidade:** coroa e cunha fora levam a tiras onduladas, em borda ou em centro, e a problemas de bobina (telescopia, desvio lateral).
- **Cliente:** erros de espessura e largura geram reclamação, retrabalho e desclassificação.
- **Laminação a frio e acabamento:** perfil ruim na saída do acabador se propaga para a decapagem e a laminação a frio.

## 8. Manutenção preventiva e preditiva

| Item | Periodicidade típica | Observação |
|---|---|---|
| Calibração com padrões (raio-X) | Diária (Usina exemplo) | Registrar AI012 antes e depois |
| Limpeza das lentes dos pirômetros | Por turno (Usina exemplo) | Checar também a purga de ar |
| Verificação das janelas e purgas do cabeçote | Por turno | Água ou óleo na janela gera erro |
| Inspeção da água da camisa (vazão, temperatura) | Semanal | Alarme de AI011 como apoio |
| Verificação cruzada com amostra medida fora da linha | Semanal ou a cada campanha | Confirma ganho e compensação de liga |
| Troca preventiva do tubo de raio-X | Conforme horas de uso e tendência de AI009/AI010 | Planejar em parada programada |
| Inspeção do shutter e dos intertravamentos | Mensal | Teste funcional |
| Verificação das câmeras de largura (alinhamento, vidro) | Mensal | Calibrar com padrão geométrico |
| Calibração dos pirômetros contra corpo negro | Trimestral a semestral | Checar emissividade ajustada |

Manutenção preditiva:

- Acompanhe a tendência de AI012, AI009, AI010 e AI011 por semana.
- Uma subida lenta de corrente com queda de ganho aponta para fim de vida do tubo.
- Compare o medidor com amostras fora da linha. Uma tendência sistemática indica erro de liga ou de ganho.

## 9. Segurança (bloqueio/LOTO, riscos específicos)

- **Radiação ionizante:** o tubo de raio-X só emite com alta tensão. Faça bloqueio e etiquetagem (LOTO) do gerador antes de qualquer intervenção no cabeçote. Confirme o shutter fechado.
- Se a máquina usar fonte de isótopo, só pessoal autorizado manuseia a fonte. Siga o plano de proteção radiológica e os procedimentos da autoridade competente.
- **Alta tensão:** o gerador trabalha na faixa de 140 a 160 kV. Descarregue e verifique ausência de tensão.
- **Calor:** o C-frame fica perto da tira a mais de 800 °C. Espere o resfriamento e use EPI adequado.
- **Água:** a camisa refrigerada e a mesa têm água quente e vapor. Atenção a vazamento perto de partes elétricas.
- **Movimento do C-frame:** o medidor pode sair da linha automaticamente. Bloqueie a energia e o ar antes de entrar na área.
- **Laser e óptica:** alguns pirômetros usam mira laser. Evite olhar para o feixe.
- **Linha em operação:** não entre na área sobre a mesa com a tira passando. Siga as regras gerais de acesso do acabador.

## 10. Perguntas frequentes do operador

1. **O medidor mostra desvio de espessura, mas a força e o gap não mudaram. O que é?**
   Provavelmente é deriva do medidor. Veja o desvio de calibração. Se estiver alto, calibre com os padrões.

2. **Qual o limite do desvio de calibração?**
   Normal até 10 µm. Acima de 20 µm vira alarme de instrumentação.

3. **A FDT caiu de repente. É o forno?**
   Pode ser. Compare com o pirômetro vizinho e olhe a lente. Vapor ou lente suja fazem a leitura cair sem o processo mudar.

4. **Por que o vapor atrapalha o pirômetro?**
   O vapor e a água absorvem e espalham a radiação infravermelha. O pirômetro lê menos do que a tira realmente emite.

5. **O que significa coroa C40 de 50 µm?**
   É a espessura no centro menos a espessura a 40 mm da borda. Na simulação, 50 µm é o ideal e a faixa normal vai de 20 a 80.

6. **Quanto é planicidade de 20 I-units?**
   São 0,2 % de diferença de comprimento entre fibras. Na simulação, acima de 30 I-units dá alarme.

7. **Com que frequência calibra o raio-X?**
   Todo dia com os padrões. Se a deriva subir rápido, calibre antes.

8. **O AGC pode estar errado por causa do medidor?**
   Sim. O AGC corrige o que o medidor vê. Se o medidor erra, o AGC leva a tira para fora da tolerância.

## Fontes

- [Thermo Fisher — SIPRO, folheto do medidor de perfil simultâneo](https://assets.thermofisher.com/TFS-Assets/CAD/brochures/SIPRO_BR.pdf)
- [Thermo Fisher — Gauges for Hot Strip Mills (catálogo SIPRO)](https://www.thermofisher.com/order/catalog/product/SIPRO)
- [Thermo Fisher — RM 215 HM thickness gauge (folheto)](https://assets.thermofisher.com/TFS-Assets/CAD/brochures/rm-215-hm-thickness-gauge.pdf)
- [Thermo Fisher — A practical guide to metals gauging systems](https://assets.thermofisher.com/TFS-Assets/CAD/Scientific-Resources/metals-gauging-systems-ebook.pdf)
- [Primetals Technologies — Steel strip width camera](https://www.primetals.com/en/portfolio/solutions/hot-rolling/hot-strip-mills/automation/steel-strip-width-camera/)
- [Nippon Steel — relatório técnico sobre pirômetros na mesa de resfriamento](https://www.nipponsteel.com/en/tech/report/nssmc/pdf/111-04.pdf)
- [US 3,759,102 — Pirômetro com interferência de vapor (Google Patents)](https://patents.google.com/patent/US3759102A/en)
- [ORNL — Infrared thermometry em processamento de materiais a alta temperatura: efeito de água líquida e vapor](https://www.ornl.gov/publication/infrared-thermometry-high-temperature-materials-processing-influence-liquid-water-and)
- [US 4,088,886 — Radiation thickness gauge for sheet material (Google Patents)](https://patents.google.com/patent/US4088886)
- [JP 2706330 B2 — Correção de medidor de espessura por radiação (Google Patents)](https://patents.google.com/patent/JP2706330B2/en)
- [Univ. of Wollongong — Expert PI controller com compensação de tempo morto para monitor AGC](https://ro.uow.edu.au/articles/journal_contribution/An_expert_PI_controller_with_dead_time_compensation_of_monitor_AGC_in_hot_strip_mill/27761790)
- [Salzgitter Flachstahl — Profile Analysis on the Hot-Rolled Wide Strip Mill (C40, C100)](https://www.salzgitter-flachstahl.de/en/news/details/profile-analysis-on-the-hot-rolled-wide-strip-mill-26864.html)
- [The Fabricator — Controlling flat rolled shape (I-unit)](https://www.thefabricator.com/thefabricator/article/bending/controlling-flat-rolled-shape)
