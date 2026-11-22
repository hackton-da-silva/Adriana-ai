"""Catálogo da planta: hierarquia, equipamentos e variáveis.

Fonte: docs/planta/organizacao-laminacao.md. Números marcados [E] na
especificação são estimativas; todos os dados da simulação são fictícios.
"""

from __future__ import annotations

from dataclasses import dataclass, field

CENARIO = "Usina exemplo — laminação de tiras a quente (dados fictícios)"
USINA = "UNI-01"
AREA = "Laminação a Quente (LTQ)"

LINHAS: dict[int, str] = {
    1: "Reaquecimento",
    2: "Desbaste",
    3: "Acabamento",
    4: "Resfriamento e bobinamento",
}


@dataclass(frozen=True)
class Var:
    id: str
    nome: str
    unidade: str
    faixa: tuple[float | None, float | None]  # faixa normal (None = sem limite)
    base: float  # valor nominal usado pela simulação
    ruido: float  # desvio-padrão do ruído
    alarme_lo: float | None = None
    alarme_hi: float | None = None
    setpoint: float | None = None
    tol_setpoint: float | None = None  # alarme se |v - setpoint| > tol
    processo: bool = False  # sem valor (null) com a linha parada
    casas: int = 1
    # nível ideal de operação (preenchido por _com_ideal; ver regras lá)
    ideal: float | None = None
    tol_ideal: float | None = None  # "ideal" se o desvio do ideal ≤ tol_ideal; acima disso, "atencao"
    sentido: str = "alvo"  # alvo (desvio dos dois lados) | menor (menor é melhor) | info (sem ideal fixo)
    origem_ideal: str = ""

    @property
    def limite_alarme(self) -> tuple[float | None, float | None]:
        lo, hi = self.alarme_lo, self.alarme_hi
        if self.setpoint is not None and self.tol_setpoint is not None:
            lo = self.setpoint - self.tol_setpoint if lo is None else lo
            hi = self.setpoint + self.tol_setpoint if hi is None else hi
        return lo, hi

    def to_dict(self) -> dict:
        d: dict = {"id": self.id, "nome": self.nome, "unidade": self.unidade,
                   "ideal": self.ideal, "tol_ideal": _arred(self.tol_ideal), "sentido": self.sentido,
                   "origem_ideal": self.origem_ideal,
                   "faixa_normal": list(self.faixa), "limite_alarme": list(self.limite_alarme)}
        return d


def _arred(x: float | None) -> float | None:
    return None if x is None else round(x, 3)


@dataclass(frozen=True)
class Equip:
    id: str
    nome: str
    linha: int
    tipo: str
    fabricantes: tuple[str, ...]
    variaveis: tuple[Var, ...]
    descricao: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def linha_nome(self) -> str:
        return LINHAS[self.linha]

    def var(self, var_id: str) -> Var:
        for v in self.variaveis:
            if v.id == var_id:
                return v
        raise KeyError(var_id)

    def to_dict(self, com_variaveis: bool = True) -> dict:
        d = {"id": self.id, "nome": self.nome, "linha": self.linha,
             "linha_nome": self.linha_nome, "tipo": self.tipo,
             "fabricantes_referencia": list(self.fabricantes),
             "descricao": self.descricao}
        if self.extra:
            d.update(self.extra)
        if com_variaveis:
            d["variaveis"] = [v.to_dict() for v in self.variaveis]
        return d


def V(id, nome, unidade, lo, hi, base, ruido, **kw) -> Var:  # noqa: N802
    return Var(id, nome, unidade, (lo, hi), base, ruido, **kw)


