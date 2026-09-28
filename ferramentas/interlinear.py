#!/usr/bin/env python3
"""
interlinear.py — gera dados de interlinear (TSV) a partir de bases abertas.

Fontes (baixadas e guardadas em ferramentas/.cache/ na primeira execução):
  Grego NT  : SBLGNT (CC BY 4.0) + morfologia MorphGNT (CC BY-SA 3.0)
              github.com/morphgnt/sblgnt  |  github.com/LogosBible/SBLGNT (aparato)
  Léxico gr.: MorphGNT morphological-lexicon (Strong + glosa de Dodson, domínio público)
  Hebraico/aramaico AT: OpenScriptures Hebrew Bible — WLC + morfologia (CC BY 4.0)
              github.com/openscriptures/morphhb
  Léxico hb.: OpenScriptures HebrewLexicon (Strong, domínio público)

Uso:
  python3 interlinear.py grego    Lc 6:20-26  -o ../dados/lc06_20-26.grc.tsv
  python3 interlinear.py hebraico Is 65:13-14 -o ../dados/is65_13-14.hbo.tsv
  python3 interlinear.py hebraico Dn 7:13     -o ../dados/dn07_13.arc.tsv   (aramaico bíblico)
  python3 interlinear.py concordancia σκιρτάω            (ocorrências no NT)
  python3 interlinear.py aparato  Lc 6:20-26             (variantes WH/Treg/NA28/RP)

O TSV gerado traz: ref, palavra, translit, lema, strong, morf (em português),
pt (vazio — preencha você!), en (glosa lexical de Dodson/Strong), var, freq_nt.
A coluna 'pt' fica vazia de propósito: escrever a própria glosa é parte do estudo.
Depende apenas da biblioteca padrão do Python 3.8+.
"""
import argparse
import collections, os, re, sys, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE, ".cache")
RAW = "https://raw.githubusercontent.com/"

# --------------------------------------------------------------------------
# Livros
# --------------------------------------------------------------------------
NT = [("Mt","Mt"),("Mc","Mk"),("Lc","Lk"),("Jo","Jn"),("At","Ac"),("Rm","Ro"),
      ("1Co","1Co"),("2Co","2Co"),("Gl","Ga"),("Ef","Eph"),("Fp","Php"),("Cl","Col"),
      ("1Ts","1Th"),("2Ts","2Th"),("1Tm","1Ti"),("2Tm","2Ti"),("Tt","Tit"),("Fm","Phm"),
      ("Hb","Heb"),("Tg","Jas"),("1Pe","1Pe"),("2Pe","2Pe"),("1Jo","1Jn"),("2Jo","2Jn"),
      ("3Jo","3Jn"),("Jd","Jud"),("Ap","Re")]
NT_SBL = {"Mt":"Matt","Mc":"Mark","Lc":"Luke","Jo":"John","At":"Acts","Rm":"Rom",
          "1Co":"1Cor","2Co":"2Cor","Gl":"Gal","Ef":"Eph","Fp":"Phil","Cl":"Col",
          "1Ts":"1Thess","2Ts":"2Thess","1Tm":"1Tim","2Tm":"2Tim","Tt":"Titus",
          "Fm":"Phlm","Hb":"Heb","Tg":"Jas","1Pe":"1Pet","2Pe":"2Pet","1Jo":"1John",
          "2Jo":"2John","3Jo":"3John","Jd":"Jude","Ap":"Rev"}
AT = {"Gn":"Gen","Êx":"Exod","Ex":"Exod","Lv":"Lev","Nm":"Num","Dt":"Deut","Js":"Josh",
      "Jz":"Judg","Rt":"Ruth","1Sm":"1Sam","2Sm":"2Sam","1Rs":"1Kgs","2Rs":"2Kgs",
      "1Cr":"1Chr","2Cr":"2Chr","Ed":"Ezra","Ne":"Neh","Et":"Esth","Jó":"Job","Jo_":"Job",
      "Sl":"Ps","Pv":"Prov","Ec":"Eccl","Ct":"Song","Is":"Isa","Jr":"Jer","Lm":"Lam",
      "Ez":"Ezek","Dn":"Dan","Os":"Hos","Jl":"Joel","Am":"Amos","Ob":"Obad","Jn":"Jonah",
      "Mq":"Mic","Na":"Nah","Hc":"Hab","Sf":"Zeph","Ag":"Hag","Zc":"Zech","Ml":"Mal"}


