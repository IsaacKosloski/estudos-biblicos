#!/usr/bin/env python3
"""
estudos.py — ferramenta do repositório de estudos bíblicos.

  python3 estudos.py listar
  python3 estudos.py compilar cadernos/exegese/lc06-20-26     (ou --todos)
  python3 estudos.py erros    cadernos/livros/lff              (o que o main.log acusou)
  python3 estudos.py limpar   cadernos/exegese/lc06-20-26     (ou --todos)
  python3 estudos.py novo exegese mt05-03-12 --titulo "Mateus 5:3–12"
  python3 estudos.py novo livro   lff        --titulo "Seja Feliz Para Sempre!"
  python3 estudos.py novo tema    sangue     --titulo "O que a Bíblia diz sobre o sangue?"
  python3 estudos.py overleaf cadernos/livros/lff              (gera saida/<nome>-overleaf.zip)
  python3 estudos.py verificar                                 (confere se o TeX está instalado)

Só usa a biblioteca padrão do Python 3 (Windows, macOS e Linux).
"""
import argparse
import configparser
import datetime
import os
import re
import shutil
import subprocess
import sys
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
CADERNOS = os.path.join(RAIZ, "cadernos")
SAIDA = os.path.join(RAIZ, "saida")
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
LIXO = re.compile(r"\.(aux|log|toc|out|bbl|bcf|blg|idx|ilg|ind|fls|fdb_latexmk|synctex\.gz|run\.xml|xdv)$")


def rel(caminho):
    return os.path.relpath(caminho, RAIZ).replace(os.sep, "/")


def cadernos():
    achados = []
    for pasta, _, arquivos in os.walk(CADERNOS):
        if "main.tex" in arquivos:
            achados.append(pasta)
    return sorted(achados)


def resolver(alvos, todos):
    if todos:
        return cadernos()
    if not alvos:
        sys.exit("Indique um caderno (ex.: cadernos/exegese/lc06-20-26) ou use --todos.")
    saida = []
    for a in alvos:
        p = a if os.path.isabs(a) else os.path.join(os.getcwd(), a)
        if not os.path.exists(os.path.join(p, "main.tex")):
            # aceita só o nome da pasta
            cand = [c for c in cadernos() if os.path.basename(c) == a.strip("/")]
            if len(cand) == 1:
                p = cand[0]
            else:
                sys.exit(f"Caderno não encontrado: {a}")
        saida.append(os.path.abspath(p))
    return saida


def nome_saida(caderno):
    partes = rel(caderno).split("/")[1:]          # tira "cadernos"
    return "-".join(partes)


# ------------------------------------------------------------------ listar
def cmd_listar(a):
    for c in cadernos():
        cfg = open(os.path.join(c, "config.tex"), encoding="utf-8").read() \
            if os.path.exists(os.path.join(c, "config.tex")) else ""
        m = re.search(r"\\newcommand\\ebTitulo\{(.*?)\}", cfg)
        pdf = os.path.join(SAIDA, nome_saida(c) + ".pdf")
        estado = "PDF em saida/" if os.path.exists(pdf) else "ainda não compilado"
        print(f"{rel(c):40s} {m.group(1) if m else '':35s} {estado}")


# ---------------------------------------------------------------- verificar
def cmd_verificar(a):
    ok = True
    for prog in ["lualatex", "latexmk", "biber", "makeindex", "pdftotext"]:
        achou = shutil.which(prog)
        print(f"  {'ok ' if achou else 'FALTA'}  {prog:10s} {achou or ''}")
        if not achou and prog != "pdftotext":
            ok = False
    if not shutil.which("pdftotext"):
        print("  (pdftotext só é necessário para ferramentas/livro.py)")
    if not ok:
        print("\nInstale o TeX Live (ver MANUAL.md, seção Instalação).")
    return 0 if ok else 1


# ------------------------------------------------------------------ compilar
ERRO_TEX = re.compile(r"^(?:!|\S*\.(?:tex|sty|lua|bib):\d+:)")