# ---------------------------------------------------------------- Linha 1
def _forno(id_: str, nome: str) -> Equip:
    zona = dict(tol_setpoint=25.0, casas=0)
    vs = (
        V("t_zona_preaquec_queimado", "T zona pré-aquecimento queimado", "°C", 1000, 1200, 1120, 4, setpoint=1120, **zona),
        V("t_zona_aquec1_topo", "T zona aquecimento 1 (topo)", "°C", 1200, 1320, 1280, 3, setpoint=1280, **zona),
        V("t_zona_aquec1_fundo", "T zona aquecimento 1 (fundo)", "°C", 1200, 1320, 1280, 3, setpoint=1280, **zona),
        V("t_zona_aquec2_topo", "T zona aquecimento 2 (topo)", "°C", 1200, 1320, 1280, 3, setpoint=1280, **zona),
        V("t_zona_aquec2_fundo", "T zona aquecimento 2 (fundo)", "°C", 1200, 1320, 1280, 3, setpoint=1280, **zona),
        V("t_zona_encharque", "T zona de encharque", "°C", 1220, 1290, 1255, 2.5, setpoint=1255, **zona),
        V("t_desenfornamento", "T de desenfornamento da placa (alvo nível 2: 1.220)", "°C", 1180, 1260, 1222, 4, casas=0),
        V("desvio_modelo_n2", "Desvio do modelo nível 2 (|medido − previsto|)", "°C", 0, 10, 4, 1.5, alarme_hi=20),
        V("dt_skid_mark", "ΔT de skid mark após encharque", "°C", 15, 35, 24, 2.5),
        V("pressao_forno", "Pressão do forno", "Pa", 5, 15, 10, 1.5, alarme_lo=0, alarme_hi=25),
        V("o2_fumos", "O₂ nos fumos", "% seco", 1.0, 3.0, 2.0, 0.15, alarme_lo=0.5, alarme_hi=4.0, casas=2),
        V("co_fumos", "CO nos fumos", "ppm", 0, 200, 70, 15, alarme_hi=400, casas=0),
        V("t_fumos_pos_recuperador", "T dos fumos após o recuperador", "°C", 300, 450, 385, 5, casas=0),
        V("consumo_especifico", "Consumo específico de gás", "GJ/t", 1.1, 1.5, 1.25, 0.012, casas=3),
        V("tempo_residencia", "Tempo de residência (placa fria 250 mm)", "min", 150, 240, 195, 4, casas=0),
        V("ritmo_desenfornamento", "Ritmo de desenfornamento", "placas/h", 12, 20, 15, 0.7, processo=True),
        V("t_agua_skids_entrada", "Água dos skids: T de entrada", "°C", 30, 40, 34, 0.5),
        V("dt_agua_skids", "Água dos skids: ΔT", "°C", 8, 15, 11, 0.5, alarme_hi=18),
        V("pressao_hidraulica_viga", "Pressão hidráulica da viga caminhante", "bar", 120, 180, 150, 3, casas=0),
        V("queimadores_em_trip", "Queimadores em trip / falha de chama", "un", 0, 0, 0, 0, alarme_hi=0.5, casas=0),
    )
    return Equip(
        id_, nome, 1, "forno_viga_caminhante",
        ("Tenova (até ~450 t/h)", "Fives Stein (Digit@l Furnace)", "Danieli Centro Combustion", "Andritz/Maerz"),
        vs,
        "Forno de reaquecimento de viga caminhante, 350–400 t/h, 5 zonas (8 malhas topo/fundo), gás misto COG+BFG com GN de reforço.",
        {"zonas": ["pré-aquecimento não queimado", "pré-aquecimento queimado", "aquecimento 1", "aquecimento 2", "encharque"]},
    )


