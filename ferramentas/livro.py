#!/usr/bin/env python3
"""
livro.py — prepara os dados de um "estudo de livro" a partir do PDF da publicação.

Gera, na pasta dados/livros/<sigla>/ :
  licoes.tsv   num, parte, titulo, pagina, pagina_pdf      (índice das lições/capítulos)
  textos.tsv   licao, secao, ref, abrev, ordem, cap, vers, tipo   (textos bíblicos citados)

Uso:
  python3 livro.py indice  REFERENCIAS/livro.pdf -o ../dados/livros/lff   [--deslocamento 2]
  python3 livro.py textos  REFERENCIAS/livro.pdf -o ../dados/livros/lff
  python3 livro.py resumo  ../dados/livros/lff        (estatísticas: textos mais citados etc.)

Fluxo recomendado para um livro novo:
  1. `indice` tenta achar sozinho o início de cada lição (número de 2 dígitos no alto
     da página). Confira licoes.tsv e CORRIJA à mão os títulos (o PDF às vezes perde os
     acentos) e as páginas. Se o livro tiver outro formato, escreva licoes.tsv à mão:
     basta num, parte, titulo e pagina_pdf (página do PDF onde a lição começa).
  2. `textos` usa as páginas de licoes.tsv para saber a que lição pertence cada texto
     bíblico encontrado. Textos precedidos de "Leia/Leiam" recebem tipo=leia.

Precisa do `pdftotext` (poppler-utils). Só usa a biblioteca padrão do Python 3.
O PDF da publicação NÃO deve ir para o repositório (direitos autorais): guarde-o em
referencias/ (ignorado pelo git).
"""
import argparse
import collections
import os
import re
import subprocess
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVROS_TSV = os.path.join(RAIZ, "dados", "biblia", "livros.tsv")
ACENTOS_SOLTOS = "´`ˆ˜¨¸˙˚ˇ˘\u0002"


# --------------------------------------------------------------- utilidades
def ler_tsv(caminho):
    linhas, cab = [], None
    with open(caminho, encoding="utf-8") as f:
        for l in f:
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
    s = s.replace("ı", "i")
    return "".join(ch for ch in unicodedata.normalize("NFD", s)
                   if unicodedata.category(ch) != "Mn")


def paginas_pdf(pdf):
    """Texto de cada página (lista, índice 0 = página 1), sem acentos soltos."""
    try:
        bruto = subprocess.run(["pdftotext", pdf, "-"], capture_output=True,
                               check=True).stdout.decode("utf-8", "replace")
    except FileNotFoundError:
        sys.exit("Erro: instale o poppler (pdftotext).")
    paginas = []
    for p in bruto.split("\f"):
        linhas = [l for l in p.split("\n") if l.strip(" " + ACENTOS_SOLTOS)]
        t = "\n".join(linhas)
        t = re.sub("[" + re.escape(ACENTOS_SOLTOS) + "]", "", t)
        paginas.append(sem_acentos(t))
    return paginas


def texto_corrido(t):
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)          # hifenização no fim da linha
    return re.sub(r"\s*\n\s*", " ", t)


# -------------------------------------------------------- nomes dos livros
def carregar_livros():
    livros = ler_tsv(LIVROS_TSV)
    nomes = []
    for l in livros:
        alts = {sem_acentos(l["nome"]).lower()} | set(filter(None, l["nomes_alt"].split("|")))
        for a in alts:
            nomes.append((a, l))
    nomes.sort(key=lambda x: -len(x[0]))
    return livros, nomes


def regex_referencias(nomes):
    alt = "|".join(re.escape(n).replace(r"\ ", r"\s+") for n, _ in nomes)
    return re.compile(r"(?<![\w])(" + alt + r")\s+(\d{1,3}:\d{1,3}[\d\s:,;\-–—]*)", re.I)


def expandir(bloco):
    """'10:13, 14; 11:2-4' -> [(10,'13, 14'), (11,'2-4')]"""
    saida = []
    for parte in bloco.split(";"):
        parte = parte.strip(" ,")
        m = re.match(r"(\d{1,3}):(.+)", parte)
        if m:
            vers = re.sub(r"\s+", " ", m.group(2)).strip(" ,-–—")
            vers = re.sub(r"\s*([-–—])\s*", r"\1", vers)
            vers = vers.replace("—", "–")
            if vers:
                saida.append((int(m.group(1)), vers))
    return saida


# ------------------------------------------------------------------ indice
def cmd_indice(a):
    paginas = paginas_pdf(a.pdf)
    licoes, parte = [], 0
    for i, t in enumerate(paginas, start=1):
        linhas = [l.strip() for l in t.split("\n") if l.strip()]
        if any(re.fullmatch(r"PARTE \d+", l) for l in linhas[:3]) and "REVIS" not in t[:200]:
            parte += 1
        for j, l in enumerate(linhas[:6]):
            if re.fullmatch(r"\d{2}", l):
                titulo = " ".join(linhas[j + 1:j + 3])
                licoes.append({"num": l, "parte": parte or "", "titulo": titulo,
                               "pagina": i - a.deslocamento, "pagina_pdf": i})
                break
    destino = os.path.join(a.o, "licoes.tsv")
    escrever_tsv(destino, ["num", "parte", "titulo", "pagina", "pagina_pdf"], licoes,
                 ["Índice das lições — gerado por livro.py indice; CONFIRA e corrija os títulos",
                  "pagina = página impressa; pagina_pdf = página do arquivo PDF"])
    print(f"{len(licoes)} lições encontradas -> {destino}")