def erros_do_log(caminho, quantos=3):
    """Devolve as primeiras mensagens de erro do main.log, já formatadas."""
    if not os.path.exists(caminho):
        return []
    linhas = open(caminho, encoding="utf-8", errors="replace").read().split("\n")
    saida, i = [], 0
    while i < len(linhas) and len(saida) < quantos:
        if ERRO_TEX.match(linhas[i].strip()):
            bloco = [l for l in linhas[i:i + 4] if l.strip()]
            saida.append("\n      ".join(bloco))
            i += 4
        else:
            i += 1
    return saida


def rodar_latexmk(pasta, forcar, verboso):
    cmd = ["latexmk", "main.tex"] + (["-g"] if forcar else [])
    if verboso:
        return subprocess.run(cmd, cwd=pasta).returncode, ""
    r = subprocess.run(cmd, cwd=pasta, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def cmd_compilar(a):
    if not shutil.which("latexmk"):
        sys.exit("latexmk não encontrado. Rode `python3 estudos.py verificar` e veja o MANUAL.md.")
    os.makedirs(SAIDA, exist_ok=True)
    falhas = []
    for c in resolver(a.cadernos, a.todos):
        print(f"==> {rel(c)}")
        rc, saida = rodar_latexmk(c, a.forcar, a.verboso)
        # latexmk se recusa a repetir uma compilação que falhou antes: limpa e tenta de novo
        if rc != 0 and "previous invocation" in saida:
            print("    (a compilação anterior falhou; limpando os auxiliares e tentando de novo)")
            limpar_pasta(c, False)
            rc, saida = rodar_latexmk(c, True, a.verboso)
        pdf = os.path.join(c, "main.pdf")
        if rc == 0 and os.path.exists(pdf):
            destino = os.path.join(SAIDA, nome_saida(c) + ".pdf")
            shutil.copy2(pdf, destino)
            print(f"    ok -> {rel(destino)}")
        else:
            falhas.append(c)
            print(f"    ERRO — veja {rel(os.path.join(c, 'main.log'))} (ou rode com -v)")
            for e in erros_do_log(os.path.join(c, "main.log")):
                print("      " + e)
    if falhas:
        sys.exit(1)


# -------------------------------------------------------------------- limpar
def limpar_pasta(c, tambem_pdf):
    n = 0
    for pasta, _, arquivos in os.walk(c):
        for f in arquivos:
            if LIXO.search(f) or (tambem_pdf and f == "main.pdf"):
                os.remove(os.path.join(pasta, f))
                n += 1
    return n


def cmd_limpar(a):
    for c in resolver(a.cadernos, a.todos):
        print(f"{rel(c)}: {limpar_pasta(c, a.pdf)} arquivo(s) auxiliares removidos")


# -------------------------------------------------------------------- erros
def cmd_erros(a):
    for c in resolver(a.cadernos, a.todos):
        log = os.path.join(c, "main.log")
        if not os.path.exists(log):
            print(f"{rel(c)}: sem main.log (compile pelo menos uma vez)")
            continue
        msgs = erros_do_log(log, a.n)
        print(f"==> {rel(log)}")
        if not msgs:
            print("    nenhum erro no log (a última compilação terminou bem)")
        for m in msgs:
            print("      " + m)


# ---------------------------------------------------------------------- novo
def padroes():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(RAIZ, "estudos.ini"), encoding="utf-8")
    return cfg["padrao"] if "padrao" in cfg else {}


