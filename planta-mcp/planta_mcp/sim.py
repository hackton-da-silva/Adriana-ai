"""Simulação determinística da laminação de tiras a quente (dados fictícios).

- Semente fixa: cada execução gera os mesmos dados (relativos ao início).
- Na inicialização há 8 h de histórico, uma amostra por minuto, de todas as variáveis.
- A simulação avança pelo relógio: a cada consulta, geram-se as amostras até "agora".
  Não há thread de fundo.

Índice de tempo: minuto `m` desde o início do histórico. O servidor sobe em m = 480.

Problemas plantados (minutos desde o início do histórico):
1. FRN-02: trip de queimador na zona de aquecimento 2 (topo) em m=200; zona vai a ~1.180 °C
   (setpoint 1.280); placas saem a ~1.160 °C (alvo 1.220); R1 +18 % de força e FDT −15 °C
   nas placas do FRN-02; O₂ e GJ/t sobem.
2. DSC-02: pressão cai de ~205 para ~150 bar entre m=300 e m=480; corrente da bomba 2 anômala;
   bobinas com mais carepa secundária.
3. F5: chatter. Vibração sobe de ~3 para ~9 mm/s RMS entre m=240 e m=360, pico em ~160 Hz;
   cilindro de trabalho com ~74 de 80 km em m=480; MED-01 com espessura oscilando ±60 µm.
4. F6: 3 cobbles no turno (m=285, 360, 428), motivo "instabilidade do looper F5–F6"; looper
   oscila ±8° a ~1 Hz; ΔF do F6 chega a ~2.000 kN antes de cada cobble. Ligado ao problema 3.
5. ROT-01: banco 7 com vazão 40 % abaixo do setpoint (m=60→120); CT +25 °C nas bobinas HSLA.
"""

from __future__ import annotations

import bisect
import math
import random
import threading
import time
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import catalogo as cat

SEED = 2026
HIST_MIN = 480  # 8 h de histórico na partida
TZ = ZoneInfo("America/Sao_Paulo")

# Linha de produção (desbaste em diante) para por paradas que param a linha
EQUIP_LINHA = {e.id for e in cat.EQUIPAMENTOS if e.linha >= 2}

# Problemas plantados
TRIP_FRN2 = 200
CHATTER_INI, CHATTER_FIM = 240, 360
DSC2_INI, DSC2_FIM = 300, 480
BANCO7_INI, BANCO7_FIM = 60, 120
COBBLES = (285, 360, 428)
COBBLE_DUR = (60, 50, 45)
COBBLE_FUTURO_INI, COBBLE_FUTURO_PERIODO, COBBLE_FUTURO_DUR = 548, 75, 45

RITMO_NOMINAL_TH = 700.0  # t/h com a linha rodando
META_TH = 560.0  # meta média do turno (t/h), ~4,0 Mt/ano com disponibilidade típica
CAPACIDADE_TH = 760.0  # capacidade nominal (t/h) usada no desempenho do OEE

KM_ALVO_PARTIDA = {"F1": 82.0, "F2": 78.0, "F3": 71.0, "F5": 74.0}  # km em m=480 (F4, F6 e R1 trocados no turno)

AR_PHI = 0.8


def ramp(m: float, a: float, b: float) -> float:
    if m <= a:
        return 0.0
    if m >= b:
        return 1.0
    return (m - a) / (b - a)


def _seed(*parts) -> int:
    return zlib.crc32(":".join(str(p) for p in (SEED, *parts)).encode())


@dataclass
class Parada:
    id: str
    equip: str
    inicio: float
    fim: float
    motivo: str
    tipo: str  # "programada" | "nao_programada"
    para_linha: bool = True
    categoria: str = ""

    @property
    def duracao(self) -> float:
        return self.fim - self.inicio


