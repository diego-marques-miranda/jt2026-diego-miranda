> **Vídeo (Entregável 2):** https://drive.google.com/file/d/1YCM5gTr8WxxYuDRr4NKCbqy_Ea2WimQE/view?usp=sharing — compartilhamento em "qualquer pessoa com o link".

> **Transcrição (Entregável 2):** https://drive.google.com/file/d/1YCM5gTr8WxxYuDRr4NKCbqy_Ea2WimQE/view?usp=sharing — compartilhamento em "qualquer pessoa com o link".

# Hackathon Jovens Talentos AI Builder 2026 — Seazone · Itapema (SC)

Recomendação de investimento imobiliário para a Seazone, construída com IA a partir dos dados
reais de anúncios de Airbnb e VivaReal de Itapema.

- **Enunciado do desafio:** [`index.html`](index.html) (abra no navegador).
- **Resposta final:** [`relatorio.md`](relatorio.md).
- **Processo completo com a IA:** pasta [`ai-log/`](ai-log/) (conversa exportada em texto, parte da avaliação).
- **Código da análise:** [`analise.py`](analise.py) (um único script, reproduzível).

## Como rodar

Requisitos: **Python 3.9+** com **pandas** (única dependência).

```powershell
pip install pandas
python analise.py
```

O script lê os arquivos de `data/`, **regenera** as planilhas de `output/` e **reescreve**
`relatorio.md` com a recomendação. Não precisa de mais nada — dados já estão no repositório.

Para conferir a saída sem rodar, os resultados já estão commitados em `output/` e `relatorio.md`.

## Onde está a resposta

| Pergunta do desafio | Resposta (em `relatorio.md`) | Planilha de apoio (`output/`) |
|---|---|---|
| 1. Melhor perfil de imóvel | Seção "Pergunta 1" | `q1_perfil.csv` |
| 2. Melhor localização | Seção "Pergunta 2" | `q2_localizacao.csv` |
| 3. Características que explicam a receita | Seção "Pergunta 3" | `q3_correlacoes.csv`, `q3_grupos.csv` |
| 4. O que comprar + retorno estimado | Seção "Pergunta 4" | `q4_yield_cidade.csv`, `q4_yield_bairro.csv`, `q4_preco_cidade.csv`, `q4_robustez.csv` |
| Posição sobre a tese (compactos no Centro) | Seção "Posição sobre a tese interna" | `q1_perfil.csv`, `q4_yield_bairro.csv` |
| Contexto do mercado Airbnb por bairro | Seção "Premissas e decisões" | `mercado_contexto.csv` |
| VivaReal normalizado (bairros padronizados) | Seção "Premissas e decisões" | `viva_normalizado.csv` |

## Estrutura do repositório

```
analise.py            Código da análise (limpeza, receita, Q1–Q4, gera o relatório)
relatorio.md          RESPOSTA FINAL escrita (recomendação + posição sobre a tese)
output/*.csv          Planilhas de apoio geradas pelo script (1 por pergunta)
ai-log/               Conversas com a IA exportadas em texto (avaliação de processo)
data/                 Snapshot dos dados do desafio (Airbnb + VivaReal)
index.html            Enunciado do desafio (baixe e abra no navegador)
```

## Método em poucas linhas

- Receita anual estimada por anúncio a partir do preço por noite (última captura por data) e
  do nº de avaliações como proxy de noites alugadas; sensibilidade testada com cenários de
  ocupação (25% / 35% / 45%) — ver `q4_robustez.csv`.
- Retorno (Q4) = **gross yield**: receita estimada ÷ preço mediano de venda (VivaReal), por
  perfil e por perfil × bairro.
- Detalhes, premissas e limitações estão documentados em [`relatorio.md`](relatorio.md).