def baixar(caminho_raw, nome):
    os.makedirs(CACHE, exist_ok=True)
    destino = os.path.join(CACHE, nome)
    if not os.path.exists(destino):
        print(f"[baixando] {caminho_raw}", file=sys.stderr)
        urllib.request.urlretrieve(RAW + caminho_raw, destino)
    return destino


def intervalo(txt):
    """'6:20-26' | '6:20-7:2' | '7:13' -> ((c1,v1),(c2,v2))"""
    m = re.fullmatch(r"(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?", txt)
    if not m:
        sys.exit(f"Intervalo inválido: {txt}")
    c1, v1 = int(m[1]), int(m[2])
    c2 = int(m[3]) if m[3] else c1
    v2 = int(m[4]) if m[4] else v1
    return (c1, v1), (c2, v2)


# --------------------------------------------------------------------------
# GREGO
# --------------------------------------------------------------------------
POS_GR = {"A-":"adj.","C-":"conj.","D-":"adv.","I-":"interj.","N-":"subst.",
          "P-":"prep.","RA":"art.","RD":"pron. dem.","RI":"pron. interr./indef.",
          "RP":"pron. pess.","RR":"pron. rel.","V-":"v.","X-":"partíc."}
TEMPO = dict(P="pres.", I="imperf.", F="fut.", A="aor.", X="perf.", Y="m.-q.-perf.")
VOZ = dict(A="at.", M="méd.", P="pass.")
MODO = dict(I="ind.", D="imper.", S="subj.", O="opt.", N="inf.", P="part.")
CASO = dict(N="nom.", G="gen.", D="dat.", A="ac.", V="voc.")
NUM = dict(S="sg.", P="pl.")
GEN = dict(M="m.", F="f.", N="n.")


def morf_grego(pos, cod):
    p, t, v, m, c, n, g, d = cod
    if pos == "V-":
        if m == "P":   # particípio
            return f"part. {TEMPO[t]} {VOZ[v]} {CASO[c]} {GEN.get(g,'')} {NUM[n]}".replace("  ", " ")
        if m == "N":
            return f"inf. {TEMPO[t]} {VOZ[v]}"
        return f"v. {TEMPO[t]} {VOZ[v]} {MODO[m]} {p}{'sg' if n=='S' else 'pl'}"
    partes = [POS_GR.get(pos, pos)]
    if p != "-":
        partes.append(f"{p}ª")
    if c != "-": partes.append(CASO[c])
    if g != "-": partes.append(GEN[g])
    if n != "-": partes.append(NUM[n])
    if d != "-": partes.append({"C":"compar.","S":"superl."}[d])
    return " ".join(partes)


def lexico_grego():
    arq = baixar("morphgnt/morphological-lexicon/master/lexemes.yaml", "lexemes.yaml")
    lex, atual = {}, None
    for linha in open(arq, encoding="utf8"):
        if not linha.startswith(" ") and linha.rstrip().endswith(":"):
            atual = linha.rstrip()[:-1]
            lex[atual] = {}
        elif atual and ":" in linha:
            k, _, v = linha.strip().partition(":")
            lex[atual][k.strip()] = v.strip()
    return lex


def morphgnt(abrev):
    idx = [a for a, _ in NT].index(abrev)
    nome = f"{61+idx}-{NT[idx][1]}-morphgnt.txt"
    return baixar(f"morphgnt/sblgnt/master/{nome}", nome), idx + 1


def frequencias_nt():
    cont = collections.Counter()
    for abrev, _ in NT:
        arq, _ = morphgnt(abrev)
        for linha in open(arq, encoding="utf8"):
            cont[linha.split()[-1]] += 1
    return cont