# ---------------------------------------------------------------- Linha 2
def _descarepador(id_: str, nome: str, linha: int, p_faixa, p_base, q_faixa, q_base, desc: str) -> Equip:
    vs = (
        V("pressao_header", "Pressão no header", "bar", p_faixa[0], p_faixa[1], p_base, 2.0, alarme_lo=160, casas=0),
        V("vazao_ciclo", "Vazão por ciclo", "m³/h", q_faixa[0], q_faixa[1], q_base, 8, processo=True, casas=0),
        V("nivel_acumulador", "Nível do acumulador", "%", 70, 90, 80, 1.2, casas=0),
        V("dp_filtro", "ΔP do filtro", "bar", 0, 1.0, 0.5, 0.05, alarme_hi=1.5, casas=2),
        V("corrente_bomba_1", "Corrente da bomba 1", "% nominal", 80, 95, 88, 1.0, alarme_hi=105),
        V("corrente_bomba_2", "Corrente da bomba 2", "% nominal", 80, 95, 88, 1.0, alarme_hi=105),
        V("t_agua", "T da água", "°C", 25, 40, 32, 0.5),
    )
    return Equip(id_, nome, linha, "descarepador",
                 ("Lechler Scalemaster (bicos 80–450 bar)", "Spraying Systems DescaleJet (até ~400 bar)",
                  "caixa do integrador: SMS / Primetals / Danieli"), vs, desc)


R1 = Equip(
    "R1", "Laminador desbastador reversível R1 + edger", 2, "desbastador",
    ("SMS group", "Primetals", "Danieli", "acionamentos Siemens / ABB / TMEIC"),
    (
        V("forca_laminacao", "Força de laminação", "MN", 15, 45, 30, 1.0, alarme_hi=47.5, processo=True),
        V("delta_forca_lados", "ΔF lado operador × lado acionamento", "%", 0, 5, 2.0, 0.5, alarme_hi=8, processo=True),
        V("torque", "Torque", "% nominal", 30, 90, 62, 2.5, alarme_hi=100, processo=True, casas=0),
        V("corrente_motor", "Corrente do motor", "% nominal", 0, 150, 85, 4, alarme_hi=150, processo=True, casas=0),
        V("velocidade", "Velocidade", "m/s", 2, 5, 3.6, 0.12, processo=True, casas=2),
        V("gap", "Gap (último passe)", "mm", 30, 250, 38, 1.5, processo=True),
        V("t_placa_entrada", "T da placa na entrada (desenfornamento)", "°C", 1180, 1260, 1222, 3, processo=True, casas=0),
        V("t_esboco_saida", "T do esboço na saída", "°C", 1050, 1120, 1085, 4, alarme_lo=1030, processo=True, casas=0),
        V("forca_edger", "Força do edger", "MN", 1, 4, 2.4, 0.2, processo=True, casas=2),
        V("camber", "Camber", "mm/10 m", 0, 15, 6, 1.8, alarme_hi=20, processo=True),
        V("vibracao_mancais", "Vibração dos mancais", "mm/s", 0, 7, 2.8, 0.25, alarme_hi=9, processo=True),
    ),
    "R1 4-high reversível (ref. Tubarão: 2 × 7,5 MW; edger 2 × 1,5 MW). Placa 220–250 mm vira esboço 30–45 mm em 5 ou 7 passes.",
    {"campanha_cilindro_km_limite": 450},
)

CB01 = Equip(
    "CB-01", "Coil box", 2, "coil_box", ("integrador (SMS / Primetals / Danieli)",),
    (
        V("t_entrada", "T do esboço na entrada", "°C", 1050, 1100, 1075, 4, processo=True, casas=0),
        V("t_saida", "T do esboço na saída", "°C", 1030, 1080, 1055, 4, processo=True, casas=0),
        V("dt_cabeca_cauda", "ΔT cabeça–cauda na saída", "°C", 0, 30, 14, 3, alarme_hi=40, processo=True, casas=0),
        V("tempo_enrol_desenrol", "Tempo de enrolamento + desenrolamento", "s", 60, 120, 90, 5, processo=True, casas=0),
    ),
    "Enrola o esboço entre o desbaste e o acabador, equalizando a temperatura da cabeça e da cauda.",
)

