# Manual do repositório de estudos bíblicos

Do zero ao fim: instalar, entender, usar, modificar e manter.

Este repositório guarda todos os seus cadernos de estudo num só lugar, com uma
identidade visual comum, dados em arquivos de texto simples e ferramentas que
geram automaticamente o que seria trabalhoso digitar (interlineares, índices,
listas de ocorrências, tabelas).

**Sumário**

| | |
|---|---|
| [1. Ideia geral](#1-ideia-geral) | o que o repositório faz e por quê |
| [2. Instalação](#2-instalação) | Linux/WSL, Windows, macOS |
| [3. Primeiro uso](#3-primeiro-uso) | do zip ao primeiro PDF |
| [4. Como funciona uma compilação](#4-como-funciona-uma-compilação) | o que acontece por dentro |
| [5. Estrutura do repositório](#5-estrutura-do-repositório) | pasta por pasta, arquivo por arquivo |
| [6. Os três tipos de caderno](#6-os-três-tipos-de-caderno) | quando usar cada um |
| [7. estudos.py](#7-estudospy--a-ferramenta-do-repositório) | todos os comandos |
| [8. Compilar](#8-compilar) | latexmk, VS Code, velocidade |
| [9. Caderno de exegese](#9-caderno-de-exegese) | passo a passo |
| [10. Caderno de estudo de livro](#10-caderno-de-estudo-de-livro) | passo a passo |
| [11. Caderno temático](#11-caderno-temático) | passo a passo |
| [12. Referência de comandos LaTeX](#12-referência-de-comandos-latex) | tudo o que você escreve nos capítulos |
| [13. Ferramentas de linha de comando](#13-ferramentas-de-linha-de-comando) | interlinear.py, livro.py, tema.py |
| [14. Formato dos dados](#14-formato-dos-dados) | todos os TSV |
| [15. Personalizar](#15-personalizar) | cores, fontes, margens, caixas, capa |
| [16. Bibliografia e índices](#16-bibliografia-e-índices) | biblatex e imakeidx |
| [17. Overleaf](#17-overleaf) | exportar e compilar na nuvem |
| [18. Git e GitHub](#18-git-e-github) | versionar e sincronizar |
| [19. Manutenção](#19-manutenção-do-repositório) | renomear, mover, apagar, backup |
| [20. Estender o repositório](#20-estender-o-repositório) | criar um tipo novo de caderno |
| [21. Problemas comuns](#21-problemas-comuns) | erros e soluções |
| [22. Licenças e cuidados](#22-licenças-e-cuidados) | o que pode e o que não pode ser publicado |

---

## 1. Ideia geral

O repositório é feito de quatro camadas independentes. Entender essa separação
explica quase tudo o que vem depois.

| Camada | O que é | Onde fica |
|---|---|---|
| **Dados** | texto bíblico palavra por palavra, listas de textos, índices de livros — arquivos TSV que você pode abrir no editor ou numa planilha | `dados/` |
| **Ferramentas** | programas em Python que *geram* dados a partir de bases abertas e do PDF das publicações | `ferramentas/` |
| **Estilo** | a aparência e os comandos disponíveis (cores, fontes, caixas, interlinear, tabelas) | `compartilhado/estilo/` |
| **Conteúdo** | o seu estudo: os capítulos de cada caderno | `cadernos/<tipo>/<nome>/capitulos/` |

Três consequências práticas:

1. **Uma melhoria no estilo vale para todos os cadernos** na próxima compilação.
2. **Os mesmos dados servem a vários cadernos.** O interlinear de 2 Tm 3:16
   pode aparecer num caderno de exegese, numa lição de um caderno de livro e na
   ficha de um caderno temático.
3. **Você escreve pouco.** Tabelas, índices, listas de ocorrências e
   interlineares são montados a partir dos TSV; você escreve o texto do estudo.

---

## 2. Instalação

São necessários: **TeX Live** (LuaLaTeX, latexmk, biber, makeindex), **Python 3**
e, apenas para extrair dados do PDF de um livro, o **Poppler** (`pdftotext`).
O **Git** e o **GitHub CLI** são opcionais, para versionar.

### Linux (Debian/Ubuntu) e WSL

```bash
sudo apt update
sudo apt install texlive-luatex texlive-latex-extra texlive-lang-greek \
  texlive-lang-other texlive-lang-portuguese texlive-bibtex-extra biber \
  latexmk python3 poppler-utils git gh
```

Se der algum erro de pacote faltando, a alternativa segura é `sudo apt install texlive-full`
(ocupa vários GB, mas evita surpresas).

> **WSL:** trabalhe com o repositório dentro do sistema de arquivos do Linux
> (`~/estudos-biblicos`), não em `/mnt/c/...`. Em `/mnt/c` cada leitura de arquivo
> passa por uma ponte com o Windows, e a compilação pode ficar várias vezes mais
> lenta. Para abrir a pasta no Explorer: `explorer.exe .`

### Windows (PowerShell)

```powershell
winget install TeXLive.TeXLive      # ou baixe o instalador em tug.org/texlive
winget install Python.Python.3.12
winget install Git.Git GitHub.cli
# pdftotext (só para cadernos de livro):
winget install oschwartz10612.Poppler   # ou: scoop install poppler
```

Feche e reabra o terminal para o PATH ser atualizado. Use `python` no lugar de
`python3`. O MiKTeX também serve, mas exige instalar o Perl à parte (o latexmk
é um script Perl).

### macOS

```bash
brew install --cask mactex          # ou basictex, menor
brew install python poppler git gh
```

### Conferir

```bash
python3 estudos.py verificar
```

Deve listar `lualatex`, `latexmk`, `biber`, `makeindex` e `pdftotext` como
encontrados. O que faltar aparece como `FALTA`.

---

## 3. Primeiro uso

```bash
cd ~                                  # ou onde quiser guardar
unzip estudos-biblicos.zip
cd estudos-biblicos

python3 estudos.py verificar
python3 estudos.py listar             # quais cadernos existem
python3 estudos.py compilar --todos   # PDFs em saida/
```

A primeira compilação é a mais lenta: o LuaLaTeX monta o cache das fontes. As
seguintes levam de 20 s a 1 min por caderno.

Se você também recebeu um zip de atualização, descompacte-o **por cima** da
pasta, substituindo os arquivos:

```bash
unzip -o atualizacao-estudo-tematico.zip
```

---

## 4. Como funciona uma compilação

Vale conhecer a sequência, porque quase todo erro aparece num destes passos.

```
main.tex
  ├─ \input{config}                 título, autor, tema de cores, papel…
  ├─ \usepackage{estilo/estudobiblico}   visual + comandos comuns
  ├─ \usepackage{estilo/interlinear}     (exegese)  → estilo/interlinear.lua
  ├─ \usepackage{estilo/livro}           (livro)    → estilo/livro.lua
  ├─ \usepackage{estilo/tema}            (tema)     → estilo/tema.lua
  └─ \include{capitulos/…}          o seu texto
```

1. Você roda `latexmk` (direto ou pelo `estudos.py`).
2. O `latexmkrc` do caderno sobe as pastas até achar o arquivo `.estudos-raiz`,
   descobre a raiz do repositório e carrega `compartilhado/latexmkrc`.
3. Esse arquivo define o motor (**LuaLaTeX**) e acrescenta
   `compartilhado/` e a raiz aos caminhos de busca do TeX. É por isso que
   `\usepackage{estilo/estudobiblico}` e `dados/biblia/xxx.tsv` funcionam de
   qualquer caderno, sem caminhos relativos.
4. O LuaLaTeX roda. Ao encontrar `\interlinear{...}`, o código Lua lê o TSV e
   devolve o texto já formatado ao LaTeX — os dados **não** entram no `.tex`.
5. O latexmk chama o **biber** (bibliografia) e o **makeindex** (índices) e
   repete o LuaLaTeX até o documento estabilizar (referências, sumário, índices).
6. O PDF fica ao lado do `main.tex`; o `estudos.py` copia uma cópia para `saida/`.

**Por que LuaLaTeX e não pdfLaTeX:** só ele combina fontes OpenType (grego
politônico, hebraico com vogais, siríaco), escrita da direita para a esquerda e
a execução de código Lua que monta os interlineares.

---

## 5. Estrutura do repositório

```
estudos-biblicos/
├── .estudos-raiz            marca a raiz — NÃO APAGUE (os cadernos se acham por ela)
├── estudos.py               a ferramenta principal
├── estudos.ini              valores padrão para cadernos novos
├── Makefile                 atalhos (make todos, make limpar…)
├── MANUAL.md  README.md
├── .gitignore  .vscode/  .github/workflows/
│
├── compartilhado/           tudo o que vale para todos os cadernos
│   ├── estilo/
│   │   ├── estudobiblico.sty   página, cores, fontes, títulos, caixas, capa, índices
│   │   ├── interlinear.sty     comandos do interlinear (lado LaTeX)
│   │   ├── interlinear.lua     motor do interlinear (lê os TSV, translitera)
│   │   ├── livro.sty / .lua    caderno de estudo de livro
│   │   └── tema.sty / .lua     caderno temático
│   ├── fontes/              fontes livres (SIL OFL) + LEIA-ME.md
│   ├── bibliografia/geral.bib  obras usadas por vários cadernos
│   ├── indice.ist           formato do índice remissivo
│   ├── indice-termos.ist    formato dos índices de termos e de textos
│   ├── latexmkrc            configuração comum (motor, caminhos)
│   └── latexmkrc-caderno    copiado para cada caderno novo
│
├── dados/
│   ├── biblia/
│   │   ├── livros.tsv       os 66 livros: abreviação, nome, capítulos, grupo
│   │   └── *.grc|hbo|arc|syr.tsv   texto original palavra por palavra
│   ├── livros/<sigla>/      licoes.tsv + textos.tsv (um por publicação)
│   └── temas/<sigla>/       textos.tsv + vocabulario.tsv + ocorrencias.tsv
│
├── ferramentas/
│   ├── interlinear.py       gera o texto original; concordância; aparato crítico
│   ├── livro.py             extrai índice e referências do PDF de uma publicação
│   ├── tema.py              ocorrências e vocabulário de um tema; confere a lista
│   └── .cache/              bases baixadas (ignorado pelo git)
│
├── modelos/                 esqueletos usados por `estudos.py novo`
│   ├── exegese/  livro/  tema/
│
├── cadernos/
│   ├── exegese/<nome>/      main.tex, config.tex, capitulos/, bibliografia.bib, latexmkrc
│   ├── livros/<sigla>/      + licoes/  (suas anotações por lição)
│   └── temas/<sigla>/
│
├── referencias/             PDFs das publicações — ficam só na sua máquina
└── saida/                   PDFs compilados e zips do Overleaf
```

### Os arquivos de um caderno

| Arquivo | Para que serve | Você edita? |
|---|---|---|
| `main.tex` | lista os capítulos, na ordem | raramente (ao criar ou remover capítulos) |
| `config.tex` | título, autor, tema de cores, papel, opções do tipo de caderno | sim, sempre |
| `capitulos/*.tex` | o seu estudo | sim, é onde você escreve |
| `licoes/NN.tex` | anotações de uma lição (só caderno de livro) | sim, opcional |
| `bibliografia.bib` | obras citadas só neste caderno | às vezes |
| `latexmkrc` | 4 linhas que acham a raiz do repositório | não |

---

## 6. Os três tipos de caderno

| | **exegese** | **livro** | **tema** |
|---|---|---|---|
| Pergunta de partida | o que *este texto* diz? | o que *esta publicação* ensina? | o que a Bíblia diz sobre *este assunto*? |
| Unidade | uma passagem | uma lição/capítulo | uma pergunta |
| Etapas | 7 (traduções → texto original → estrutura → contexto → intertexto → diálogo → síntese) | método + uma seção por lição | 7 (pergunta → palavras → textos → contexto → desenvolvimento → diálogo → síntese) |
| Dados próprios | `dados/biblia/*.tsv` | `dados/livros/<sigla>/` | `dados/temas/<sigla>/` |
| Gera sozinho | interlinear, tabela morfológica, vocabulário, variantes | lições, tabela de textos, progresso, índice de textos, registro de leitura | catálogo de textos, vocabulário, distribuição, todas as ocorrências |
| Pasta | `cadernos/exegese/` | `cadernos/livros/` | `cadernos/temas/` |

Os três usam o mesmo estilo visual e podem usar o interlinear.

---

## 7. estudos.py — a ferramenta do repositório

Rode sempre a partir da raiz do repositório. Todos os comandos aceitam o
caminho do caderno (`cadernos/livros/lff`) ou só o nome da pasta (`lff`).

### `listar`

```bash
python3 estudos.py listar
```

Mostra cada caderno, o título (lido do `config.tex`) e se já existe PDF em `saida/`.

### `verificar`

```bash
python3 estudos.py verificar
```

Confere se `lualatex`, `latexmk`, `biber`, `makeindex` e `pdftotext` estão instalados.

### `compilar`

```bash
python3 estudos.py compilar lff              # um caderno
python3 estudos.py compilar lff sangue       # vários
python3 estudos.py compilar --todos          # todos
python3 estudos.py compilar lff -v           # mostra a saída do LaTeX na tela
python3 estudos.py compilar lff -g           # força recompilar tudo
```

O PDF fica no caderno (`main.pdf`) e é copiado para `saida/<tipo>-<nome>.pdf`.
Em caso de erro, o comando mostra as primeiras mensagens do `main.log` e sai com
código 1. Se a compilação anterior tinha falhado (e o latexmk se recusa a
repetir), ele limpa os auxiliares e tenta de novo sozinho.

### `erros`

```bash
python3 estudos.py erros lff_E        # mostra as mensagens de erro do main.log
python3 estudos.py erros --todos -n 3
```

O resumo final do latexmk na tela quase nunca traz a mensagem verdadeira — ele
diz apenas que o `lualatex` devolveu código 1. O erro de verdade está no
`main.log`, e é isso que este comando extrai.

### `limpar`

```bash
python3 estudos.py limpar lff        # apaga .aux, .log, .toc, .bbl, .ind…
python3 estudos.py limpar --todos
python3 estudos.py limpar --todos --pdf   # apaga também os main.pdf dos cadernos
```

### `novo`

```bash
python3 estudos.py novo exegese mt05-03-12 --titulo "Mateus 5:3–12" \
  --subtitulo "As bem-aventuranças" --incipit "Μακάριοι οἱ πτωχοὶ τῷ πνεύματι"
python3 estudos.py novo livro  lff2   --titulo "Título da publicação"
python3 estudos.py novo tema   jesus  --titulo "Quem é Jesus?"
```

Opções: `--titulo`, `--subtitulo`, `--incipit`, `--autor`, `--tema`
(`lapis`, `purpura`, `oliveira`, `sepia`).

O comando copia o modelo, substitui os marcadores `«TITULO»`, `«AUTOR»` etc.
pelos valores (os que faltarem vêm de `estudos.ini`), cria a pasta de dados
quando é caderno de livro ou de tema, e imprime os próximos passos.

**Nome da pasta:** use minúsculas, sem espaços nem acentos
(`mt05-03-12`, `lff`, `sangue`). Ele vira o nome do PDF em `saida/`.

### `overleaf`

```bash
python3 estudos.py overleaf lff
python3 estudos.py overleaf lff -o ~/Downloads/lff.zip
```

Gera um zip autossuficiente: o caderno, o estilo, as fontes, a bibliografia e
só os arquivos de dados citados nos capítulos dele.

### `estudos.ini`

Valores padrão usados por `novo`:

```ini
[padrao]
autor = Isaac Kosloski
serie = Cadernos de Estudo Bíblico
epigrafe = Those seeking Jehovah will praise him. May you enjoy life forever.
epigrafe_ref = Psalm 22:26 — July 2024
tema_exegese = lapis
tema_livro = oliveira
tema_tema = purpura
papel = a4
```

### Makefile (Linux/macOS)

```bash
make todos        # = python3 estudos.py compilar --todos
make listar
make limpar
make verificar
make overleaf C=cadernos/livros/lff
```

---

## 8. Compilar

### Pela ferramenta (recomendado)

Veja a seção 7. É o caminho mais simples e o que copia os PDFs para `saida/`.

### Direto com o latexmk

```bash
cd cadernos/exegese/lc06-20-26
latexmk main.tex          # compila (LuaLaTeX + biber + índices, quantas vezes precisar)
latexmk -pvc main.tex     # fica observando: recompila a cada gravação
latexmk -c                # limpa os auxiliares
latexmk -C                # limpa os auxiliares e o PDF
latexmk -g main.tex       # força recompilação completa
```

> **Nunca use `latexmk -pdf`.** Essa opção força o pdfLaTeX, que não dá conta
> das fontes nem do código Lua. A configuração do repositório já escolhe o
> LuaLaTeX; basta `latexmk main.tex`.

### No VS Code

O arquivo `.vscode/settings.json` já vem configurado para a extensão
**LaTeX Workshop**: abra a pasta do repositório, abra o `main.tex` de um caderno
e grave (Ctrl+S) para compilar. O PDF abre ao lado com Ctrl+Alt+V, e o
SyncTeX liga o texto ao PDF (Ctrl+Alt+J).

### Velocidade

Uma passagem do LuaLaTeX leva de 15 s a 30 s; o documento inteiro pode exigir
três passagens. Para trabalhar rápido:

- **Exegese e tema:** descomente no `main.tex` a linha
  `\includeonly{capitulos/02-texto-original}` e deixe só o capítulo atual.
  O sumário e as referências continuam certos porque os `.aux` anteriores são
  reaproveitados.
- **Livro:** em `config.tex`, `\livroLicoes{1-12}` compila só as lições 1 a 12.
- Evite `-g` no dia a dia; ele refaz tudo.
- No WSL, mantenha o repositório no sistema de arquivos do Linux (seção 2).

---

## 9. Caderno de exegese

Estudo aprofundado de uma passagem, em 7 etapas. Exemplo pronto:
`cadernos/exegese/lc06-20-26`.

### 9.1 Criar

```bash
python3 estudos.py novo exegese mt05-03-12 --titulo "Mateus 5:3–12" \
  --subtitulo "As bem-aventuranças" --incipit "Μακάριοι οἱ πτωχοὶ τῷ πνεύματι"
```

O `--incipit` são as primeiras palavras no original; aparecem girados na lombada
da capa.

### 9.2 Gerar os dados do texto original

Sempre a partir da raiz do repositório:

```bash
python3 ferramentas/interlinear.py grego    Mt 5:3-12  -o dados/biblia/mt05_03-12.grc.tsv
python3 ferramentas/interlinear.py hebraico Is 61:1-3  -o dados/biblia/is61_01-03.hbo.tsv
python3 ferramentas/interlinear.py hebraico Dn 7:13-14 -o dados/biblia/dn07_13-14.arc.tsv
```

Convenção de nome: `<livro><capítulo>_<versículos>.<língua>.tsv`, em minúsculas
(`mt05_03-12.grc.tsv`). A extensão decide a língua e a direção da escrita:
`.grc` grego, `.hbo` hebraico, `.arc` aramaico, `.syr` siríaco.

Depois de gerar, **complete o arquivo**: a coluna `pt` (glosa em português) vem
vazia de propósito — escrevê-la é parte do estudo — e no hebraico a
transliteração também. No grego a transliteração é gerada sozinha, no padrão SBL.

Outros comandos úteis:

```bash
python3 ferramentas/interlinear.py concordancia μακάριος   # ocorrências no NT
python3 ferramentas/interlinear.py aparato Mt 5:3-12       # variantes (WH, Treg, NA28, RP)
```

### 9.3 Usar os dados nos capítulos

```latex
\textooriginal{dados/biblia/mt05_03-12.grc.tsv}          % texto corrido + variantes
\interlinear[de=5:3, ate=5:6, modo=completo, titulo={Mt 5:3–6}]{dados/biblia/mt05_03-12.grc.tsv}
\tabelamorfologica[de=5:3, ate=5:3]{dados/biblia/mt05_03-12.grc.tsv}
\vocabulario[minimo=2]{dados/biblia/mt05_03-12.grc.tsv}
\variantes{dados/biblia/mt05_03-12.grc.tsv}
```

### 9.4 As sete etapas

Cada capítulo do modelo já vem com o objetivo e as seções sugeridas:

1. **Traduções** — comparar versões; registrar cada divergência como pergunta.
2. **Texto original** — crítica textual, interlinear, léxico, gramática.
3. **Estrutura** — divisão, paralelismos, formas literárias, marcadores.
4. **Contexto** — no livro, nos paralelos, no mundo social e histórico.
5. **Intertexto** — citações, alusões e ecos do Antigo Testamento.
6. **Diálogo** — comentários e história da interpretação (só agora).
7. **Síntese** — ideia exegética, princípio, aplicação.

O caderno de Lucas 6 é o exemplo completo dessas sete etapas.

---

## 10. Caderno de estudo de livro

Acompanha uma publicação lição a lição. Exemplo: `cadernos/livros/lff`.

### 10.1 Fluxo completo

```bash
# 1. o PDF da publicação vai para referencias/ (fora do git)
cp ~/Downloads/publicacao.pdf referencias/

# 2. criar o caderno (a sigla é curta: lff, lff_E, ia…)
python3 estudos.py novo livro lff --titulo "Seja Feliz Para Sempre!"

# 3. índice das lições (detecta o número de 2 dígitos no alto da página)
python3 ferramentas/livro.py indice referencias/publicacao.pdf \
  -o dados/livros/lff --deslocamento 2

# 4. CONFIRA E CORRIJA dados/livros/lff/licoes.tsv (o PDF costuma perder acentos)

# 5. textos bíblicos de cada lição
python3 ferramentas/livro.py textos referencias/publicacao.pdf \
  -o dados/livros/lff --ultima 258

# 6. estatísticas (opcional)
python3 ferramentas/livro.py resumo dados/livros/lff

# 7. compilar
python3 estudos.py compilar lff
```

- `--deslocamento` = página do PDF − página impressa. Descubra abrindo o PDF:
  se a lição 01 começa na página 7 do arquivo e traz o número 5 impresso, é 2.
- `--ultima` = última página do PDF que ainda pertence à última lição (antes dos
  apêndices).

Se o livro tiver outro formato e o `indice` não funcionar, escreva o
`licoes.tsv` à mão: bastam `num`, `parte`, `titulo`, `pagina`, `pagina_pdf`.

### 10.2 O que sai pronto

Cada lição vem com ficha (páginas, nº de textos, datas de estudo e revisão),
o campo "Antes de ler", a tabela dos textos bíblicos (com o ponto da lição em
que cada um aparece, o selo LEIA e caixinhas para "li o contexto" e "comparei
traduções") e campos para escrever. Ao final do caderno: registro de progresso,
visão geral dos textos mais citados, índice de textos bíblicos e um quadro dos
1189 capítulos da Bíblia para marcar a leitura.

### 10.3 Anotar no computador

Crie `licoes/NN.tex` na pasta do caderno (NN = número da lição com dois
dígitos). O conteúdo entra na lição no lugar dos campos em branco:

```latex
\begin{campo}{Ideia central}
A resposta da lição, com as minhas palavras.
\end{campo}

\begin{campo}{Texto em foco: 2 Timóteo 3:16}
\interlinear[modo=leitura]{dados/biblia/2tm03_16-17.grc.tsv}
\end{campo}

\EBlivcampo[3]{Dúvidas para pesquisar}{}    % campo com 3 linhas em branco
```

Veja os exemplos em `cadernos/livros/lff/licoes/01.tex` e `04.tex`.

### 10.4 Opções (config.tex)

| Comando | Efeito |
|---|---|
| `\livroDados` | pasta dos dados (`dados/livros/lff`) |
| `\livroNome`, `\livroEditora`, `\livroEdicao` | identificação da publicação |
| `\livroUnidade`, `\livroUnidadePlural` | `Lição`/`Lições`, `Capítulo`/`Capítulos`, `Artigo`… |
| `\livroParte` | nome das divisões maiores |
| `\livroModo` | `impresso` (linhas e caixinhas) ou `digital` (só o que você escreveu) |
| `\livroLinhas` | quantas linhas em cada campo em branco |
| `\livroLicoes` | quais lições incluir: vazio = todas, `1-12`, `1,4,7` |
| `\livroNotas` | pasta das anotações (padrão `licoes`) |
| `\ebAbasPor` | `parte` ou `capitulo` — o que as abas da borda contam |

---

## 11. Caderno temático

Parte de uma pergunta e procura a resposta em toda a Bíblia.
Exemplo: `cadernos/temas/sangue`.

### 11.1 Fluxo completo

```bash
# 1. criar
python3 estudos.py novo tema sangue --titulo "O que a Bíblia diz sobre o sangue?" \
  --incipit "περὶ τοῦ αἵματος"

# 2. todas as ocorrências das palavras do tema (H = hebraico, G = grego)
python3 ferramentas/tema.py ocorrencias H1818 G129 -o dados/temas/sangue

# 3. vocabulário pré-preenchido (complete transliteração e sentido em português)
python3 ferramentas/tema.py vocabulario H1818 H5315 G129 G4156 -o dados/temas/sangue

# 4. escreva a SUA lista de estudo em dados/temas/sangue/textos.tsv

# 5. confira a lista e veja o que ainda não leu
python3 ferramentas/tema.py conferir dados/temas/sangue

# 6. compilar
python3 estudos.py compilar sangue
```

**Como achar os números de Strong:** gere um trecho em que a palavra aparece e
olhe a coluna `strong` (`python3 ferramentas/interlinear.py grego Hb 9:22` mostra
`αἷμα G129`), ou use uma concordância.

### 11.2 A lista de estudo

`dados/temas/<sigla>/textos.tsv` é o coração do caderno:

| coluna | conteúdo |
|---|---|
| `ref` | `Lv 17:10-14`, `At 15:28, 29` ou `Levítico 17:10-14` |
| `grupo` | a categoria que **você** cria; os grupos saem na ordem em que aparecem no arquivo |
| `peso` | `central`, `apoio`, `dificil` ou vazio (vazio = caixinhas para decidir no papel) |
| `nota` | observação curta |

### 11.3 As sete etapas

1. **A pergunta** — formular, dividir em subperguntas, registrar o que já penso.
2. **Palavras e conceitos** — vocabulário no original; o que existe sem a palavra.
3. **Os textos** — a lista, por grupo, com o peso de cada um.
4. **Leitura no contexto** — fichas dos textos centrais.
5. **Desenvolvimento** — como o tema aparece nas várias partes da Bíblia.
6. **Diálogo** — os textos difíceis e as leituras divergentes.
7. **Síntese** — proposições numeradas, cada uma com a sua base textual.

O apêndice traz **todas** as ocorrências, destacando as que já estão na sua
lista. É a defesa contra o erro típico do estudo temático: escolher só os textos
que confirmam o que já se pensava.

### 11.4 Temas guiados por conceito

Em perguntas como *Quem é Jesus?* o assunto não depende de uma palavra só. Use a
concordância para os termos-chave (Χριστός G5547, κύριος G2962, υἱός G5207,
λόγος G3056) mas monte a lista também por conceitos — o que Jesus diz de si, o
que outros dizem dele, o que ele faz, a relação com o Pai, o papel futuro — e
deixe a coluna `grupo` refletir isso.

---

## 12. Referência de comandos LaTeX

Tudo o que se segue está disponível em qualquer caderno (o que é específico
está marcado).

### 12.1 Texto em outras línguas e referências

| Comando | Resultado |
|---|---|
| `\gr{μακάριοι}` | grego, na cor do grego |
| `\hb{אַשְׁרֵי}` | hebraico (direita para a esquerda automática) |
| `\arc{כְּבַר אֱנָשׁ}` | aramaico |
| `\sy{ܛܘܒܝܟܘܢ}` | siríaco |
| `\en{blessed}` | inglês, em itálico e cinza-ardósia |
| `\tl{makarioi}` | transliteração |
| `\trgr{μακάριοι}` | translitera o grego automaticamente (padrão SBL) |
| `\rb{Lc 6:20}` | referência bíblica em linha |
| `\vs{20}` | número de versículo sobrescrito, em vermelho-rubrica |
| `\margem{...}` | nota na margem externa |
| `\EBimplicito{...}` | palavra implícita, em cinza |
| `\poema` | inicia parágrafo com recuo pendente (poesia) |

### 12.2 Caixas

```latex
\begin{objetivo} O que se quer alcançar na etapa. \end{objetivo}

\begin{traducao}{ARA}{Almeida Revista e Atualizada}{1993}
\vs{20}Texto do versículo…
\basetextual{Biblia Hebraica Stuttgartensia}{Nestle-Aland}
\end{traducao}

\begin{nota} Observação. \end{nota}
\begin{nota}[Sobre o título] Com título próprio. \end{nota}
\begin{pergunta} Pergunta de estudo (numerada por capítulo). \end{pergunta}
\begin{alerta} Cuidado de método. \end{alerta}
\begin{alerta}[Falácias a evitar] … \end{alerta}
\begin{aplicacao} Ponte para a vida. \end{aplicacao}
\begin{variante} Problema de crítica textual. \end{variante}
\begin{citacao}{Bovon, p. 222} Texto citado. \end{citacao}
\begin{lexico}{μακάριος}{G3107}{50} Verbete: sentido, uso, ocorrências. \end{lexico}
```

`\lexicoref{μακάριος}` põe um lema no índice de termos sem abrir uma caixa.

### 12.3 Tabelas

```latex
\begin{ebtabela}{@{}l >{\raggedright\arraybackslash}X@{}}
\EBcab{Texto} & \EBcab{Observação}\\\midrule
\rb{Lc 1:53} & Magnificat\\
\end{ebtabela}
```

`X` é a coluna elástica (do pacote `tabularx`); `\EBcab` formata o cabeçalho; as
linhas saem com fundo alternado.

### 12.4 Interlinear (todos os cadernos)

```latex
\interlinear[opções]{dados/biblia/arquivo.tsv}
\textooriginal[opções]{arquivo}        % texto corrido, com nº de versículo e variantes
\tabelamorfologica[opções]{arquivo}    % uma linha por palavra
\vocabulario[opções]{arquivo}          % lemas repetidos, com frequência no NT
\variantes[opções]{arquivo}            % só a lista de variantes
\interlinearset{en=false}              % muda o padrão daqui em diante
```

Opções:

| Opção | Valores | Padrão |
|---|---|---|
| `modo` | `leitura` · `estudo` · `completo` | `\ebInterlinearModo` do `config.tex` |
| `de`, `ate` | `6:20`, `6:26` | tudo o que houver no arquivo |
| `lingua` | `grego` · `hebraico` · `aramaico` · `siriaco` | pela extensão do arquivo |
| `titulo` | texto ao lado do nome da língua | vazio |
| `translit`, `pt`, `en`, `lema`, `strong`, `morf` | `true`/`false` (camadas) | conforme o modo |
| `acentos` | `true`/`false` — te'amim no hebraico | `\ebAcentosHebraicos` |
| `legenda`, `moldura`, `indice` | `true`/`false` | `true` |
| `quebra` | `true` = cada versículo numa linha nova | `false` |
| `minimo` | só em `\vocabulario`: nº mínimo de ocorrências | `2` |

Os modos: **leitura** = original + transliteração + português; **estudo** =
mais inglês e morfologia; **completo** = mais lema e número de Strong.

### 12.5 Caderno de livro

| Comando | Efeito |
|---|---|
| `\licoes` | gera todas as lições (respeitando `\livroLicoes`) |
| `\progresso` | tabela para registrar datas de estudo e revisão |
| `\textosmaiscitados[2]` | textos que se repetem, e em que lições |
| `\textosporlivro` | quantas referências por livro bíblico |
| `\leituradabiblia` | quadro dos 1189 capítulos para marcar |
| `\begin{campo}{Título}…\end{campo}` | bloco de anotação sua |
| `\EBlivcampo[4]{Título}{dica}` | campo em branco com 4 linhas (só no modo impresso) |

### 12.6 Caderno temático

| Comando | Efeito |
|---|---|
| `\textosdotema` | catálogo dos textos, por grupo |
| `\textosdotema[ordem=biblica]` | em ordem bíblica, mostrando o grupo |
| `\textosdotema[peso=dificil]` | só os textos marcados como difíceis |
| `\textosdotema[grupo={Sangue e vida}]` | um grupo só |
| `\vocabulariodotema` | tabela das palavras do tema |
| `\distribuicaodotema` | textos e ocorrências por parte da Bíblia |
| `\ocorrenciasdotema[H1818]` | todas as ocorrências (sem argumento: todas as palavras) |
| `\tema{Lv 17:11}` | escreve "Levítico 17:11" e põe no índice de textos |
| `\begin{fichatexto}[grupo]{Lv 17:11}…\end{fichatexto}` | ficha de estudo de um texto |
| `\proposicao{Afirmação.}{Lv 17:11; Hb 9:22}` | proposição numerada da síntese |
| `\campovazio[3]{Título}{dica}` | campo em branco com 3 linhas |

### 12.7 Estrutura do documento

`\capa`, `\colofao`, `\part{...}`, `\chapter{...}`, `\section{...}`,
`\EBornamento`, `\EBlosango`, `\EBemblema`.
Citações: `\parencite{fee2002}` (entre parênteses) e `\textcite{bovon2002}`
(no corpo da frase). Referências cruzadas: `\label{cap:original}` e
`\ref{cap:original}`.

---

## 13. Ferramentas de linha de comando

Todas usam só a biblioteca padrão do Python 3 e são executadas **a partir da
raiz** do repositório. Na primeira execução, baixam as bases para
`ferramentas/.cache/` (é preciso internet só nessa vez).

### 13.1 interlinear.py

```bash
python3 ferramentas/interlinear.py grego LIVRO CAP:V-V -o ARQUIVO.tsv
python3 ferramentas/interlinear.py hebraico LIVRO CAP:V-V -o ARQUIVO.tsv
python3 ferramentas/interlinear.py concordancia LEMA
python3 ferramentas/interlinear.py aparato LIVRO CAP:V-V
```

- `grego` usa o **SBLGNT** com a morfologia do **MorphGNT**; preenche lema,
  número de Strong, morfologia em português, glosa em inglês, frequência no NT
  e, quando há variante, a leitura alternativa (ex.: `RP: ἔλεγχον`).
- `hebraico` usa o **Códice de Leningrado (WLC)** com a morfologia da
  **OpenScriptures**; serve também para o aramaico bíblico (Daniel, Esdras) —
  a ferramenta detecta e avisa.
- Abreviações dos livros: as de `dados/biblia/livros.tsv` (`Mt`, `Lc`, `Sl`, `Is`, `Dn`…).
- **Numeração:** no Antigo Testamento vale a numeração **hebraica**. Sl 83:18 nas
  Bíblias em português é Sl 83:19 no hebraico, porque o título conta como
  versículo 1. Os Salmos são o caso mais frequente.

### 13.2 livro.py

```bash
python3 ferramentas/livro.py indice PDF -o PASTA [--deslocamento N]
python3 ferramentas/livro.py textos PDF -o PASTA [--ultima N]
python3 ferramentas/livro.py resumo PASTA [-n 15]
```

`indice` procura o número de duas casas no alto de cada página e monta o
`licoes.tsv` (títulos a revisar à mão). `textos` percorre as páginas de cada
lição e reconhece referências no formato "Livro capítulo:versículo", marcando
como `leia` as precedidas de "Leia"/"Leiam". `resumo` mostra os textos e livros
mais citados.

### 13.3 tema.py

```bash
python3 ferramentas/tema.py ocorrencias H1818 G129 -o PASTA
python3 ferramentas/tema.py vocabulario H1818 G129 -o PASTA
python3 ferramentas/tema.py conferir PASTA
```

`conferir` é o mais útil no dia a dia: aponta referências que ele não reconheceu
(erro de digitação ou abreviação estranha), repetições, e lista as ocorrências
que ainda não entraram na sua lista de estudo.

---

## 14. Formato dos dados

Todos os dados são **TSV**: texto puro, UTF-8, colunas separadas por
**tabulação**. Linhas iniciadas por `#` são comentários. Podem ser editados em
qualquer editor de texto ou numa planilha (ao salvar, escolha "texto separado
por tabulações").

> No editor, deixe visível a diferença entre tabulação e espaços. Uma coluna
> separada por espaços em vez de tabulação é a causa mais comum de "sumiu uma
> linha".

### 14.1 Texto original — `dados/biblia/*.grc|hbo|arc|syr.tsv`

Uma palavra por linha:

| coluna | conteúdo |
|---|---|
| `ref` | `6:20` (capítulo:versículo) |
| `palavra` | a forma como está no texto |
| `translit` | transliteração (vazia no grego = gerada automaticamente) |
| `lema` | forma de dicionário |
| `strong` | `G3107`, `H1818` |
| `morf` | análise morfológica em português |
| `pt` | sua glosa; `[palavra]` marca o que é implícito (sai em cinza) |
| `en` | glosa em inglês (lexical, gerada) |
| `var` | variante textual — marca a palavra com ° e entra na lista de variantes |
| `freq_nt` | ocorrências do lema no NT |

### 14.2 Livro — `dados/livros/<sigla>/`

- `licoes.tsv`: `num`, `parte`, `titulo`, `pagina`, `pagina_pdf`
- `textos.tsv`: `licao`, `secao`, `ref`, `abrev`, `ordem`, `cap`, `vers`, `tipo`
  (`leia` ou `citado`)

### 14.3 Tema — `dados/temas/<sigla>/`

- `textos.tsv`: `ref`, `grupo`, `peso`, `nota` — **escrito por você**
- `vocabulario.tsv`: `lingua`, `lema`, `translit`, `strong`, `ocorrencias`, `sentido`, `nota`
- `ocorrencias.tsv`: `strong`, `lema`, `ref`, `ordem`, `cap`, `vers`, `forma` — gerado

### 14.4 Livros da Bíblia — `dados/biblia/livros.tsv`

Os 66 livros com `ordem`, `abrev`, `nome`, `capitulos`, `testamento`, `grupo` e
`nomes_alt` (grafias alternativas usadas no reconhecimento de referências).
É a tabela que faz o `livro.py` e o `tema.py` entenderem "Cântico de Salomão",
"Cantares" e "Ct" como o mesmo livro. Para aceitar outra grafia, acrescente-a em
`nomes_alt`, separada por `|`.

---

## 15. Personalizar

### 15.1 Trocar o tema de cores

No `config.tex` do caderno:

```latex
\newcommand\ebTema{purpura}     % lapis | purpura | oliveira | sepia
```

Cada tema define seis cores: `destaque`, `destaque2` (ouro), `rubrica`
(vermelho dos números de versículo), `fundo`, `fundo2` e `fundopagina`.
As cores das línguas são fixas em todos os temas: `grego` (azul), `hebraico`
(âmbar), `aramaico` (oliva, usada também no siríaco), `ingles` (ardósia), além
de `tinta` e `suave`.

### 15.2 Criar um tema novo

Em `compartilhado/estilo/estudobiblico.sty`, junto dos outros:

```latex
% ------------- temas ------------- destaque  ouro    rubrica fundo   fundo2  página
\EB@se{\ebTema}{indigo}  {\EB@tema{2E3A59}{A98B36}{9C3B26}{F4F4F0}{DCDCD2}{FAFAF7}}
```

Os seis valores são cores em hexadecimal, na ordem do comentário. Depois é só
usar `\newcommand\ebTema{indigo}` no `config.tex`.

### 15.3 Papel e margens

```latex
\newcommand\ebPapel{a4}    % a4 = margem externa larga para notas | b5 = livro
```

Para ajustar as margens, edite o bloco `\geometry{...}` em
`estudobiblico.sty`. A margem externa grande existe para o `\margem{...}`;
`marginparwidth` controla a largura dessas notas.

### 15.4 Trocar uma fonte

As fontes ficam em `compartilhado/fontes/` e são carregadas por nome de arquivo.
Para trocar a fonte do hebraico, por exemplo: copie os arquivos para essa pasta
e, no `config.tex`:

```latex
\renewfontfamily\EBfhebraico{SILEOT}[Path=compartilhado/fontes/, Extension=.ttf, Script=Hebrew]
```

Famílias definidas pelo estilo: `\EBfgrego`, `\EBftranslit`, `\EBfhebraico`,
`\EBfsiriaco`, `\EBfsiriacoOriental`, `\EBftitulo`, `\EBfversal`, `\EBfnumeros`.
Sugestões livres: Cardo, Ezra SIL, Taamey Frank CLM, Libertinus Serif.
SBL BibLit e SBL Hebrew são gratuitas com licença própria; Brill é gratuita só
para uso não comercial.

### 15.5 Ligar ou desligar elementos

```latex
\newcommand\ebFundoPagina{sim}   % fundo pergaminho em todas as páginas
\newcommand\ebAbas{nao}          % abas coloridas na borda
\newcommand\ebAbasPor{parte}     % abas por parte (livro) ou por capítulo
```

### 15.6 Criar uma caixa nova

Em `estudobiblico.sty`, ao lado das outras:

```latex
\newtcolorbox{oracao}[1][Oração]{EB/base, colback=grego!5,
  borderline west={2.5pt}{0pt}{grego},
  before upper={\EB@rotulo{grego}{#1}\quad}}
```

Fica disponível como `\begin{oracao} … \end{oracao}` em todos os cadernos.

### 15.7 Ajustar o interlinear

No `interlinear.sty`:

- `\EBilespaco` — espaço entre as palavras;
- `\EBilentrelinhas` — espaço entre as linhas do bloco;
- `\EBilmorfmax` — largura máxima da coluna de morfologia;
- `\EBil@conf@grego` e irmãos — fonte, corpo e cor de cada língua.

### 15.8 Capa e colofão

`\capa` e `\colofao` estão no fim de `estudobiblico.sty`. A capa usa
`\ebTitulo`, `\ebSubtitulo`, `\ebIncipit` (girado na lateral), `\ebSerie`,
`\ebNumero`, `\ebAutor` e `\ebData`; o emblema é a lâmpada de azeite
(`\EBemblema`), desenhada em TikZ. O colofão traz a epígrafe, os créditos das
bases de dados e das fontes.

---

## 16. Bibliografia e índices

### Bibliografia

Duas fontes: `compartilhado/bibliografia/geral.bib` (obras usadas por vários
cadernos) e o `bibliografia.bib` do caderno. Ambas são declaradas no `main.tex`:

```latex
\addbibresource{geral.bib}
\addbibresource{bibliografia.bib}
```

Estilo autor-data (biblatex + biber). Cite com `\parencite{chave}` ou
`\textcite{chave}`. Só aparecem na bibliografia as obras citadas.

### Índices

- **Índice remissivo** (`\index{...}`) — assuntos gerais; formato em `indice.ist`.
- **Índice de termos originais** — alimentado automaticamente pelo interlinear e
  pelas caixas `lexico`; ordena o grego pela transliteração sem acentos.
- **Índice de textos bíblicos** — nos cadernos de livro e de tema, alimentado
  pelas tabelas de textos; sai em ordem bíblica.

Os dois últimos usam `indice-termos.ist`. Tudo é chamado pelo latexmk; não é
preciso rodar o makeindex à mão.

---

## 17. Overleaf

```bash
python3 estudos.py overleaf lff      # gera saida/livros-lff-overleaf.zip
```

No Overleaf: **New Project → Upload Project**, escolha o zip e depois
**Menu → Compiler → LuaLaTeX**. O zip é autossuficiente (estilo, fontes, dados e
bibliografia numa estrutura plana) e traz um `latexmkrc` próprio.

Limitações: no plano gratuito, o tempo de compilação pode estourar em cadernos
grandes — use `\includeonly` ou `\livroLicoes`. E o Overleaf não devolve as
alterações sozinho: copie de volta os arquivos do caderno que você editou lá
(ou use a integração com o GitHub, disponível nos planos pagos).

---

## 18. Git e GitHub

**Crie o repositório como privado.** Ele contém textos de traduções modernas e
dados extraídos de publicações protegidas por direitos autorais, para uso pessoal.

### Primeira vez

```bash
git config --global user.name  "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
git config --global init.defaultBranch main
gh auth login --web --git-protocol https --scopes workflow

cd estudos-biblicos
git init
git add .
git status                                    # confira o que vai subir
git check-ignore -v referencias/publicacao.pdf   # deve estar ignorado
git commit -m "Repositório de estudos bíblicos"
gh repo create estudos-biblicos --private --source=. --remote=origin --push
```

Se o push for recusado com *"refusing to allow an OAuth App to create or update
workflow"*, falta o escopo: `gh auth refresh -s workflow` e `git push -u origin main`.

### No dia a dia

```bash
git add -A
git commit -m "lff: anotações das lições 05-06"
git push
```

Sugestão de mensagens: `<caderno>: <o que mudou>` — `lc06: etapa 4 revisada`,
`sangue: fichas de Lv 17 e At 15`, `estilo: caixa de oração`.

### Em outro computador

```bash
gh repo clone estudos-biblicos
cd estudos-biblicos
python3 estudos.py verificar
python3 estudos.py compilar --todos
```

### O que o `.gitignore` deixa de fora

PDFs gerados (`saida/`, `main.pdf`), arquivos auxiliares do LaTeX, o cache das
ferramentas e a pasta `referencias/`. O repositório guarda o que é fonte: texto,
dados e estilo.

### Compilação automática (opcional)

`.github/workflows/compilar.yml` compila os cadernos a cada push e guarda os
PDFs na aba **Actions**. Em repositório privado, consome os minutos gratuitos do
plano.

```bash
gh run list            # execuções
gh run watch           # acompanha
gh run download -n cadernos-pdf
gh workflow disable compilar     # desligar
```

---

## 19. Manutenção do repositório

### Renomear um caderno

```bash
git mv cadernos/livros/lff cadernos/livros/lff-pt
# se for caderno de livro ou tema, mova também os dados e ajuste o config.tex:
git mv dados/livros/lff dados/livros/lff-pt
# em cadernos/livros/lff-pt/config.tex: \newcommand\livroDados{dados/livros/lff-pt}
rm -f saida/livros-lff.pdf
python3 estudos.py compilar lff-pt
```

### Duas edições do mesmo livro

É o caso de uma publicação em português e em inglês: crie dois cadernos
(`lff` e `lff_E`) com duas pastas de dados. O estilo e as ferramentas são os
mesmos; muda só o `licoes.tsv` (títulos na língua da edição) e o
`\livroDados` de cada `config.tex`. Se quiser, aponte os dois para a mesma pasta
`licoes/` de anotações usando `\livroNotas`.

### Apagar um caderno

```bash
git rm -r cadernos/temas/sangue
rm -f saida/temas-sangue.pdf
# os dados em dados/temas/sangue podem ser mantidos para outro caderno
```

### Atualizar as bases das ferramentas

```bash
rm -rf ferramentas/.cache        # tudo é baixado de novo na próxima execução
```

### Espaço e backup

O que precisa de backup é o repositório inteiro **menos** `saida/`,
`referencias/` e `ferramentas/.cache/` — isto é, exatamente o que o git versiona.
Um `git push` já é o seu backup.

---

## 20. Estender o repositório

### Acrescentar uma etapa a um caderno

1. Crie `capitulos/08-nome.tex` com `\chapter{...}`.
2. Acrescente `\include{capitulos/08-nome}` no `main.tex`, na ordem desejada.

### Criar um tipo novo de caderno

Os três tipos seguem o mesmo padrão; para um quarto (por exemplo, "estudo de
personagem"):

1. `cp -r modelos/tema modelos/personagem` e ajuste os capítulos.
2. Se precisar de comandos próprios, crie
   `compartilhado/estilo/personagem.sty` (e um `.lua` se for ler dados) e
   carregue-o no `main.tex` do modelo.
3. Em `estudos.py`, acrescente `"personagem": "personagens"` no dicionário
   `tipo_pasta` de `cmd_novo` e `"personagem"` na lista de `choices` do
   argumento `tipo`.
4. `python3 estudos.py novo personagem abraao --titulo "Abraão"`.

O `estudos.py` acha os cadernos procurando `main.tex` dentro de `cadernos/`, e o
`overleaf` monta o zip a partir dos `dados/...` citados nos `.tex` — os dois
funcionam com qualquer tipo novo, sem mais alterações.

### Acrescentar uma língua ao interlinear

Em `interlinear.sty`, copie um bloco `\EBil@conf@<lingua>` (fonte, corpo, cor,
direção) e acrescente a extensão correspondente na tabela `EXT` de
`interlinear.lua`.

---

## 21. Problemas comuns

### "Nothing to do" / "gave an error in previous invocation"

```
Latexmk: Nothing to do for 'main.tex'.
  lualatex: gave an error in previous invocation of latexmk.
```

O latexmk guarda, no `main.fdb_latexmk`, que a última tentativa falhou, e se
recusa a repetir enquanto nada mudar. O erro verdadeiro está no `main.log` da
tentativa anterior.

```bash
python3 estudos.py limpar lff_E        # apaga os auxiliares
python3 estudos.py compilar lff_E -v   # recompila mostrando tudo
```

A versão atual do `estudos.py` faz isso sozinha: ao detectar essa mensagem, ela
limpa e tenta de novo, e mostra as primeiras mensagens de erro do log.
Para ver o erro à mão:

```bash
grep -n -m3 -A5 -E '^(!|.*\.(tex|sty|lua):[0-9]+:)' cadernos/livros/lff_E/main.log
```

### "Missing $ inserted"

Quase sempre é um caractere que o LaTeX reserva para si aparecendo em texto
comum: `_`, `&`, `%`, `#`, `$`, `^`, `~`, `\`. O caso mais frequente aqui é a
sigla de um caderno com sublinhado (`lff_E`) escrita dentro de um `.tex` ou de
um `.bib`. Escreva `lff\_E` nesses arquivos — nos **caminhos** e nos nomes de
pasta o sublinhado é normal e não precisa de nada.

### Outros erros

| Sintoma | Causa e solução |
|---|---|
| `Missing $ inserted` | caractere reservado em texto (veja acima); o `main.log` mostra o arquivo e a linha. |
| `Este projeto precisa do LuaLaTeX` | usou pdfLaTeX (`latexmk -pdf`). Use `latexmk main.tex` ou `estudos.py compilar`. |
| `Não achei a raiz do repositório` | o caderno está fora de `cadernos/`, ou o arquivo `.estudos-raiz` foi apagado. |
| `File 'estilo/estudobiblico.sty' not found` | compilou com `lualatex main.tex` direto. Use o latexmk, que configura os caminhos. |
| `Font … not found` | falta o arquivo em `compartilhado/fontes/` (confira maiúsculas no nome). |
| Bibliografia vazia, citações como `??` | rode de novo; se persistir, veja `main.blg` (erro de sintaxe no `.bib`) e confira a chave citada. |
| Índice vazio | o makeindex não rodou: compile pelo latexmk. |
| `Interlinear: arquivo … não encontrado` | caminho errado: ele é relativo à raiz (`dados/biblia/...`), não ao capítulo. |
| `Estudo temático: arquivo … não encontrado` | confira `\temaDados` no `config.tex` e se o TSV existe. |
| Hebraico com versículos "trocados" | use a numeração hebraica ao gerar os dados (seção 13.1). |
| Uma referência não aparece no catálogo/índice | rode `tema.py conferir` ou `livro.py resumo`: a abreviação pode não estar em `livros.tsv`. |
| Tabela desalinhada depois de editar um TSV | alguma coluna ficou separada por espaços em vez de tabulação. |
| Compilação lenta | normal com LuaLaTeX; compile por partes (seção 8). No WSL, saia de `/mnt/c`. |
| `Overfull \hbox` | aviso, não erro: uma linha passou da margem. Reformule a frase ou ignore. |

### Onde procurar o erro

O resumo final do latexmk (`Command for 'lualatex' gave return code 1`) só diz
*que* falhou, não *por quê*. Procure nesta ordem:

0. `python3 estudos.py erros <caderno>` — atalho para o que vem abaixo.
1. `main.log` — a mensagem verdadeira, com arquivo e linha.
2. `main.blg` — erros de bibliografia.
3. `*.ilg` — erros de índice.
4. `python3 estudos.py compilar <caderno> -v` — tudo na tela, ao vivo.

---

## 22. Licenças e cuidados

**Dados e programas usados:**

- SBL Greek New Testament — CC BY 4.0 (Society of Biblical Literature / Logos)
- MorphGNT (morfologia do NT) — CC BY-SA 3.0
- OpenScriptures Hebrew Bible (WLC + morfologia) — CC BY 4.0
- Léxico Strong — domínio público
- Fontes tipográficas — SIL Open Font License 1.1 (ver `compartilhado/fontes/LEIA-ME.md`)

**O que exige cuidado:**

- Textos de traduções modernas citados nos cadernos são © dos seus detentores.
  Estão aqui para estudo pessoal.
- O PDF de uma publicação estudada **nunca** entra no repositório; fica em
  `referencias/`, que o git ignora. O que é versionado são os dados extraídos
  (índice das lições e referências bíblicas), que são fatos organizados por você.
- Por isso: **mantenha o repositório privado** e não publique os PDFs compilados.

Transliterações, glosas em português, análises e sínteses são seus.