def cmd_novo(a):
    tipo_pasta = {"exegese": "exegese", "livro": "livros", "tema": "temas"}[a.tipo]
    destino = os.path.join(CADERNOS, tipo_pasta, a.nome)
    if os.path.exists(destino):
        sys.exit(f"Já existe: {rel(destino)}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", a.nome):
        print("Aviso: prefira nomes só com letras minúsculas, números, '-' e '.'.\n"
              "       Caracteres como '_' precisam ser escritos como \\_ dentro de arquivos .tex e .bib.")
    modelo = os.path.join(RAIZ, "modelos", a.tipo)
    shutil.copytree(modelo, destino)
    shutil.copy2(os.path.join(RAIZ, "compartilhado", "latexmkrc-caderno"),
                 os.path.join(destino, "latexmkrc"))
    p = padroes()
    hoje = datetime.date.today()
    valores = {
        "TITULO": a.titulo or a.nome,
        "SUBTITULO": a.subtitulo or "",
        "INCIPIT": a.incipit or "",
        "SERIE": p.get("serie", "Cadernos de Estudo Bíblico"),
        "NUMERO": str(len(cadernos())),
        "AUTOR": a.autor or p.get("autor", ""),
        "DATA": f"{MESES[hoje.month - 1].capitalize()} de {hoje.year}",
        "EPIGRAFE": p.get("epigrafe", ""),
        "EPIGRAFE_REF": p.get("epigrafe_ref", ""),
        "TEMA": a.tema or p.get("tema_" + a.tipo, {"tema": "purpura"}.get(a.tipo, "lapis")),
        "PAPEL": p.get("papel", "a4"),
        "SIGLA": a.nome,
    }
    for pasta, _, arquivos in os.walk(destino):
        for f in arquivos:
            if f.endswith((".tex", ".bib")):
                caminho = os.path.join(pasta, f)
                s = open(caminho, encoding="utf-8").read()
                for k, v in valores.items():
                    s = s.replace(f"«{k}»", v)
                open(caminho, "w", encoding="utf-8").write(s)
    print(f"Caderno criado: {rel(destino)}")
    if a.tipo == "livro":
        dados = os.path.join(RAIZ, "dados", "livros", a.nome)
        os.makedirs(dados, exist_ok=True)
        print(f"\nPróximos passos (dados em {rel(dados)}):\n"
              f"  1. copie o PDF do livro para referencias/\n"
              f"  2. python3 ferramentas/livro.py indice referencias/LIVRO.pdf -o {rel(dados)} --deslocamento N\n"
              f"     (confira e corrija os títulos em licoes.tsv)\n"
              f"  3. python3 ferramentas/livro.py textos referencias/LIVRO.pdf -o {rel(dados)}\n"
              f"  4. python3 estudos.py compilar {rel(destino)}")
    elif a.tipo == "tema":
        dados = os.path.join(RAIZ, "dados", "temas", a.nome)
        os.makedirs(dados, exist_ok=True)
        textos = os.path.join(dados, "textos.tsv")
        if not os.path.exists(textos):
            with open(textos, "w", encoding="utf-8") as f:
                f.write("# Lista de estudo do tema. ref | grupo | peso (central|apoio|dificil) | nota\n"
                        "ref\tgrupo\tpeso\tnota\n")
        print(f"\nPróximos passos (dados em {rel(dados)}):\n"
              f"  1. descubra os números de Strong das palavras do tema (ex.: sangue = H1818, G129)\n"
              f"  2. python3 ferramentas/tema.py ocorrencias H1818 G129 -o {rel(dados)}\n"
              f"  3. python3 ferramentas/tema.py vocabulario H1818 G129 -o {rel(dados)}\n"
              f"  4. escreva a sua lista em {rel(textos)} (ref, grupo, peso, nota)\n"
              f"  5. python3 ferramentas/tema.py conferir {rel(dados)}\n"
              f"  6. python3 estudos.py compilar {rel(destino)}")
    else:
        print(f"\nPróximos passos:\n"
              f"  1. edite {rel(destino)}/config.tex (título, incipit)\n"
              f"  2. gere os dados: python3 ferramentas/interlinear.py grego Mt 5:3-12 "
              f"-o dados/biblia/mt05_03-12.grc.tsv\n"
              f"  3. python3 estudos.py compilar {rel(destino)}")


# ------------------------------------------------------------------ overleaf
LATEXMKRC_OVERLEAF = """# LuaLaTeX + biber + makeindex (projeto exportado para o Overleaf)
$pdf_mode = 4;
$lualatex = 'lualatex -interaction=nonstopmode -file-line-error -synctex=1 %O %S';
$bibtex_use = 2;
$makeindex = 'makeindex -s indice.ist %O -o %D %S';
"""


