"""Busca textual da documentação: BM25 (Okapi) com sinônimos do domínio.

Local e determinística: sem modelo, sem API, sem latência extra. Cada consulta
roda sobre poucas dezenas de trechos (a documentação de uma máquina), então o
índice é montado na hora e guardado em cache por corpus.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from functools import lru_cache

K1 = 1.5
B = 0.75

_VAZIAS = {
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "um", "uma", "com", "por", "para", "pra",
    "que", "esta", "ta", "o", "a", "os", "as", "e", "ou", "se", "ao", "aos", "the", "and", "of",
}

# Linguagem do operador → termos da documentação. As chaves e os valores passam
# pelo mesmo normalizador, então acentos e plural não importam.
SINONIMOS: dict[str, list[str]] = {
    "superaquecendo": ["temperatura alta", "sobretemperatura"],
    "superaquecimento": ["temperatura alta", "sobretemperatura"],
    "esquentando": ["temperatura alta"],
    "quente": ["temperatura alta"],
    "frio": ["temperatura baixa"],
    "fria": ["temperatura baixa"],
    "vibrando": ["vibracao", "chatter"],
    "tremendo": ["vibracao", "chatter"],
    "trepidacao": ["vibracao", "chatter"],
    "enrolou": ["cobble"],
    "embolou": ["cobble"],
    "encavalou": ["cobble"],
    "sucata": ["cobble", "refugo"],
    "entupido": ["obstrucao", "vazao baixa", "bico"],
    "entupimento": ["obstrucao", "vazao baixa", "bico"],
    "vazando": ["vazamento"],
    "parou": ["parada", "trip"],
    "desarmou": ["trip", "parada"],
    "caiu": ["trip", "queda"],
    "pressao baixa": ["queda de pressao"],
    "torta": ["camber"],
    "torto": ["camber"],
    "espessura errada": ["espessura fora", "agc"],
    "carepa": ["descarepacao", "oxido"],
    "gasto": ["desgaste", "campanha"],
    "desgastado": ["desgaste", "campanha"],
    "troca de cilindro": ["campanha", "cilindro de trabalho"],
    "telescopada": ["telescopia"],
    "bobina torta": ["telescopia"],
    "queimador apagado": ["falha de chama", "trip de queimador"],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def tokens(s: str) -> list[str]:
    """Termos normalizados: sem acento, sem palavras vazias, cortados em 5 letras
    (stemming simples: alta/alto, vazão/vazões batem). Mantém repetições (BM25 usa a frequência)."""
    return [t[:5] for t in re.split(r"[^a-z0-9]+", norm(s)) if len(t) >= 2 and t not in _VAZIAS]


def expandir(consulta: str) -> list[str]:
    """Tokens da consulta mais os sinônimos de qualquer expressão do glossário presente nela."""
    q = norm(consulta)
    extra: list[str] = []
    for chave, alvos in SINONIMOS.items():
        if re.search(rf"\b{re.escape(norm(chave))}\b", q):
            for a in alvos:
                extra += tokens(a)
    return tokens(consulta) + extra


class BM25:
    def __init__(self, docs: list[str]):
        self.docs = [tokens(d) for d in docs]
        self.n = len(self.docs)
        self.avgdl = (sum(len(d) for d in self.docs) / self.n) if self.n else 0.0
        self.tf = [Counter(d) for d in self.docs]
        df = Counter(t for d in self.docs for t in set(d))
        # IDF do Okapi BM25 com +1 para nunca ficar negativo em termos muito comuns.
        self.idf = {t: math.log(1 + (self.n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def pontuar(self, consulta: str) -> list[float]:
        q = set(expandir(consulta))
        out = []
        for tf, d in zip(self.tf, self.docs):
            s = 0.0
            norm_len = 1 - B + B * (len(d) / self.avgdl if self.avgdl else 0)
            for t in q:
                f = tf.get(t)
                if f:
                    s += self.idf[t] * f * (K1 + 1) / (f + K1 * norm_len)
            out.append(s)
        return out

    def melhores(self, consulta: str, n: int) -> list[tuple[int, float]]:
        """(índice, pontuação) dos n melhores documentos com pontuação > 0."""
        pts = self.pontuar(consulta)
        ordem = sorted(range(len(pts)), key=lambda i: -pts[i])
        return [(i, pts[i]) for i in ordem[:n] if pts[i] > 0]


@lru_cache(maxsize=64)
def indice(docs: tuple[str, ...]) -> BM25:
    return BM25(list(docs))
