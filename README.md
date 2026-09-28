# Estudos bíblicos — cadernos em LaTeX

Repositório pessoal de estudos bíblicos, com identidade visual comum e
ferramentas para gerar interlineares (grego, hebraico, aramaico, siríaco),
cadernos de acompanhamento de livros e estudos por tema.

| Caderno | Tipo | Pasta |
|---|---|---|
| Lucas 6:20–26 — Sermão da Planície: felicidades e ais | exegese | `cadernos/exegese/lc06-20-26` |
| Seja Feliz Para Sempre! — lição a lição | estudo de livro | `cadernos/livros/lff` |
| O que a Bíblia diz sobre o sangue? | estudo temático | `cadernos/temas/sangue` |

## Início rápido

```bash
python3 estudos.py verificar          # confere a instalação (TeX Live, Python, Poppler)
python3 estudos.py compilar --todos   # PDFs em saida/
python3 estudos.py novo exegese mt05-03-12 --titulo "Mateus 5:3–12"
python3 estudos.py novo tema jesus --titulo "Quem é Jesus?"
python3 estudos.py overleaf lff       # zip pronto para o Overleaf
```

Tudo sobre instalação, estrutura, criação de cadernos, formato dos dados,
Overleaf e Git está no **[MANUAL.md](MANUAL.md)**.

## Fontes de dados e licenças

- Texto grego: SBL Greek New Testament (CC BY 4.0); morfologia MorphGNT (CC BY-SA 3.0)
- Hebraico e aramaico: Westminster Leningrad Codex + morfologia OpenScriptures (CC BY 4.0)
- Fontes tipográficas: SIL Open Font License (ver `compartilhado/fontes/LEIA-ME.md`)
- Traduções modernas e publicações estudadas: © dos respectivos detentores,
  citadas para estudo pessoal. **Mantenha este repositório privado.**
