# Manual do repositório de estudos bíblicos

Este repositório guarda todos os seus cadernos de estudo num só lugar,
com uma identidade visual e um conjunto de ferramentas comuns. Há dois
tipos de caderno:

- **exegese** — estudo aprofundado de uma passagem, em 7 etapas, com
  interlinear grego / hebraico / aramaico / siríaco (ex.: Lucas 6:20–26);
- **livro** — acompanhamento de uma publicação lição a lição, com os textos
  bíblicos de cada lição, espaço para anotações, índice de textos e registro
  de leitura (ex.: *Seja Feliz Para Sempre!*);
- **tema** — estudo de um assunto em toda a Bíblia, partindo de uma pergunta
  (ex.: *O que a Bíblia diz sobre o sangue?*, *Quem é Jesus?*), com
  vocabulário no original, todas as ocorrências, catálogo de textos por grupo,
  fichas de leitura no contexto e síntese em proposições.

Sumário: [1. Instalação](#1-instalação) · [2. Primeiros passos](#2-primeiros-passos) ·
[3. Estrutura](#3-estrutura) · [4. Compilar](#4-compilar) ·
[5. Caderno de exegese](#5-novo-caderno-de-exegese) ·
[6. Caderno de livro](#6-novo-caderno-de-estudo-de-livro) ·
[7. Caderno temático](#7-novo-caderno-de-estudo-temático) ·
[8. Formato dos dados](#8-formato-dos-dados) · [9. Overleaf](#9-overleaf) ·
[10. Git e GitHub](#10-git-e-github) · [11. Problemas comuns](#11-problemas-comuns)

---

## 1. Instalação

Você precisa de **TeX Live** (LuaLaTeX, biber, latexmk, makeindex),
**Python 3** e, só para extrair dados de PDFs de livros, **Poppler** (`pdftotext`).

**Linux (Debian/Ubuntu)**

```bash
sudo apt install texlive-luatex texlive-latex-extra texlive-lang-greek \
  texlive-lang-other texlive-lang-portuguese texlive-bibtex-extra biber \
  latexmk python3 poppler-utils git
```

(Ou instale o TeX Live completo: `sudo apt install texlive-full`.)

**Windows** — instale o [TeX Live](https://tug.org/texlive/) (já traz Perl,
necessário para o latexmk), o [Python 3](https://www.python.org/) (marque
*Add to PATH*) e o Git. Para o `pdftotext`, instale o Poppler (por exemplo,
`scoop install poppler` ou `choco install poppler`). Use `python` no lugar de
`python3` nos comandos deste manual. O MiKTeX também funciona, mas exige
instalar o Perl à parte.

**macOS** — instale o [MacTeX](https://tug.org/mactex/) e, com o Homebrew,
`brew install python poppler git`.

Confira a instalação:

```bash
python3 estudos.py verificar
```

## 2. Primeiros passos

```bash
git clone <endereço-do-seu-repositório> estudos-biblicos
cd estudos-biblicos
python3 estudos.py listar            # mostra os cadernos
python3 estudos.py compilar --todos  # compila tudo; PDFs em saida/
```

A primeira compilação é lenta (o LuaLaTeX monta o cache das fontes). As
seguintes levam de 20 s a 1 min por caderno.

## 3. Estrutura

```
estudos-biblicos/
├── estudos.py               ferramenta principal (listar, compilar, novo, overleaf…)
├── estudos.ini              valores padrão (autor, série, epígrafe, tema)
├── MANUAL.md  README.md  Makefile
├── .estudos-raiz            marca a raiz — não apague
├── compartilhado/           comum a todos os cadernos
│   ├── estilo/              estudobiblico.sty (visual) · interlinear.sty/.lua · livro.sty/.lua · tema.sty/.lua
│   ├── fontes/              fontes livres (SIL OFL)
│   ├── bibliografia/geral.bib
│   ├── indice.ist · indice-termos.ist
│   ├── latexmkrc            configuração do latexmk
│   └── latexmkrc-caderno    copiado para cada caderno
├── dados/
│   ├── biblia/              livros.tsv + textos originais palavra por palavra (*.grc/.hbo/.arc/.syr.tsv)
│   ├── livros/<sigla>/      licoes.tsv + textos.tsv de cada livro estudado
│   └── temas/<sigla>/       textos.tsv + vocabulario.tsv + ocorrencias.tsv de cada tema
├── ferramentas/
│   ├── interlinear.py       gera dados do texto original (SBLGNT, OSHB) e concordância
│   ├── livro.py             extrai índice e referências bíblicas do PDF de um livro
│   └── tema.py              ocorrências e vocabulário de um tema; confere a lista de textos
├── modelos/                 esqueletos usados por `estudos.py novo`
│   ├── exegese/
│   ├── livro/
│   └── tema/
├── cadernos/
│   ├── exegese/lc06-20-26/  main.tex · config.tex · capitulos/ · latexmkrc
│   ├── livros/lff/          main.tex · config.tex · capitulos/ · licoes/ · bibliografia.bib · latexmkrc
│   └── temas/sangue/        main.tex · config.tex · capitulos/ · bibliografia.bib · latexmkrc
├── referencias/             PDFs das publicações (NÃO vão para o git)
└── saida/                   PDFs compilados e zips do Overleaf (NÃO vão para o git)
```

**Regra de ouro:** o que é comum fica em `compartilhado/` e `dados/`; o que é
de um estudo fica na pasta do caderno. Uma melhoria no estilo vale para todos
os cadernos na próxima compilação.

Cada caderno tem um `latexmkrc` de poucas linhas que sobe as pastas até achar
`.estudos-raiz` e carrega `compartilhado/latexmkrc`. É isso que permite
escrever `\usepackage{estilo/estudobiblico}` e `\interlinear{dados/biblia/…}`
em qualquer caderno, sem caminhos relativos.

## 4. Compilar

**Com a ferramenta (recomendado)**

```bash
python3 estudos.py compilar cadernos/livros/lff      # um caderno
python3 estudos.py compilar lff                      # aceita só o nome da pasta
python3 estudos.py compilar --todos                  # todos
python3 estudos.py compilar lff -v                   # mostra a saída do LaTeX
python3 estudos.py limpar --todos                    # apaga os arquivos auxiliares
```

O PDF fica na pasta do caderno (`main.pdf`) e é copiado para
`saida/<tipo>-<nome>.pdf`.

**Direto com o latexmk**

```bash
cd cadernos/exegese/lc06-20-26
latexmk main.tex          # compila (LuaLaTeX + biber + índices)
latexmk -pvc main.tex     # recompila sozinho a cada gravação e abre o visualizador
latexmk -c                # limpa
```

> Não use `latexmk -pdf`: essa opção força o pdfLaTeX, e os cadernos precisam
> do LuaLaTeX. A configuração do repositório já escolhe o motor certo.

**No VS Code** (extensão *LaTeX Workshop*): o arquivo `.vscode/settings.json`
do repositório já configura a receita. Abra a pasta do repositório, abra o
`main.tex` do caderno e grave (Ctrl+S).

**Para compilar mais rápido enquanto escreve:** no `main.tex` de um caderno
de exegese, descomente `\includeonly{capitulos/…}` e deixe só a etapa em que
está trabalhando. No caderno de livro, use `\livroLicoes{1-12}` no `config.tex`.

## 5. Novo caderno de exegese

```bash
python3 estudos.py novo exegese mt05-03-12 --titulo "Mateus 5:3–12" \
  --subtitulo "As bem-aventuranças" --incipit "Μακάριοι οἱ πτωχοὶ τῷ πνεύματι"
```

Isso cria `cadernos/exegese/mt05-03-12/` com as 7 etapas em esqueleto (cada
uma com o objetivo e as seções sugeridas). Depois:

1. **Gere os dados do texto original** (a partir da raiz):

   ```bash
   python3 ferramentas/interlinear.py grego    Mt 5:3-12  -o dados/biblia/mt05_03-12.grc.tsv
   python3 ferramentas/interlinear.py hebraico Is 61:1-3  -o dados/biblia/is61_01-03.hbo.tsv
   python3 ferramentas/interlinear.py hebraico Dn 7:13-14 -o dados/biblia/dn07_13-14.arc.tsv
   python3 ferramentas/interlinear.py aparato  Mt 5:3-12          # variantes (WH, Treg, NA28, RP)
   python3 ferramentas/interlinear.py concordancia μακάριος       # ocorrências no NT
   ```

   A primeira execução baixa as bases (SBLGNT, MorphGNT, OSHB) para
   `ferramentas/.cache/`. A coluna `pt` (glosa em português) vem vazia de
   propósito: escrever a glosa é parte do estudo. No hebraico, preencha também
   a transliteração. Use a numeração hebraica dos versículos (ex.: Sl 83:18 em
   português = 83:19 no hebraico).

2. **Use os dados nos capítulos:**

   ```latex
   \textooriginal{dados/biblia/mt05_03-12.grc.tsv}
   \interlinear[de=5:3, ate=5:6, modo=completo, titulo={Mt 5:3–6}]{dados/biblia/mt05_03-12.grc.tsv}
   \tabelamorfologica[de=5:3, ate=5:3]{dados/biblia/mt05_03-12.grc.tsv}
   \vocabulario[minimo=2]{dados/biblia/mt05_03-12.grc.tsv}
   ```

3. **Escreva** nas caixas: `objetivo`, `traducao`, `nota`, `pergunta`,
   `alerta`, `variante`, `lexico`, `citacao`, `aplicacao`. Texto em outras
   línguas: `\gr{…}`, `\hb{…}`, `\arc{…}`, `\sy{…}`; referência: `\rb{Mt 5:3}`;
   versículo: `\vs{3}`; nota na margem: `\margem{…}`.

4. **Cite** obras de `compartilhado/bibliografia/geral.bib` com
   `\parencite{fee2002}` ou `\textcite{bovon2002}`. Acrescente lá as obras que
   servem a vários estudos.

## 6. Novo caderno de estudo de livro

O modelo é o mesmo para qualquer livro: muda só a pasta de dados.

```bash
# 1. copie o PDF para referencias/ (fica fora do git)
# 2. crie o caderno
python3 estudos.py novo livro lff --titulo "Seja Feliz Para Sempre!"
# 3. índice das lições (detecta o número de 2 dígitos no alto da página)
python3 ferramentas/livro.py indice referencias/lff_TPO.pdf -o dados/livros/lff --deslocamento 2
# 4. CONFIRA dados/livros/lff/licoes.tsv e corrija os títulos (o PDF pode perder acentos)
# 5. textos bíblicos de cada lição
python3 ferramentas/livro.py textos referencias/lff_TPO.pdf -o dados/livros/lff --ultima 258
python3 ferramentas/livro.py resumo dados/livros/lff        # textos e livros mais citados
# 6. compile
python3 estudos.py compilar lff
```

- `--deslocamento` é a diferença entre a página do PDF e a página impressa
  (no *lff*, a lição 01 começa na página 7 do PDF e na página 5 impressa: 2).
- `--ultima` é a última página do PDF que ainda pertence à última lição.
- Se o livro tiver outro formato e o `indice` não funcionar, escreva o
  `licoes.tsv` à mão (basta `num`, `parte`, `titulo`, `pagina`, `pagina_pdf`) e
  rode só o `textos`.

**Suas anotações.** Cada lição sai com a ficha, a tabela de textos e campos
para escrever. Para anotar no computador, crie `licoes/NN.tex` na pasta do
caderno (NN = número com dois dígitos). O conteúdo entra na lição no lugar
dos campos em branco. Exemplo:

```latex
\begin{campo}{Ideia central}
A resposta da lição, com as minhas palavras.
\end{campo}
\begin{campo}{Texto em foco: 2 Timóteo 3:16}
\interlinear[modo=leitura]{dados/biblia/2tm03_16-17.grc.tsv}
\end{campo}
\EBlivcampo[3]{Dúvidas para pesquisar}{}      % campo com linhas em branco
```

Veja `cadernos/livros/lff/licoes/01.tex` e `04.tex`.

**Opções no `config.tex`:** `\livroModo` (`impresso` com linhas e caixinhas,
ou `digital` só com o que você escreveu), `\livroLinhas` (linhas por campo),
`\livroLicoes` (ex.: `1-12` para imprimir só a Parte 1), `\livroUnidade`
(`Lição`, `Capítulo`, `Artigo`…), tema e papel.

## 7. Novo caderno de estudo temático

Um estudo temático parte de uma pergunta e procura a resposta em toda a
Bíblia. O caderno segue sete etapas: a pergunta, palavras e conceitos, os
textos, leitura no contexto, desenvolvimento ao longo da Bíblia, diálogo e
síntese.

```bash
# 1. crie o caderno (sigla curta, sem espaços)
python3 estudos.py novo tema sangue --titulo "O que a Bíblia diz sobre o sangue?" \
  --incipit "περὶ τοῦ αἵματος"
# 2. todas as ocorrências das palavras do tema (números de Strong: H = hebraico, G = grego)
python3 ferramentas/tema.py ocorrencias H1818 G129 -o dados/temas/sangue
# 3. vocabulário pré-preenchido (complete a transliteração e o sentido em português)
python3 ferramentas/tema.py vocabulario H1818 H5315 G129 -o dados/temas/sangue
# 4. escreva a sua lista de estudo em dados/temas/sangue/textos.tsv
# 5. confira a lista e veja que ocorrências ainda não leu
python3 ferramentas/tema.py conferir dados/temas/sangue
# 6. compile
python3 estudos.py compilar sangue
```

**Como achar os números de Strong.** Gere um texto em que a palavra aparece e
veja a coluna `strong` (ex.: `python3 ferramentas/interlinear.py grego Hb 9:22`
mostra `αἷμα G129`); ou use uma concordância impressa ou em linha.

**A lista de estudo (`textos.tsv`)** é o coração do caderno. Cada linha tem:

| coluna | conteúdo |
|---|---|
| `ref` | `Lv 17:10-14`, `At 15:28, 29` ou `Levítico 17:10-14` |
| `grupo` | a categoria que **você** cria (ex.: *Sangue e vida*); os grupos aparecem na ordem da 1.ª linha de cada um |
| `peso` | `central`, `apoio`, `dificil` ou vazio (no modo impresso, vazio mostra caixinhas para decidir à mão) |
| `nota` | observação curta (opcional) |

**Comandos para os capítulos:**

```latex
\vocabulariodotema                         % tabela das palavras do tema
\textosdotema                              % catálogo por grupo
\textosdotema[ordem=biblica]               % em ordem bíblica, com o grupo
\textosdotema[peso=dificil]                % só os difíceis (use na Etapa 6)
\textosdotema[grupo={Sangue e vida}]       % um grupo só
\distribuicaodotema                        % textos e ocorrências por parte da Bíblia
\ocorrenciasdotema[H1818]                  % todas as ocorrências (apêndice)
\tema{Lv 17:11}                            % escreve "Levítico 17:11" e põe no índice
\begin{fichatexto}[Sangue e vida]{Lv 17:11}  % estudo de um texto no contexto
  \begin{campo}{Contexto} ... \end{campo}
  \interlinear{dados/biblia/lv017_11.hbo.tsv}
  \campovazio[3]{Contribuição para o tema}{}   % campo com linhas em branco
\end{fichatexto}
\proposicao{Afirmação que os textos sustentam.}{Lv 17:11; Hb 9:22}
```

**Temas guiados por conceito.** Em perguntas como *Quem é Jesus?* o assunto
não depende de uma palavra só. Use a concordância para as palavras-chave
(títulos como Χριστός G5547, κύριος G2962, υἱός G5207, λόγος G3056), mas
monte a lista também por conceitos (o que Jesus diz de si mesmo, o que
outros dizem dele, o que ele faz, a relação com o Pai, o papel futuro) e
deixe a coluna `grupo` refletir isso. O capítulo *Como fazer um estudo
temático* do caderno explica o cuidado de não confundir palavra e conceito.

**Opções no `config.tex`:** `\temaPergunta`, `\temaDados`, `\temaModo`
(`impresso` ou `digital`), `\temaLinhas`, tema de cores e papel.

## 8. Formato dos dados

Todos os dados são **TSV** (texto com colunas separadas por tabulação, UTF-8).
Linhas que começam com `#` são comentários. Podem ser editados em qualquer
editor de texto ou planilha (salve como "texto separado por tabulações").

**Texto original** (`dados/biblia/*.grc|hbo|arc|syr.tsv`) — uma palavra por linha:

| coluna | conteúdo |
|---|---|
| `ref` | capítulo:versículo |
| `palavra` | forma no texto |
| `translit` | transliteração (vazio no grego = gerada automaticamente) |
| `lema`, `strong` | forma de dicionário e número de Strong |
| `morf` | análise morfológica em português |
| `pt`, `en` | glosas; `[palavra]` = implícita (sai em cinza) |
| `var` | variante textual (ex.: `RP: ταῦτα`); marca a palavra com ° |
| `freq_nt` | ocorrências do lema no NT |

A língua é deduzida da extensão: `.grc` grego, `.hbo` hebraico, `.arc`
aramaico, `.syr` siríaco (os três últimos da direita para a esquerda).

**Livro** (`dados/livros/<sigla>/`):

- `licoes.tsv`: `num`, `parte`, `titulo`, `pagina`, `pagina_pdf`
- `textos.tsv`: `licao`, `secao` (ponto da lição), `ref`, `abrev`, `ordem`
  (nº do livro bíblico), `cap`, `vers`, `tipo` (`leia` ou `citado`)

**Tema** (`dados/temas/<sigla>/`):

- `textos.tsv`: `ref`, `grupo`, `peso`, `nota` (ver seção 7)
- `vocabulario.tsv`: `lingua`, `lema`, `translit`, `strong`, `ocorrencias`, `sentido`, `nota`
- `ocorrencias.tsv`: `strong`, `lema`, `ref`, `ordem`, `cap`, `vers`, `forma` (gerado;
  no AT, numeração hebraica)

**Bíblia** (`dados/biblia/livros.tsv`): os 66 livros com abreviação, nome,
número de capítulos, testamento, grupo e grafias alternativas (usadas pelo
`livro.py` para reconhecer referências).

## 9. Overleaf

```bash
python3 estudos.py overleaf cadernos/livros/lff     # gera saida/livros-lff-overleaf.zip
```

O zip contém o caderno com tudo de que ele precisa (estilo, fontes, dados,
bibliografia) numa estrutura plana. No Overleaf: *New Project → Upload
Project*, escolha o zip e depois *Menu → Compiler → **LuaLaTeX***. No plano
gratuito, o tempo de compilação pode estourar: use `\includeonly` ou
`\livroLicoes` para compilar partes.

As alterações feitas no Overleaf não voltam sozinhas para o repositório:
copie de volta os arquivos do caderno que você editou (ou use a integração
do Overleaf com o GitHub, nos planos pagos).

## 10. Git e GitHub

**Crie o repositório como privado.** Ele contém textos de traduções modernas e
dados de publicações protegidas por direitos autorais, para uso pessoal.

```bash
git init
git add .
git commit -m "Repositório de estudos: exegese Lc 6:20-26 e estudo de livro lff"
git branch -M main
git remote add origin git@github.com:<usuario>/estudos-biblicos.git
git push -u origin main
```

Rotina sugerida: um commit por sessão de estudo, com mensagem descritiva
(`lff: anotações das lições 05-06`, `lc06: etapa 4 revisada`). O `.gitignore`
já exclui PDFs gerados, arquivos auxiliares, o cache das ferramentas e a
pasta `referencias/`.

**Compilação automática (opcional):** o arquivo
`.github/workflows/compilar.yml` compila todos os cadernos no GitHub a cada
push e guarda os PDFs na aba *Actions*. Em repositório privado isso consome os
minutos gratuitos do plano; apague o arquivo se não quiser usar.

## 11. Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `Este projeto precisa do LuaLaTeX` | foi usado o pdfLaTeX (ex.: `latexmk -pdf`). Use `latexmk main.tex` ou `estudos.py compilar`. |
| `Não achei a raiz do repositório` | o caderno está fora de `cadernos/` ou o arquivo `.estudos-raiz` foi apagado. |
| `File 'estilo/estudobiblico.sty' not found` | compilou sem o latexmk (ex.: `lualatex main.tex` direto). Use o latexmk, que configura os caminhos. |
| Fonte não encontrada | confira se `compartilhado/fontes/` tem os arquivos `.otf/.ttf`. |
| Bibliografia vazia ou `??` | rode de novo; se persistir, veja `main.blg` (erro no `.bib`). |
| Índice vazio | o `makeindex` não rodou: compile com o latexmk, que o chama. |
| `Interlinear: arquivo … não encontrado` | caminho do TSV errado; os caminhos são relativos à raiz (`dados/biblia/…`). |
| Hebraico com números de versículo trocados | use a numeração do texto hebraico ao gerar os dados. |
| Compilação lenta | normal com LuaLaTeX e muitas fontes; compile por partes (seção 4). |
| `Estudo temático: arquivo … não encontrado` | confira `\temaDados` no `config.tex` e se `textos.tsv` existe na pasta do tema. |
| Referência não aparece no catálogo ou no índice | rode `tema.py conferir`: ele aponta abreviações não reconhecidas (use as de `dados/biblia/livros.tsv`). |