@dataclass
class Bobina:
    id: str
    inicio: float
    fim: float
    forno: str
    aco: str
    espessura_mm: float
    largura_mm: float
    peso_t: float
    t_desenf: float
    frio: float  # 0..1, intensidade do efeito "placa fria"
    fdt: float
    ct_visada: float
    ct_medida: float
    bobinadeira: str
    defeitos: list[str] = field(default_factory=list)
    status: str = "ok"  # ok | desclassificada | sucata
    causa_sucata: str | None = None

    @property
    def erro_ct(self) -> float:
        return self.ct_medida - self.ct_visada

    @property
    def comprimento_km(self) -> float:
        vol = self.peso_t / 7.85
        return vol / (self.espessura_mm / 1000 * self.largura_mm / 1000) / 1000

    def km_cadeira(self, i: int) -> float:
        """km laminados na cadeira Fi: comprimento na saída dela (esboço 38 mm → tira, redução geométrica)."""
        h_saida = 38 * (self.espessura_mm / 38) ** (i / 6)
        return self.comprimento_km * self.espessura_mm / h_saida

    @property
    def km_r1(self) -> float:
        # soma dos comprimentos nos 7 passes (250 → 38 mm, redução geométrica)
        vol = self.peso_t / 0.975 / 7.85
        w = self.largura_mm / 1000
        hs = [0.250 * (0.038 / 0.250) ** (k / 7) for k in range(1, 8)]
        return sum(vol / (h * w) for h in hs) / 1000

    @property
    def diametro_mm(self) -> float:
        vol = self.peso_t / 7.85
        d2 = 0.762 ** 2 + 4 * vol / (math.pi * self.largura_mm / 1000)
        return math.sqrt(d2) * 1000