def cmd_overleaf(a):
    c = resolver([a.caderno], False)[0]
    nome = nome_saida(c)
    os.makedirs(SAIDA, exist_ok=True)
    zipdest = a.o or os.path.join(SAIDA, nome + "-overleaf.zip")
    comp = os.path.join(RAIZ, "compartilhado")
    usados = set()
    # que dados o caderno usa? (dados/... citados nos .tex) + livros.tsv sempre
    for pasta, _, arquivos in os.walk(c):
        for f in arquivos:
            if f.endswith(".tex"):
                usados |= set(re.findall(r"dados/[\w./-]+", open(os.path.join(pasta, f), encoding="utf-8").read()))
    with zipfile.ZipFile(zipdest, "w", zipfile.ZIP_DEFLATED) as z:
        def add(orig, arc):
            z.write(orig, f"{nome}/{arc}")
        for pasta, _, arquivos in os.walk(c):
            for f in arquivos:
                if LIXO.search(f) or f in ("latexmkrc", "main.pdf"):
                    continue
                orig = os.path.join(pasta, f)
                add(orig, os.path.relpath(orig, c).replace(os.sep, "/"))
        for sub in ("estilo", "fontes"):
            for f in sorted(os.listdir(os.path.join(comp, sub))):
                add(os.path.join(comp, sub, f), f"{sub}/{f}")
        for f in os.listdir(comp):
            if f.endswith(".ist"):
                add(os.path.join(comp, f), f)
        add(os.path.join(comp, "bibliografia", "geral.bib"), "geral.bib")
        add(os.path.join(RAIZ, "dados", "biblia", "livros.tsv"), "dados/biblia/livros.tsv")
        for u in sorted(usados):
            alvo = os.path.join(RAIZ, u.rstrip("/."))
            if os.path.isdir(alvo):
                for f in sorted(os.listdir(alvo)):
                    if os.path.isfile(os.path.join(alvo, f)):
                        add(os.path.join(alvo, f), f"{u.rstrip('/.')}/{f}")
            elif os.path.isfile(alvo) and not u.endswith("livros.tsv"):
                add(alvo, u)
        z.writestr(f"{nome}/latexmkrc", LATEXMKRC_OVERLEAF)
    print(f"ok -> {rel(zipdest)}\nNo Overleaf: New Project > Upload Project; depois Menu > Compiler > LuaLaTeX.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("listar", help="lista os cadernos")
    s.set_defaults(f=cmd_listar)

    s = sub.add_parser("verificar", help="confere se o TeX e as ferramentas estão instalados")
    s.set_defaults(f=cmd_verificar)

    s = sub.add_parser("compilar", help="compila cadernos e copia o PDF para saida/")
    s.add_argument("cadernos", nargs="*")
    s.add_argument("--todos", action="store_true")
    s.add_argument("-g", "--forcar", action="store_true", help="recompila mesmo sem mudanças")
    s.add_argument("-v", "--verboso", action="store_true", help="mostra a saída do LaTeX")
    s.set_defaults(f=cmd_compilar)

    s = sub.add_parser("limpar", help="apaga arquivos auxiliares da compilação")
    s.add_argument("cadernos", nargs="*")
    s.add_argument("--todos", action="store_true")
    s.add_argument("--pdf", action="store_true", help="apaga também o main.pdf do caderno")
    s.set_defaults(f=cmd_limpar)

    s = sub.add_parser("erros", help="mostra as mensagens de erro do main.log")
    s.add_argument("cadernos", nargs="*")
    s.add_argument("--todos", action="store_true")
    s.add_argument("-n", type=int, default=5, help="quantas mensagens mostrar")
    s.set_defaults(f=cmd_erros)

    s = sub.add_parser("novo", help="cria um caderno a partir de modelos/")
    s.add_argument("tipo", choices=["exegese", "livro", "tema"])
    s.add_argument("nome", help="nome da pasta (ex.: mt05-03-12), sigla do livro (ex.: lff) ou do tema (ex.: sangue)")
    s.add_argument("--titulo"); s.add_argument("--subtitulo"); s.add_argument("--incipit")
    s.add_argument("--autor"); s.add_argument("--tema", choices=["lapis", "purpura", "oliveira", "sepia"])
    s.set_defaults(f=cmd_novo)

    s = sub.add_parser("overleaf", help="gera um .zip do caderno para enviar ao Overleaf")
    s.add_argument("caderno"); s.add_argument("-o", help="arquivo .zip de saída")
    s.set_defaults(f=cmd_overleaf)

    a = p.parse_args()
    r = a.f(a)
    sys.exit(r or 0)


if __name__ == "__main__":
    main()
