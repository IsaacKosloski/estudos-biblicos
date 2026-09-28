#!/usr/bin/env python3
"""
tema.py — prepara os dados de um estudo temático (dados/temas/<sigla>/).

  python3 ferramentas/tema.py ocorrencias H1818 G129 -o dados/temas/sangue
      todas as ocorrências dos números de Strong no AT (WLC/OSHB) e no NT (SBLGNT)
      -> ocorrencias.tsv  (e um resumo por livro na tela)
  python3 ferramentas/tema.py vocabulario H1818 G129 -o dados/temas/sangue
      -> vocabulario.tsv pré-preenchido (lema, Strong, nº de ocorrências, sentido em inglês)
  python3 ferramentas/tema.py conferir dados/temas/sangue
      confere textos.tsv (livros reconhecidos, repetições) e mostra quais
      ocorrências ainda não foram incluídas na sua lista de textos

Arquivos da pasta do tema (TSV, UTF-8, tabulação; # = comentário):
  textos.tsv       ref, grupo, peso, nota          ← VOCÊ escreve (a lista de estudo)
  vocabulario.tsv  lingua, lema, translit, strong, ocorrencias, sentido, nota
  ocorrencias.tsv  strong, lema, ref, ordem, cap, vers, forma   (gerado)

Referências no formato "Gn 9:4", "Lv 17:10-14", "At 15:28, 29" (abreviações de
dados/biblia/livros.tsv) ou com o nome completo ("Gênesis 9:4").
Atenção: no AT as ocorrências usam a numeração HEBRAICA dos versículos
(ex.: Sl 83:19 no hebraico = 83:18 nas Bíblias em português).
Usa a biblioteca padrão do Python 3 e baixa as bases na primeira execução
(ferramentas/.cache/).
"""
import argparse
import collections
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interlinear as il  # noqa: E402  (reaproveita downloads e léxicos)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OSHB = ["Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam",
        "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov", "Eccl",
        "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos", "Obad", "Jonah",
        "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal"]


def ler_tsv(caminho):
    linhas, cab = [], None
    if not os.path.exists(caminho):
        return linhas
    for l in open(caminho, encoding="utf-8"):
        l = l.rstrip("\n\r")
        if not l.strip() or l.startswith("#"):
            continue
        campos = l.split("\t")
        if cab is None:
            cab = campos
        else:
            linhas.append(dict(zip(cab, campos + [""] * (len(cab) - len(campos)))))
    return linhas


def escrever_tsv(caminho, cab, linhas, comentarios=()):
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        for c in comentarios:
            f.write("# " + c + "\n")
        f.write("\t".join(cab) + "\n")
        for l in linhas:
            f.write("\t".join(str(l.get(c, "")) for c in cab) + "\n")


def sem_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


LIVROS = ler_tsv(os.path.join(RAIZ, "dados", "biblia", "livros.tsv"))
POR_NOME = {}
for _l in LIVROS:
    for _n in [_l["abrev"], _l["nome"]] + _l["nomes_alt"].split("|"):
        if _n:
            POR_NOME[sem_acentos(_n).replace(" ", "")] = _l


def livro_de(ref):
    m = re.match(r"^(.*?)\s*(\d+):(.+)$", ref.strip())
    if not m:
        return None, None, None
    return POR_NOME.get(sem_acentos(m[1]).replace(" ", "")), int(m[2]), m[3].strip()


def versiculos(vers):
    """'10-14, 16' -> {10,...,14,16}"""
    s = set()
    for p in re.split(r"[,;]", vers):
        m = re.match(r"\s*(\d+)(?:\s*[-–]\s*(\d+))?", p)
        if m:
            a, b = int(m[1]), int(m[2] or m[1])
            s.update(range(a, b + 1))
    return s


# ------------------------------------------------------------ ocorrências
def ocorrencias_gregas(num):
    lex = il.lexico_grego()
    lemas = {l for l, info in lex.items() if info.get("strongs", "").strip("'\" ") == num}
    achados = []
    for idx, (abrev, _) in enumerate(il.NT):
        arq, _ = il.morphgnt(abrev)
        for linha in open(arq, encoding="utf8"):
            c = linha.split()
            if c[-1] in lemas:
                ref = c[0]
                achados.append({"strong": "G" + num, "lema": c[-1], "ordem": 40 + idx,
                                "abrev": LIVROS[39 + idx]["abrev"],
                                "cap": int(ref[2:4]), "vers": int(ref[4:6]),
                                "forma": re.sub("[⸀⸁⸂⸃⸄⸅]", "", c[3])})
    return achados


def ocorrencias_hebraicas(num):
    lex = il.lexico_hebraico()
    lema = lex.get(num, ("", ""))[0]
    achados = []
    for idx, livro in enumerate(OSHB):
        arq = il.baixar(f"openscriptures/morphhb/master/wlc/{livro}.xml", f"{livro}.xml")
        xml = open(arq, encoding="utf8").read()
        for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)"[^>]*>(.*?)</verse>', xml, re.S):
            for w in re.finditer(r'<w ([^>]*)>(.*?)</w>', m[3]):
                att = dict(re.findall(r'(\w+)="([^"]*)"', w[1]))
                nums = re.findall(r"\d+", att.get("lemma", ""))
                if nums and nums[-1] == num:
                    achados.append({"strong": "H" + num, "lema": lema, "ordem": idx + 1,
                                    "abrev": LIVROS[idx]["abrev"], "cap": int(m[1]),
                                    "vers": int(m[2]), "forma": w[2].replace("/", "")})
    return achados