class Planta:
    """Estado da planta simulada. Thread-safe; avança pelo relógio a cada consulta."""

    def __init__(self, relogio=time.time):
        self._relogio = relogio
        self._lock = threading.RLock()
        agora = relogio()
        self.t0 = math.floor(agora / 60) * 60 - HIST_MIN * 60  # epoch do minuto 0
        self.paradas: list[Parada] = []
        self._paradas_ate = -1.0
        self.bobinas: list[Bobina] = []
        self._inicios: list[float] = []
        self._cursor = 0.0
        self._rng_bob = random.Random(_seed("bobinas"))
        self._seq_bob = 0
        self._bob_por_bobinadeira: dict[str, list[int]] = {"BOB-01": [], "BOB-02": []}
        self._coil_at: list[int | None] = []
        self._km_cum: dict[str, list[float]] = {}
        self.km_offset: dict[str, float] = {}
        self.series: dict[tuple[str, str], list[float | None]] = {}
        self._ar: dict[tuple[str, str], float] = {}
        self._rng: dict[tuple[str, str], random.Random] = {}
        for e in cat.EQUIPAMENTOS:
            for v in e.variaveis:
                k = (e.id, v.id)
                self.series[k] = []
                self._ar[k] = 0.0
                self._rng[k] = random.Random(_seed(e.id, v.id))
        self._paradas_fixas()
        self._gerar_bobinas(HIST_MIN + 5)
        self._calibrar_km()
        self.garantir()

    # ------------------------------------------------------------ tempo
    def m_agora(self) -> int:
        return int((self._relogio() - self.t0) // 60)

    def ts(self, m: float) -> datetime:
        return datetime.fromtimestamp(self.t0 + m * 60, TZ)

    def ts_iso(self, m: float) -> str:
        return self.ts(m).strftime("%Y-%m-%dT%H:%M")

    def garantir(self) -> int:
        """Gera tudo até o minuto atual e devolve m_agora."""
        with self._lock:
            m = self.m_agora()
            self._gerar_paradas(m + 300)
            self._gerar_bobinas(m + 5)
            self._preencher_coil_at(m)
            self._preencher_km(m)
            n = len(next(iter(self.series.values())))
            for mm in range(n, m + 1):
                parada = self.linha_parada(mm) is not None
                for e in cat.EQUIPAMENTOS:
                    for v in e.variaveis:
                        k = (e.id, v.id)
                        self.series[k].append(self._amostra(e, v, mm, parada))
            return m

    # ------------------------------------------------------------ paradas
    def _paradas_fixas(self) -> None:
        P = self.paradas
        P.append(Parada("P-001", "R1", 55, 95, "Troca programada de cilindros de trabalho do R1 e do F4",
                        "programada", True, "troca_cilindros"))
        P.append(Parada("P-002", "CB-01", 150, 168,
                        "Falha de transferência do mandril da coil box; esboço telescopado sucateado",
                        "nao_programada", True, "mecanica"))
        P.append(Parada("P-003", "BOB-02", 232, 244, "Ajuste do gap do pinch roll (assimetria)",
                        "nao_programada", False, "ajuste"))
        for i, (c, d) in enumerate(zip(COBBLES, COBBLE_DUR)):
            P.append(Parada(f"P-{4 + i:03d}", "F6", c, c + d,
                            "Cobble no F6 — instabilidade do looper F5–F6; troca dos cilindros do F6 na limpeza",
                            "nao_programada", True, "cobble"))
        self._paradas_ate = COBBLE_FUTURO_INI - 1

    def _gerar_paradas(self, ate: float) -> None:
        k = len(self.paradas) + 1
        c = COBBLE_FUTURO_INI
        while c <= ate:
            if c > self._paradas_ate:
                self.paradas.append(Parada(f"P-{k:03d}", "F6", c, c + COBBLE_FUTURO_DUR,
                                           "Cobble no F6 — instabilidade do looper F5–F6; troca dos cilindros do F6 na limpeza",
                                           "nao_programada", True, "cobble"))
                k += 1
                self._paradas_ate = c
            c += COBBLE_FUTURO_PERIODO

    def linha_parada(self, m: float) -> Parada | None:
        t = m + 0.5
        for p in self.paradas:
            if p.para_linha and p.inicio <= t < p.fim:
                return p
        return None

    def paradas_ativas(self, m: float) -> list[Parada]:
        t = m + 0.5
        return [p for p in self.paradas if p.inicio <= t < p.fim]

    def _proxima_parada_linha(self, t: float) -> Parada | None:
        cands = [p for p in self.paradas if p.para_linha and p.inicio >= t]
        return min(cands, key=lambda p: p.inicio) if cands else None

    # ------------------------------------------------------------ bobinas
    def pressao_dsc2(self, m: float) -> float:
        return 205 - 55 * ramp(m, DSC2_INI, DSC2_FIM) - 5 * ramp(m, DSC2_FIM, DSC2_FIM + 240)

    def chatter(self, m: float) -> float:
        return ramp(m, CHATTER_INI, CHATTER_FIM)

    def deficit_banco7(self, m: float) -> float:
        return 0.4 * ramp(m, BANCO7_INI, BANCO7_FIM)

    def queda_desenf_frn2(self, m: float) -> float:
        return 62 * ramp(m, TRIP_FRN2, TRIP_FRN2 + 60)

    def _gerar_bobinas(self, ate: float) -> None:
        self._gerar_paradas(ate + 300)
        r = self._rng_bob
        while self._cursor < ate:
            p = self.linha_parada(self._cursor - 0.5 + 1e-9)
            if p is not None:
                self._cursor = p.fim
                continue
            self._seq_bob += 1
            aco = r.choices(["baixo_carbono", "IF", "HSLA"], [0.5, 0.2, 0.3])[0]
            esp = {"baixo_carbono": r.uniform(2.0, 6.0), "IF": r.uniform(1.5, 4.0), "HSLA": r.uniform(3.0, 12.0)}[aco]
            larg = r.uniform(1000, 1800)
            peso = r.uniform(18, 32)
            dur = peso / (RITMO_NOMINAL_TH * r.uniform(0.95, 1.05)) * 60
            inicio = self._cursor
            fim = inicio + dur
            forno = "FRN-01" if self._seq_bob % 2 else "FRN-02"
            desenf = 1222 + r.gauss(0, 4)
            frio = 0.0
            if forno == "FRN-02":
                q = self.queda_desenf_frn2(inicio - 6)
                desenf -= q
                frio = q / 62
            fdt = 885 + r.gauss(0, 5) - 15 * frio
            visada = cat.CT_VISADA[aco] + r.choice([-10, 0, 0, 10])
            erro = r.gauss(0, 6.5)
            if aco == "HSLA":
                erro += 25 * self.deficit_banco7(inicio) / 0.4
            if self.bobinas and self.bobinas[-1].bobinadeira == "BOB-01":
                bobd = "BOB-02"
            else:
                bobd = "BOB-01"
            if any(p.equip == "BOB-02" and p.inicio <= inicio < p.fim for p in self.paradas):
                bobd = "BOB-01"
            b = Bobina(f"BQ{self._seq_bob:05d}", inicio, fim, forno, aco, round(esp, 2), round(larg),
                       round(peso, 1), round(desenf), round(frio, 2), round(fdt), visada, round(visada + erro), bobd)
            # defeitos
            p_carepa = 0.03 + min(0.62, 0.62 * max(0.0, (195 - self.pressao_dsc2(inicio)) / 40))
            if r.random() < p_carepa:
                b.defeitos.append("carepa_secundaria")
            ch = self.chatter(inicio)
            if r.random() < 0.55 * ch:
                b.defeitos.append("marca_periodica_chatter_F5")
            if r.random() < 0.35 * ch:
                b.defeitos.append("espessura_fora_tolerancia")
            if abs(b.erro_ct) > 20:
                b.defeitos.append("ct_fora_tolerancia")
            if r.random() < 0.02:
                b.defeitos.append("telescopia")
            if r.random() < 0.02:
                b.defeitos.append("variacao_espessura_skid_mark")
            prox = self._proxima_parada_linha(inicio + 1e-6)
            if prox is not None and prox.inicio < fim:
                b.fim = prox.inicio
                if prox.categoria == "cobble":
                    b.status, b.causa_sucata = "sucata", "cobble_F6"
                    b.defeitos.append("cobble_F6")
                elif prox.equip == "CB-01":
                    b.status, b.causa_sucata = "sucata", "esboco_sucateado_coil_box"
                    b.defeitos.append("esboco_sucateado_coil_box")
            if b.status != "sucata":
                criticos = {"carepa_secundaria", "marca_periodica_chatter_F5", "espessura_fora_tolerancia",
                            "ct_fora_tolerancia", "telescopia"}
                if criticos & set(b.defeitos):
                    b.status = "desclassificada"
            self.bobinas.append(b)
            self._inicios.append(b.inicio)
            self._bob_por_bobinadeira[bobd].append(len(self.bobinas) - 1)
            self._cursor = b.fim

    def _preencher_coil_at(self, m: int) -> None:
        for mm in range(len(self._coil_at), m + 1):
            t = mm + 0.5
            i = bisect.bisect_right(self._inicios, t) - 1
            if i >= 0 and self.bobinas[i].inicio <= t < self.bobinas[i].fim:
                self._coil_at.append(i)
            else:
                self._coil_at.append(None)

    def bobina_em(self, m: int) -> Bobina | None:
        i = self._coil_at[m] if 0 <= m < len(self._coil_at) else None
        return self.bobinas[i] if i is not None else None

    def ultima_bobina(self, bobinadeira: str, m: int) -> Bobina | None:
        idxs = self._bob_por_bobinadeira[bobinadeira]
        best = None
        for i in reversed(idxs):
            if self.bobinas[i].inicio <= m + 0.5:
                best = self.bobinas[i]
                break
        return best

    # ------------------------------------------------------------ campanha (km)
    def _trocas(self, cad: str) -> list[float]:
        if cad in ("R1", "F4"):
            return [p.fim for p in self.paradas if p.id == "P-001"]
        if cad == "F6":
            return [p.fim for p in self.paradas if p.categoria == "cobble"]
        return []

    def _km_bruto(self, cad: str, m: float) -> float:
        """km desde a última troca (sem offset), contando bobinas iniciadas antes de m."""
        trocas = [t for t in self._trocas(cad) if t <= m + 0.5]
        desde = max(trocas) if trocas else 0.0
        km = 0.0
        for b in self.bobinas:
            if b.inicio >= m + 0.5:
                break
            if b.inicio >= desde:
                km += b.km_r1 if cad == "R1" else b.km_cadeira(int(cad[1]))
        return km

    def _calibrar_km(self) -> None:
        for cad in ("R1", "F1", "F2", "F3", "F4", "F5", "F6"):
            alvo = KM_ALVO_PARTIDA.get(cad)
            self.km_offset[cad] = max(0.0, alvo - self._km_bruto(cad, HIST_MIN)) if alvo else 0.0
            self._km_cum[cad] = []

    def _preencher_km(self, m: int) -> None:
        for cad, arr in self._km_cum.items():
            for mm in range(len(arr), m + 1):
                trocas = [t for t in self._trocas(cad) if t <= mm + 0.5]
                off = 0.0 if trocas else self.km_offset[cad]
                arr.append(off + self._km_bruto(cad, mm))

    def km(self, cad: str, m: int) -> float:
        return self._km_cum[cad][m]

    # ------------------------------------------------------------ amostras
    def _amostra(self, e: cat.Equip, v: cat.Var, m: int, linha_parada: bool) -> float | None:
        k = (e.id, v.id)
        rng = self._rng[k]
        g = rng.gauss(0, 1)
        u = rng.random()
        self._ar[k] = AR_PHI * self._ar[k] + math.sqrt(1 - AR_PHI ** 2) * g
        if v.processo and linha_parada and (e.id in EQUIP_LINHA or e.linha == 1):
            return None
        val = v.base + v.ruido * self._ar[k]
        val = self._efeito(e, v, m, val, u, rng)
        if val is None:
            return None
        return round(val, v.casas)

    def _efeito(self, e: cat.Equip, v: cat.Var, m: int, val: float, u: float, rng: random.Random):
        eid, vid = e.id, v.id
        b = self.bobina_em(m)
        frio = b.frio if (b and b.forno == "FRN-02") else 0.0

        if e.linha == 1:
            if vid == "queimadores_em_trip":
                return 1.0 if (eid == "FRN-02" and m >= TRIP_FRN2) else 0.0
            if vid == "desvio_modelo_n2":
                val = abs(val)
            if eid == "FRN-02":
                r = ramp(m, TRIP_FRN2, TRIP_FRN2 + 8)
                rr = ramp(m, TRIP_FRN2, TRIP_FRN2 + 60)
                if vid == "t_zona_aquec2_topo":
                    val -= 100 * r
                elif vid == "t_zona_aquec2_fundo":
                    val += 14 * r
                elif vid == "t_zona_aquec1_topo":
                    val += 10 * r
                elif vid == "t_zona_encharque":
                    val -= 18 * rr
                elif vid == "t_desenfornamento":
                    val -= self.queda_desenf_frn2(m)
                elif vid == "desvio_modelo_n2":
                    val += 56 * rr
                elif vid == "o2_fumos":
                    val += 1.4 * r
                elif vid == "consumo_especifico":
                    val += 0.15 * rr
                elif vid == "t_fumos_pos_recuperador":
                    val += 25 * r
            return val

        if eid == "R1":
            kmf = self.km("R1", m) / 450
            if vid == "forca_laminacao":
                return val * (1 + 0.18 * frio) * (1 + 0.04 * kmf)
            if vid == "torque":
                return val * (1 + 0.18 * frio)
            if vid == "corrente_motor":
                return val * (1 + 0.15 * frio)
            if vid == "t_placa_entrada":
                return (b.t_desenf if b else 1222) + (val - v.base) * 0.4
            if vid == "t_esboco_saida":
                return val - 50 * frio
            return val

        if eid == "CB-01":
            if vid == "t_entrada":
                return val - 48 * frio
            if vid == "t_saida":
                return val - 42 * frio
            return val

        if eid in ("DSC-01", "DSC-02"):
            if vid == "dp_filtro":
                return max(0.05, val)
            if eid == "DSC-02":
                f = ramp(m, DSC2_INI, DSC2_FIM)
                if vid == "pressao_header":
                    return self.pressao_dsc2(m) + (val - v.base)
                if vid == "corrente_bomba_2":
                    return val + 14 * f + rng.gauss(0, 3) * f
                if vid == "vazao_ciclo":
                    return val * (1 - 0.2 * f)
                if vid == "nivel_acumulador":
                    return val - 8 * f
            return val

        if e.tipo == "cadeira_acabadora":
            i = int(eid[1])
            ch = self.chatter(m)
            if vid == "km_campanha_cilindro":
                return self.km(eid, m)
            if vid == "forca_laminacao":
                frac = self.km(eid, m) / cat.CAMPANHA_KM[eid]
                return val * (1 + 0.08 * frac ** 2) * (1 + 0.04 * frio)
            if i == 6 and vid == "gap" and b:
                return b.espessura_mm + (val - v.base) * 0.1
            if i == 6 and vid == "velocidade" and b:
                return min(19.5, max(8.4, 36 / b.espessura_mm)) + (val - v.base) * 0.3
            cobble_em = self._minutos_ate_cobble(m)
            if i == 5:
                amp = 1.2 + 6.8 * ch
                if vid == "vibracao":
                    return val + 6.2 * ch + rng.gauss(0, 0.35) * ch
                if vid == "freq_pico_vibracao":
                    return val + 105 * ramp(m, CHATTER_INI + 10, CHATTER_INI + 60) + (val - v.base) * -0.6 * ch
                if vid == "amplitude_oscilacao_looper":
                    return amp + (val - v.base)
                if vid == "angulo_looper":
                    if cobble_em == 1:
                        return 1.5 + u
                    return 20 + amp * math.sin(2 * math.pi * u) + (val - v.base) * 0.5
                if vid == "tensao_entre_cadeiras":
                    return val + 0.45 * amp * math.sin(2 * math.pi * u)
            if i == 6:
                if vid == "delta_forca_lados":
                    extra = rng.gauss(0, 70) * ch
                    if cobble_em is not None and cobble_em <= 8:
                        return 2000 * ((9 - cobble_em) / 8) ** 1.5 + rng.gauss(0, 60)
                    return val + extra
                if vid == "corrente_motor" and cobble_em == 1:
                    return 138 + 4 * u
            return val

        if eid == "MED-01":
            ch = self.chatter(m)
            amp = 14 + 46 * ch
            if vid == "fdt":
                return (b.fdt if b else 885) + (val - v.base)
            if vid == "amplitude_oscilacao_espessura":
                return val + 46 * ch
            if vid == "desvio_espessura":
                return amp * math.sin(2 * math.pi * u) + (val - v.base) * 0.5
            if vid == "planicidade":
                return val + 3 * ch
            return val

        if eid == "ROT-01":
            d7 = self.deficit_banco7(m)
            if vid == "vazao_banco_07":
                return val * (1 - d7)
            if vid == "vazao_total":
                return val - cat.SETPOINT_BANCO * d7
            if vid == "taxa_resf_laminar":
                return val * (1 - 0.06 * d7 / 0.4)
            if vid == "ct_visada":
                return b.ct_visada if b else None
            if vid == "ct_medida":
                return b.ct_medida if b else None
            if vid == "erro_ct":
                return b.erro_ct if b else None
            return val

        if e.tipo == "bobinadeira":
            ub = self.ultima_bobina(eid, m)
            if vid == "diametro_bobina":
                return ub.diametro_mm if ub else None
            if vid == "peso_bobina":
                return ub.peso_t if ub else None
            if vid == "assimetria_gap_pinch" and eid == "BOB-02":
                # assimetria antes do ajuste P-003
                return val + 0.35 * ramp(m, 200, 230) * (1 - ramp(m, 243, 244))
            return val

        return val

    def _minutos_ate_cobble(self, m: int) -> int | None:
        for p in self.paradas:
            if p.categoria == "cobble":
                d = math.ceil(p.inicio - (m + 0.5))
                if 1 <= d <= 8:
                    return d
        return None

    # ------------------------------------------------------------ leitura
    def serie(self, eq_id: str, var_id: str, ini: int, fim: int) -> list[float | None]:
        return self.series[(eq_id, var_id)][max(0, ini): fim + 1]

    def valor(self, eq_id: str, var_id: str, m: int) -> float | None:
        return self.series[(eq_id, var_id)][m]

    def ultimo_valido(self, eq_id: str, var_id: str, m: int) -> tuple[float | None, int | None]:
        s = self.series[(eq_id, var_id)]
        for mm in range(m, max(-1, m - 600), -1):
            if s[mm] is not None:
                return s[mm], mm
        return None, None

    def ts_delta(self, minutos: float) -> timedelta:
        return timedelta(minutes=minutos)