def cmd_grego(a):
    arq, nlivro = morphgnt(a.livro)
    (c1, v1), (c2, v2) = intervalo(a.intervalo)
    lex = lexico_grego()
    freq = frequencias_nt() if a.freq else {}
    linhas = []
    for linha in open(arq, encoding="utf8"):
        ref, pos, cod, texto, palavra, norm, lema = linha.split()
        c, v = int(ref[2:4]), int(ref[4:6])
        if not ((c1, v1) <= (c, v) <= (c2, v2)):
            continue
        var = "1" if re.search("[⸀⸁⸂⸃⸄⸅]", texto) else ""
        texto = re.sub("[⸀⸁⸂⸃⸄⸅]", "", texto)
        if var:
            var = variante(a.livro, c, v, texto) or "ver aparato"
        info = lex.get(lema, {})
        strong = "G" + info["strongs"] if info.get("strongs") else ""
        linhas.append([f"{c}:{v}", texto, "", lema, strong, morf_grego(pos, cod),
                       "", info.get("gloss", ""), var, str(freq.get(lema, "")) if freq else ""])
    cab = ("# Fonte: SBLGNT (CC BY 4.0) + MorphGNT (CC BY-SA 3.0); glosa 'en' lexical (Dodson, dom. público)\n"
           f"# {a.livro} {a.intervalo} — gerado por ferramentas/interlinear.py\n")
    escrever(a.o, cab, linhas)


_APARATO = {}
def variante(abrev, c, v, palavra):
    """Resumo da entrada do aparato do SBLGNT para a palavra (ex.: 'RP: ἔλεγχον')."""
    livro = NT_SBL[abrev]
    if livro not in _APARATO:
        tab = collections.defaultdict(list)
        try:
            arq = baixar(f"LogosBible/SBLGNT/master/data/sblgntapp/text/{livro}.txt", f"app-{livro}.txt")
            for b in open(arq, encoding="utf8").read().split("\n\n"):
                linhas = b.strip().split("\n")
                m = re.match(r".*?(\d+):(\d+)\s*$", linhas[0])
                if m:
                    for l in linhas[1:]:
                        for e in l.split("•"):
                            e = re.sub(r"^\s*(\d+:)?\d+\s+", "", e).strip()
                            if e:
                                tab[(int(m[1]), int(m[2]))].append(e)
        except Exception:
            pass
        _APARATO[livro] = tab
    limpa = re.sub(r"[,.;·:\u0387]", "", palavra)
    for e in _APARATO[livro].get((c, v), []):
        if limpa and limpa in e:
            texto_sbl, _, outras = e.partition("]")
            partes = re.sub(r"\s+", " ", outras).strip().split(" ")
            siglas = []
            while partes and re.fullmatch(r"WH|Treg|NA28|NA|RP|NIV|SBL", partes[-1]):
                siglas.insert(0, partes.pop())
            leitura = " ".join(partes)
            return f"{' '.join(siglas)}: {leitura}" if siglas else leitura
    return ""


def cmd_concordancia(a):
    achados = []
    for abrev, _ in NT:
        arq, _ = morphgnt(abrev)
        for linha in open(arq, encoding="utf8"):
            campos = linha.split()
            if campos[-1] == a.lema:
                ref = campos[0]
                achados.append(f"{abrev} {int(ref[2:4])}:{int(ref[4:6])}  {re.sub('[⸀⸁⸂⸃⸄⸅]', '', campos[3])}")
    print(f"{a.lema}: {len(achados)} ocorrência(s) no NT (SBLGNT)")
    print("\n".join(achados))


def cmd_aparato(a):
    livro = NT_SBL[a.livro]
    arq = baixar(f"LogosBible/SBLGNT/master/data/sblgntapp/text/{livro}.txt", f"app-{livro}.txt")
    (c1, v1), (c2, v2) = intervalo(a.intervalo)
    bloco = open(arq, encoding="utf8").read().split("\n\n")
    for b in bloco:
        m = re.match(r"[^\n]*?(\d+):(\d+)\s*\n", b.strip() + "\n")
        if m and (c1, v1) <= (int(m[1]), int(m[2])) <= (c2, v2):
            print(b.strip(), "\n")
    print("Siglas: WH = Westcott-Hort (1881); Treg = Tregelles; NA28 = Nestle-Aland 28ª; "
          "RP = Robinson-Pierpont (texto bizantino, próximo — mas não idêntico — ao Textus Receptus).")