def coletar(strongs):
    todos = []
    for s in strongs:
        s = s.upper()
        if not re.fullmatch(r"[GH]\d+", s):
            sys.exit(f"Número de Strong inválido: {s} (use G129, H1818...)")
        num = str(int(s[1:]))
        todos += ocorrencias_gregas(num) if s[0] == "G" else ocorrencias_hebraicas(num)
    return todos


def cmd_ocorrencias(a):
    achados = coletar(a.strong)
    for x in achados:
        x["ref"] = f'{x["abrev"]} {x["cap"]}:{x["vers"]}'
    destino = os.path.join(a.o, "ocorrencias.tsv")
    escrever_tsv(destino, ["strong", "lema", "ref", "ordem", "cap", "vers", "forma"], achados,
                 ["Ocorrências gerada por ferramentas/tema.py ocorrencias " + " ".join(a.strong),
                  "AT: WLC/OSHB (CC BY 4.0), numeração hebraica; NT: SBLGNT/MorphGNT"])
    por = collections.OrderedDict()
    for x in achados:
        por.setdefault((x["strong"], x["lema"]), collections.Counter())[x["abrev"]] += 1
    for (s, l), c in por.items():
        print(f"{s} {l}: {sum(c.values())} ocorrências — " + ", ".join(f"{k} {v}" for k, v in c.items()))
    print(f"-> {destino}")


def cmd_vocabulario(a):
    achados = coletar(a.strong)
    cont = collections.Counter((x["strong"], x["lema"]) for x in achados)
    lexg, lexh = None, None
    linhas = []
    for s in a.strong:
        s = s.upper(); num = str(int(s[1:]))
        if s[0] == "G":
            lexg = lexg or il.lexico_grego()
            for lema, info in lexg.items():
                if info.get("strongs", "").strip("'\" ") == num:
                    linhas.append({"lingua": "grego", "lema": lema, "strong": s,
                                   "ocorrencias": cont[(s, lema)],
                                   "sentido": info.get("gloss", "").strip("'\"")})
        else:
            lexh = lexh or il.lexico_hebraico()
            lema, defi = lexh.get(num, ("", ""))
            n = sum(v for (st, _), v in cont.items() if st == s)
            linhas.append({"lingua": "hebraico", "lema": lema, "strong": s, "ocorrencias": n,
                           "sentido": re.sub(r"<[^>]+>", "", defi)[:80]})
    destino = os.path.join(a.o, "vocabulario.tsv")
    escrever_tsv(destino, ["lingua", "lema", "translit", "strong", "ocorrencias", "sentido", "nota"],
                 linhas, ["Vocabulário do tema — gerado por tema.py vocabulario; complete translit e sentido em português",
                          "lingua: grego | hebraico | aramaico; translit vazia no grego = gerada automaticamente"])
    print(f"{len(linhas)} lema(s) -> {destino}")


# ------------------------------------------------------------------ conferir
def cmd_conferir(a):
    textos = ler_tsv(os.path.join(a.pasta, "textos.tsv"))
    if not textos:
        sys.exit("textos.tsv vazio ou ausente.")
    ok, cobertos, vistos = 0, set(), set()
    grupos = collections.Counter()
    for t in textos:
        livro, cap, vers = livro_de(t["ref"])
        if not livro:
            print(f"  ! referência não reconhecida: {t['ref']}")
            continue
        chave = (livro["abrev"], cap, vers)
        if chave in vistos:
            print(f"  ! repetida: {t['ref']}")
        vistos.add(chave)
        ok += 1
        grupos[t.get("grupo", "")] += 1
        for v in versiculos(vers):
            cobertos.add((livro["abrev"], cap, v))
    print(f"{ok} textos reconhecidos em {len(grupos)} grupo(s): "
          + ", ".join(f"{g or '(sem grupo)'} {n}" for g, n in grupos.items()))
    oc = ler_tsv(os.path.join(a.pasta, "ocorrencias.tsv"))
    if oc:
        faltam = collections.OrderedDict()
        for o in oc:
            k = (o["abrev"] if "abrev" in o else o["ref"].rsplit(" ", 1)[0], int(o["cap"]), int(o["vers"]))
            if k not in cobertos:
                faltam.setdefault(k[0], []).append(f"{k[1]}:{k[2]}")
        n = sum(len(v) for v in faltam.values())
        print(f"\nOcorrências ainda fora da sua lista: {n} de {len(oc)}")
        for livro, refs in faltam.items():
            unicos = list(dict.fromkeys(refs))
            print(f"  {livro:4s} " + ", ".join(unicos[:25]) + (" …" if len(unicos) > 25 else ""))
        print("\n(Não é preciso incluir todas: a lista de estudo é uma seleção. Mas vale ler cada uma"
              " ao menos uma vez para não perder nada importante.)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for nome, f, ajuda in [("ocorrencias", cmd_ocorrencias, "todas as ocorrências de números de Strong"),
                           ("vocabulario", cmd_vocabulario, "pré-preenche vocabulario.tsv")]:
        s = sub.add_parser(nome, help=ajuda)
        s.add_argument("strong", nargs="+", help="ex.: H1818 G129")
        s.add_argument("-o", required=True, help="pasta do tema (dados/temas/<sigla>)")
        s.set_defaults(f=f)
    s = sub.add_parser("conferir", help="confere textos.tsv e a cobertura das ocorrências")
    s.add_argument("pasta")
    s.set_defaults(f=cmd_conferir)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