# ------------------------------------------------------------------ textos
def cmd_textos(a):
    paginas = paginas_pdf(a.pdf)
    licoes = ler_tsv(os.path.join(a.o, "licoes.tsv"))
    _, nomes = carregar_livros()
    por_nome = {n: l for n, l in nomes}
    rx = regex_referencias(nomes)
    inicios = [(int(l["pagina_pdf"]), l["num"]) for l in licoes]
    inicios.sort()
    fim_ultima = a.ultima or len(paginas)
    saida = []
    for k, (ini, num) in enumerate(inicios):
        fim = inicios[k + 1][0] - 1 if k + 1 < len(inicios) else fim_ultima
        secao = ""
        for pag in range(ini, fim + 1):
            bruto = paginas[pag - 1]
            if re.search(r"PARTE \d+:\s*REVIS", bruto) or re.fullmatch(r"\s*PARTE \d+.*", bruto[:12] or ""):
                continue            # páginas de revisão / abertura de parte
            for linha in bruto.split("\n"):
                m = re.match(r"\s*(\d{1,2})\.\s+\S", linha)
                if m and int(m.group(1)) <= 12:
                    secao = m.group(1)
            t = texto_corrido(bruto)
            for m in rx.finditer(t):
                livro = por_nome[re.sub(r"\s+", " ", m.group(1).lower())]
                antes = t[max(0, m.start() - 22):m.start()].lower()
                tipo = "leia" if re.search(r"\blei(a|am)\b[^.]*$", antes) else "citado"
                for cap, vers in expandir(m.group(2)):
                    if cap > int(livro["capitulos"]):
                        continue
                    saida.append({"licao": num, "secao": secao,
                                  "ref": f'{livro["nome"]} {cap}:{vers}',
                                  "abrev": f'{livro["abrev"]} {cap}:{vers}',
                                  "ordem": livro["ordem"], "cap": cap,
                                  "vers": vers, "tipo": tipo})
    # remove duplicatas exatas dentro da mesma lição, mantendo "leia" se houver
    vistos, final = {}, []
    for s in saida:
        chave = (s["licao"], s["abrev"])
        if chave in vistos:
            if s["tipo"] == "leia":
                vistos[chave]["tipo"] = "leia"
            continue
        vistos[chave] = s
        final.append(s)
    destino = os.path.join(a.o, "textos.tsv")
    escrever_tsv(destino, ["licao", "secao", "ref", "abrev", "ordem", "cap", "vers", "tipo"],
                 final, ["Textos bíblicos citados em cada lição — gerado por livro.py textos",
                         "tipo: leia = o livro pede para ler o texto; citado = citado ou mencionado",
                         "secao = número do parágrafo/ponto da lição em que aparece (aproximado)"])
    print(f"{len(final)} referências em {len(licoes)} lições -> {destino}")


# ------------------------------------------------------------------ resumo
def cmd_resumo(a):
    textos = ler_tsv(os.path.join(a.pasta, "textos.tsv"))
    licoes = ler_tsv(os.path.join(a.pasta, "licoes.tsv"))
    print(f"{len(licoes)} lições, {len(textos)} referências "
          f'({sum(t["tipo"] == "leia" for t in textos)} para ler)')
    c = collections.Counter(t["abrev"] for t in textos)
    print("\nTextos mais citados:")
    for ref, n in c.most_common(a.n):
        print(f"  {n:3d}×  {ref}")
    livros = collections.Counter(t["abrev"].rsplit(" ", 1)[0] for t in textos)
    print("\nLivros mais citados:", ", ".join(f"{k} ({v})" for k, v in livros.most_common(12)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("indice", help="detecta as lições no PDF")
    s.add_argument("pdf"); s.add_argument("-o", required=True, help="pasta de dados do livro")
    s.add_argument("--deslocamento", type=int, default=0,
                   help="página_pdf − página_impressa (ex.: 2)")
    s.set_defaults(f=cmd_indice)
    s = sub.add_parser("textos", help="extrai os textos bíblicos de cada lição")
    s.add_argument("pdf"); s.add_argument("-o", required=True, help="pasta de dados do livro")
    s.add_argument("--ultima", type=int, help="última página do PDF que pertence à última lição")
    s.set_defaults(f=cmd_textos)
    s = sub.add_parser("resumo", help="estatísticas dos dados de um livro")
    s.add_argument("pasta"); s.add_argument("-n", type=int, default=15)
    s.set_defaults(f=cmd_resumo)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