# --------------------------------------------------------------------------
# HEBRAICO / ARAMAICO (OSHB)
# --------------------------------------------------------------------------
TRONCO_H = dict(q="Qal", N="Nifal", p="Piel", P="Pual", h="Hifil", H="Hofal", t="Hitpael",
                o="Polel", O="Polal", r="Hitpolel", m="Poel", M="Poal", k="Palel",
                K="Pulal", Q="Qal pass.", l="Pilpel", L="Polpal", f="Hitpalpel",
                D="Nitpael", j="Pealal", i="Pilel", u="Hotpaal", c="Tifil", v="Hishtafel",
                w="Nitpalel", y="Nitpoel", z="Hitpoel")
TRONCO_A = dict(q="Peal", Q="Peil", u="Hitpeel", p="Pael", P="Hitpaal", M="Hitpaal",
                a="Afel", h="Hafel", s="Safel", e="Shafel", H="Hofal", i="Itpeel",
                t="Hishtafal", v="Ishtafal", w="Hitafal", o="Polel", z="Itpoel",
                f="Poel", l="Palpel", L="Itpalpal", O="Polal", m="Itpeel", k="Pual?")
FORMA_V = dict(p="perf. (qatal)", q="perf. consec.", i="imperf. (yiqtol)",
               w="imperf. consec.", h="cohort.", j="juss.", v="imper.",
               r="part. at.", s="part. pass.", a="inf. abs.", c="inf. constr.")
PES = {"1":"1ª","2":"2ª","3":"3ª"}
GEN_H = dict(m="m.", f="f.", b="m./f.", c="comum")
NUM_H = dict(s="sg.", p="pl.", d="dual")
EST_H = dict(a="abs.", c="constr.", d="det.")
PART_H = dict(a="partíc. afirm.", d="art.", e="partíc. exort.", i="partíc. interr.",
              j="interj.", m="partíc. dem.", n="neg.", o="marca obj. dir.", r="rel.")
PRON_H = dict(d="pron. dem.", f="pron. indef.", i="pron. interr.", p="pron. pess.", r="pron. rel.")


def pgn(s):
    out = []
    for ch in s:
        if ch in PES: out.append(PES[ch])
        elif ch in GEN_H: out.append(GEN_H[ch])
        elif ch in NUM_H: out.append(NUM_H[ch])
    return " ".join(out)


def seg_morf(seg, lingua):
    if not seg: return ""
    p, r = seg[0], seg[1:]
    if p == "V":
        tronco = (TRONCO_A if lingua == "A" else TRONCO_H).get(r[0], r[0])
        forma = FORMA_V.get(r[1], r[1]) if len(r) > 1 else ""
        resto = r[2:]
        if r[1:2] in ("r", "s"):   # particípio: gênero número estado
            return f"v. {tronco} {forma} {GEN_H.get(resto[0:1],'')} {NUM_H.get(resto[1:2],'')} {EST_H.get(resto[2:3],'')}".strip()
        return f"v. {tronco} {forma} {pgn(resto)}".strip()
    if p == "N":
        tipo = {"c":"subst.","g":"gentílico","p":"n. próprio"}.get(r[:1], "subst.")
        if r[:1] == "p": return tipo
        return f"{tipo} {GEN_H.get(r[1:2],'')} {NUM_H.get(r[2:3],'')} {EST_H.get(r[3:4],'')}".strip()
    if p == "A":
        return f"adj. {GEN_H.get(r[1:2],'')} {NUM_H.get(r[2:3],'')} {EST_H.get(r[3:4],'')}".strip()
    if p == "S":
        if r[:1] == "p": return f"suf. {pgn(r[1:])}"
        return {"d":"he direcional","h":"he parag.","n":"nun parag."}.get(r[:1], "suf.")
    if p == "P": return f"{PRON_H.get(r[:1],'pron.')} {pgn(r[1:])}".strip()
    if p == "T": return PART_H.get(r[:1], "partíc.")
    if p == "R": return "prep. + art." if r[:1] == "d" else "prep."
    if p == "C": return "conj."
    if p == "D": return "adv."
    return seg