# ---------------------------------------------------------------- Linha 3
TES01 = Equip(
    "TES-01", "Tesoura de pontas (crop shear)", 3, "tesoura", ("drum shear rotativa (ref. Usiminas, velocidade diferencial)",),
    (
        V("ciclos_corte", "Ciclos de corte [E]", "cortes/h", 40, 70, 54, 2, processo=True, casas=0),
        V("tempo_corte", "Tempo de corte [E]", "ms", 150, 300, 210, 8, processo=True, casas=0),
        V("comprimento_desponte", "Comprimento do desponte", "mm", 100, 500, 260, 35, processo=True, casas=0),
        V("desvio_posicao_laminas", "Desvio de posição das lâminas [E]", "mm", 0, 2, 0.6, 0.15, alarme_hi=3, casas=2),
        V("corrente_motor", "Corrente do motor [E]", "% nominal", 40, 85, 62, 3, processo=True, casas=0),
    ),
    "Esboço de 30–45 mm a 0,5–2 m/s, desponte de 100–500 mm; esforço de corte ~300 t.",
)

DSC01 = _descarepador("DSC-01", "Descarepador primário", 2, (180, 220), 200, (250, 400), 320,
                      "2 pares de headers (sup./inf.), ~25 bicos por header, bico–placa 100–200 mm, ângulo 15°.")
DSC02 = _descarepador("DSC-02", "Descarepador do acabador", 3, (180, 215), 205, (150, 250), 200,
                      "Mesmo tipo do DSC-01. Faixa de projeto 150–200 bar, nominal ~200–205 bar; alarme < 160 bar.")

CAMPANHA_KM = {"F1": 100, "F2": 100, "F3": 100, "F4": 80, "F5": 80, "F6": 80}  # F1–F3: 60–120 / F4–F6: 40–80


def _lerp(a: float, b: float, x: float) -> float:
    return a + (b - a) * x


def _cadeira(i: int) -> Equip:
    x = (i - 1) / 5
    f_lo, f_hi = _lerp(20000, 8000, x), _lerp(35000, 17000, x)
    f_nom = _lerp(40000, 20000, x)
    g_lo, g_hi = _lerp(15, 1.2, x), _lerp(30, 12, x)
    v_lo, v_hi = _lerp(1, 8, x), _lerp(3, 20, x)
    vs = [
        V("forca_laminacao", "Força de laminação", "kN", round(f_lo), round(f_hi), round((f_lo + f_hi) / 2),
          (f_lo + f_hi) / 2 * 0.025, alarme_hi=round(0.9 * f_nom), processo=True, casas=0),
        V("delta_forca_lados", "ΔF lado operador × lado acionamento", "kN", -1000, 1000, 0, 200,
          alarme_lo=-1500, alarme_hi=1500, processo=True, casas=0),
        V("gap", "Gap", "mm", round(g_lo, 1), round(g_hi, 1), round((g_lo + g_hi) / 2, 1), (g_hi - g_lo) * 0.02,
          processo=True, casas=2),
        V("pressao_agc", "Pressão do cilindro AGC", "bar", 100, 280, 190, 6, processo=True, casas=0),
        V("velocidade", "Velocidade do cilindro", "m/s", round(v_lo, 1), round(v_hi, 1), round((v_lo + v_hi) / 2, 1),
          (v_hi - v_lo) * 0.02, processo=True, casas=2),
        V("corrente_motor", "Corrente do motor", "% nominal", 40, 90, 68, 2.5, alarme_hi=120, processo=True, casas=0),
    ]
    if i < 6:
        vs += [
            V("tensao_entre_cadeiras", f"Tensão entre cadeiras F{i}–F{i + 1}", "MPa", 3, 15, 5, 0.4, processo=True, casas=2),
            V("angulo_looper", f"Ângulo do looper F{i}–F{i + 1} (setpoint 20)", "°", 15, 30, 20, 1.0,
              alarme_lo=5, alarme_hi=40, setpoint=20, processo=True),
            V("amplitude_oscilacao_looper", f"Amplitude de oscilação do looper F{i}–F{i + 1} [E]", "°", 0, 3, 1.2, 0.2,
              alarme_hi=5, processo=True),
        ]
    vs += [
        V("bending", "Bending", "kN/mancal", -500, 1500, 600, 50, processo=True, casas=0),
        V("shifting_cvc", "Shifting CVC", "mm", -150, 150, _lerp(-40, 60, x), 3, processo=True, casas=0),
        V("vibracao", "Vibração da cadeira", "mm/s RMS", 0, 4, 2.6 if i != 5 else 3.0, 0.18, alarme_hi=7,
          processo=True, casas=2),
        V("freq_pico_vibracao", "Frequência do pico de vibração (alarme se 100–250 Hz com vibração > 4)", "Hz",
          20, 100, 55, 5, processo=True, casas=0),
        V("km_campanha_cilindro", "Campanha do cilindro de trabalho (km laminados)", "km", 0, CAMPANHA_KM[f"F{i}"],
          0, 0, alarme_hi=CAMPANHA_KM[f"F{i}"], casas=1),
    ]
    mat = "HSS/HiCr" if i <= 3 else "ICDP"
    diam = "850→765 mm" if i <= 3 else "700→630 mm"
    return Equip(
        f"F{i}", f"Cadeira acabadora F{i} (4-high)", 3, "cadeira_acabadora",
        ("SMS group CVC plus (PCFC)", "Primetals Pair Cross/SmartCrown", "Danieli Q-Change",
         "acionamentos TMEIC / Siemens / ABB"),
        tuple(vs),
        f"4-high, 8 MW, CVC ±150 mm, bending até 1.500 kN, AGC hidráulico. Cilindro de trabalho {mat}, Ø {diam}; "
        "encosto Ø 1.600→1.440 mm." + (f" O looper F{i}–F{i + 1} fica nesta cadeira." if i < 6 else " Última cadeira (sem looper a jusante)."),
        {"campanha_cilindro_km_limite": CAMPANHA_KM[f"F{i}"], "material_cilindro_trabalho": mat},
    )


MED01 = Equip(
    "MED-01", "Medidores na saída do acabador", 3, "medidores",
    ("IMS XR SMC (raio-X multicanal)", "Thermo Fisher RM 215 HM / SIPRO", "AMETEK Land SPOT+ (pirômetros)"),
    (
        V("desvio_espessura", "Desvio de espessura (amostra)", "µm", -50, 50, 0, 12, processo=True, casas=0),
        V("amplitude_oscilacao_espessura", "Amplitude de oscilação da espessura [E]", "µm", 0, 30, 14, 2,
          alarme_hi=50, processo=True, casas=0),
        V("coroa_c40", "Coroa C40", "µm", 20, 80, 45, 4, processo=True, casas=0),
        V("cunha", "Cunha", "µm", -20, 20, 0, 5, processo=True, casas=0),
        V("sobrelargura", "Sobrelargura", "mm", 0, 15, 7, 1.5, processo=True),
        V("planicidade", "Planicidade", "I-units", 0, 20, 9, 2, alarme_hi=30, processo=True),
        V("fdt", "Temperatura de acabamento (FDT)", "°C", 850, 920, 885, 2, processo=True, casas=0),
        V("gradiente_borda_centro", "Gradiente de temperatura borda–centro", "°C", 0, 20, 11, 2, alarme_hi=30,
          processo=True, casas=0),
        V("tensao_tubo_kv", "Saúde: tensão do tubo de raio-X [E]", "kV", 140, 160, 150, 0.4),
        V("corrente_tubo_ma", "Saúde: corrente do tubo [E]", "mA", 5, 15, 10, 0.2, casas=2),
        V("t_cabecote", "Saúde: temperatura do cabeçote [E]", "°C", 20, 40, 31, 0.4),
        V("desvio_calibracao", "Saúde: desvio desde a última calibração", "µm", 0, 10, 4, 0.4, alarme_hi=20),
    ),
    "Raio-X na saída do acabador (espessura, perfil, coroa, cunha, largura) e pirômetros de FDT.",
)