def morf_hebraico(cod):
    lingua, corpo = cod[0], cod[1:]
    return " + ".join(seg_morf(s, lingua) for s in corpo.split("/"))


def lexico_hebraico():
    arq = baixar("openscriptures/HebrewLexicon/master/HebrewStrong.xml", "HebrewStrong.xml")
    xml = open(arq, encoding="utf8").read()
    lex = {}
    for m in re.finditer(r'<entry id="H(\d+)">(.*?)</entry>', xml, re.S):
        w = re.search(r'<w [^>]*>(.*?)</w>', m[2])
        d = re.search(r'<def>(.*?)</def>', m[2])
        lex[m[1]] = (w[1] if w else "", d[1] if d else "")
    return lex


def cmd_hebraico(a):
    livro = AT.get(a.livro) or sys.exit(f"Livro do AT desconhecido: {a.livro}")
    arq = baixar(f"openscriptures/morphhb/master/wlc/{livro}.xml", f"{livro}.xml")
    (c1, v1), (c2, v2) = intervalo(a.intervalo)
    lex = lexico_hebraico()
    xml = open(arq, encoding="utf8").read()
    linhas, lingua = [], None
    for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)"[^>]*>(.*?)</verse>', xml, re.S):
        c, v = int(m[1]), int(m[2])
        if not ((c1, v1) <= (c, v) <= (c2, v2)):
            continue
        for w in re.finditer(r'<w ([^>]*)>(.*?)</w>|<seg type="x-maqqef">', m[3]):
            if w[1] is None:            # maqqef: gruda na palavra anterior
                if linhas: linhas[-1][1] += "־"
                continue
            att = dict(re.findall(r'(\w+)="([^"]*)"', w[1]))
            cod = att.get("morph", "")
            lingua = lingua or cod[:1]
            nums = re.findall(r"\d+", att.get("lemma", ""))
            num = nums[-1] if nums else ""
            lema, glosa = lex.get(num, ("", ""))
            linhas.append([f"{c}:{v}", w[2].replace("/", ""), "", lema,
                           f"H{num}" if num else "", morf_hebraico(cod), "", glosa, "", ""])
    nome_l = "aramaico bíblico" if lingua == "A" else "hebraico"
    cab = (f"# Fonte: OpenScriptures Hebrew Bible — WLC + morfologia (CC BY 4.0); léxico Strong (dom. público)\n"
           f"# {a.livro} {a.intervalo} ({nome_l}) — translit. a preencher manualmente\n")
    escrever(a.o, cab, linhas)


# --------------------------------------------------------------------------
def escrever(destino, cabecalho, linhas):
    colunas = ["ref","palavra","translit","lema","strong","morf","pt","en","var","freq_nt"]
    txt = cabecalho + "\t".join(colunas) + "\n" + "\n".join("\t".join(l) for l in linhas) + "\n"
    if destino:
        with open(destino, "w", encoding="utf8") as f:
            f.write(txt)
        print(f"[ok] {len(linhas)} palavras -> {destino}", file=sys.stderr)
    else:
        sys.stdout.write(txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("grego");    g.add_argument("livro"); g.add_argument("intervalo"); g.add_argument("-o")
    g.add_argument("--sem-freq", dest="freq", action="store_false", help="não calcular frequência no NT")
    h = sub.add_parser("hebraico"); h.add_argument("livro"); h.add_argument("intervalo"); h.add_argument("-o")
    c = sub.add_parser("concordancia"); c.add_argument("lema")
    p = sub.add_parser("aparato");  p.add_argument("livro"); p.add_argument("intervalo")
    a = ap.parse_args()
    {"grego": cmd_grego, "hebraico": cmd_hebraico, "concordancia": cmd_concordancia,
     "aparato": cmd_aparato}[a.cmd](a)


if __name__ == "__main__":
    main()