# ---------------------------------------------------------------- Linha 4
N_BANCOS = 20
SETPOINT_BANCO = 200.0

ROT01 = Equip(
    "ROT-01", "Mesa de resfriamento laminar", 4, "mesa_resfriamento",
    ("Primetals Power Cooling", "SMS (headers de vazão uniforme)", "TMEIC (modelo CTC)"),
    tuple(
        V(f"vazao_banco_{b:02d}", f"Vazão do banco laminar {b} (setpoint 200)", "m³/h", 0, 250, SETPOINT_BANCO, 3,
          alarme_lo=0.8 * SETPOINT_BANCO, setpoint=SETPOINT_BANCO, casas=0)
        for b in range(1, N_BANCOS + 1)
    ) + (
        V("vazao_total", "Vazão total (laminar + intensivo)", "m³/h", 8000, 12000, 10000, 40, casas=0),
        V("pressao_header_laminar", "Pressão do header laminar", "bar", 0.5, 1.0, 0.75, 0.03, casas=2),
        V("pressao_header_intensivo", "Pressão do header intensivo", "bar", 3, 10, 6.5, 0.15, casas=2),
        V("t_agua", "T da água", "°C", 28, 35, 31.5, 0.3, alarme_hi=38),
        V("taxa_resf_laminar", "Taxa de resfriamento laminar", "°C/s", 10, 40, 24, 1.5, processo=True),
        V("taxa_resf_intensivo", "Taxa de resfriamento intensivo", "°C/s", 100, 300, 190, 8, processo=True, casas=0),
        V("ct_visada", "CT visada (da bobina em processo)", "°C", 500, 740, 620, 0, processo=True, casas=0),
        V("ct_medida", "CT medida (pirômetro de bobinamento)", "°C", 500, 740, 620, 0, processo=True, casas=0),
        V("erro_ct", "Erro de CT (medida − visada)", "°C", -20, 20, 0, 0, alarme_lo=-30, alarme_hi=30,
          processo=True, casas=0),
    ),
    "100–120 m de mesa, 4 headers intensivos e 20 bancos laminares (4 headers em cima e 4 embaixo cada), "
    "total 8.000–12.000 m³/h. CT visada: baixo carbono 600–680 °C, IF 680–740 °C, HSLA 500–600 °C.",
    {"n_bancos_laminares": N_BANCOS},
)


def _bobinadeira(id_: str, nome: str) -> Equip:
    return Equip(
        id_, nome, 4, "bobinadeira",
        ("SMS (4 wrapper rolls, até 25,4 mm)", "Danieli (1,2–25,4 mm)", "Primetals (até 32 t)"),
        (
            V("tensao_bobinamento", "Tensão de bobinamento", "kN", 20, 200, 110, 7, processo=True, casas=0),
            V("forca_pinch_lo", "Força do pinch roll (lado operador)", "kN", 50, 300, 170, 7, processo=True, casas=0),
            V("forca_pinch_la", "Força do pinch roll (lado acionamento)", "kN", 50, 300, 170, 7, processo=True, casas=0),
            V("assimetria_gap_pinch", "Assimetria do gap do pinch", "mm", 0, 0.5, 0.2, 0.04, alarme_hi=0.5, casas=2),
            V("erro_posicao_wrapper", "Erro de posição do wrapper roll no degrau", "mm", 0, 2, 0.8, 0.2,
              alarme_hi=3, casas=2),
            V("t_mancal_wrapper", "T do mancal do wrapper", "°C", 40, 85, 62, 1.2, alarme_hi=85),
            V("diametro_bobina", "Diâmetro da bobina (última)", "mm", 762, 2100, 1800, 0, processo=True, casas=0),
            V("peso_bobina", "Peso da bobina (última)", "t", 10, 35, 25, 0, processo=True),
            V("pressao_expansao_mandril", "Pressão de expansão do mandril", "bar", 100, 200, 150, 2.5,
              alarme_lo=90, casas=0),
            V("telescopia", "Telescopia", "mm", 0, 5, 2.0, 0.5, alarme_hi=10),
        ),
        "Bobinadeira hidráulica, mandril Ø 762 mm, 4 wrapper rolls, bobina até 35 t, 8–20 m/s.",
    )


# ---------------------------------------------------------------- nível ideal
# Regras (documentadas no README):
# 1. Variável com setpoint ou alvo na especificação → ideal = setpoint/alvo.
#    Tolerância do ideal = 40 % da tolerância de alarme do setpoint (zonas do forno: ±10 °C) ou a indicada abaixo.
# 2. Variável cujo limite na especificação é só "< X" (vibração, ΔF, CO, ΔP do filtro, camber, telescopia...)
#    → sentido "menor": ideal = mínimo da faixa; "atencao" acima de 75 % da faixa (ou da tolerância indicada).
# 3. Variável que depende do produto (gap, velocidade do acabador, bending, shifting, CT visada, peso e diâmetro)
#    → sentido "info": sem ideal fixo; só faixa normal e alarme.
# 4. Demais variáveis (só faixa na especificação) → ideal = meio da faixa normal;
#    "atencao" se o desvio passar de 50 % da meia-faixa.
_ALVO = {  # var_id: (ideal, tol_ideal, origem)
    "t_desenfornamento": (1220, 15, "alvo do nível 2 (1.220 °C)"),
    "t_placa_entrada": (1220, 15, "alvo do nível 2 (1.220 °C)"),
    "consumo_especifico": (1.25, 0.08, "literatura ~1,25 GJ/t"),
    "tensao_entre_cadeiras": (5, 2, "especificação ~5 MPa"),
    "erro_ct": (0, 10, "CT medida = visada"),
    "desvio_espessura": (0, 25, "espessura nominal"),
    "cunha": (0, 10, "cunha nula"),
    "delta_forca_lados": (0, None, "simetria entre lados"),
    "pressao_forno": (10, 2.5, None), "o2_fumos": (2.0, 0.5, None),
}
_MENOR = {"desvio_modelo_n2", "dt_skid_mark", "co_fumos", "queimadores_em_trip", "dp_filtro", "camber",
          "vibracao_mancais", "dt_cabeca_cauda", "desvio_posicao_laminas", "amplitude_oscilacao_looper", "vibracao",
          "km_campanha_cilindro", "amplitude_oscilacao_espessura", "planicidade", "gradiente_borda_centro",
          "desvio_calibracao", "assimetria_gap_pinch", "erro_posicao_wrapper", "telescopia"}
_TOL_MENOR = {"vibracao": 3.5, "queimadores_em_trip": 0.0}
_INFO = {"gap", "bending", "shifting_cvc", "ct_visada", "ct_medida", "diametro_bobina", "peso_bobina"}
_INFO_ACABADOR = {"velocidade", "freq_pico_vibracao"}


def _com_ideal(e: "Equip", v: Var) -> Var:
    from dataclasses import replace
    lo, hi = v.faixa
    if v.id in _INFO or (e.tipo == "cadeira_acabadora" and v.id in _INFO_ACABADOR):
        return replace(v, ideal=None, tol_ideal=None, sentido="info",
                       origem_ideal="depende do produto/setup: sem ideal fixo (só faixa e alarme)")
    if v.id in _MENOR:
        tol = _TOL_MENOR.get(v.id, 0.75 * (hi - lo))
        return replace(v, ideal=lo, tol_ideal=tol, sentido="menor",
                       origem_ideal="especificação dá só limite superior: menor é melhor")
    if e.id == "DSC-02" and v.id == "pressao_header":
        return replace(v, ideal=200, tol_ideal=10, origem_ideal="especificação: normal ~200 bar")
    if v.id in _ALVO:
        ideal, tol, origem = _ALVO[v.id]
        meia = (hi - lo) / 2
        return replace(v, ideal=ideal, tol_ideal=tol if tol is not None else 0.5 * meia,
                       origem_ideal=origem or "meio da faixa normal")
    if v.setpoint is not None:
        tol = 0.4 * v.tol_setpoint if v.tol_setpoint else 0.1 * v.setpoint
        if v.id == "angulo_looper":
            tol = 4.0
        return replace(v, ideal=v.setpoint, tol_ideal=tol, origem_ideal="setpoint da especificação")
    meio = (lo + hi) / 2
    return replace(v, ideal=round(meio, 3), tol_ideal=0.25 * (hi - lo), origem_ideal="meio da faixa normal")


def _finalizar(e: "Equip") -> "Equip":
    from dataclasses import replace
    return replace(e, variaveis=tuple(_com_ideal(e, v) for v in e.variaveis))


EQUIPAMENTOS: tuple[Equip, ...] = tuple(_finalizar(e) for e in (
    _forno("FRN-01", "Forno de reaquecimento 1 (viga caminhante)"),
    _forno("FRN-02", "Forno de reaquecimento 2 (viga caminhante)"),
    DSC01, R1, CB01,
    TES01, DSC02, *(_cadeira(i) for i in range(1, 7)), MED01,
    ROT01, _bobinadeira("BOB-01", "Bobinadeira hidráulica 1"), _bobinadeira("BOB-02", "Bobinadeira hidráulica 2"),
))


def classificar(v: Var, x: float | None) -> tuple[str, str | None]:
    """Classe da leitura: ideal | atencao | fora_da_faixa | alarme | sem_material, e o limite que pesou."""
    if x is None:
        return "sem_material", None
    alo, ahi = v.limite_alarme
    if alo is not None and x < alo:
        return "alarme", f"alarme < {alo:g}"
    if ahi is not None and x > ahi:
        return "alarme", f"alarme > {ahi:g}"
    lo, hi = v.faixa
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        return "fora_da_faixa", f"faixa {lo:g}–{hi:g}"
    if v.sentido == "info" or v.ideal is None:
        return "ideal", None
    d = (x - v.ideal) if v.sentido == "menor" else abs(x - v.ideal)
    if d > v.tol_ideal + 1e-9:
        lim = f"ideal ≤ {v.ideal + v.tol_ideal:g}" if v.sentido == "menor" else f"ideal {v.ideal:g} ±{v.tol_ideal:g}"
        return "atencao", lim
    return "ideal", None

POR_ID: dict[str, Equip] = {e.id: e for e in EQUIPAMENTOS}

CT_VISADA = {"baixo_carbono": 640, "IF": 710, "HSLA": 560}


def equip(eq_id: str) -> Equip:
    key = eq_id.strip().upper()
    if key not in POR_ID:
        raise ValueError(f"Equipamento '{eq_id}' não existe. Válidos: {', '.join(POR_ID)}")
    return POR_ID[key]


def catalogo_dict() -> dict:
    return {
        "cenario": CENARIO,
        "usina": USINA,
        "area": AREA,
        "hierarquia": {
            f"Linha {n}: {nome}": [e.id for e in EQUIPAMENTOS if e.linha == n] for n, nome in LINHAS.items()
        },
        "fluxo": "placa (220–250 mm, ~1.220 °C) → desbaste → esboço (30–45 mm) → coil box → acabador F1–F6 → "
                 "tira (1,2–19 mm, FDT 850–920 °C) → mesa de resfriamento (CT 550–680 °C) → bobinadeira (até ~35 t)",
        "aços": {k: {"ct_visada_c": v} for k, v in CT_VISADA.items()},
        "equipamentos": [e.to_dict() for e in EQUIPAMENTOS],
    }
