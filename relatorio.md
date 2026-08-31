# Relatório — Recomendação de investimento imobiliário em Itapema (SC)

## Resumo executivo

Com base nos anúncios de curta temporada (Airbnb) e de venda (VivaReal), a recomendação à
Seazone é investir em **Apartamento · 2 quartos** (retorno anual estimado de aproximadamente 5,61%, com receita estimada perto de R$ 46.200 contra preço mediano de venda de R$ 823.987).

- **Pergunta 1 (perfil):** a resposta muda conforme o critério — pela **maior receita estimada**, o melhor é o **Apartamento · 4 quartos** (R$ 108.000/ano); pelo **maior retorno estimado sobre o preço de venda**, o melhor é o **Apartamento · 2 quartos** (5,61% ao ano).
- **Pergunta 2 (localização):** a maior receita estimada está na **Meia Praia**.
- **Pergunta 3 (características):** o **tamanho do imóvel** é o que mais influencia a receita;
  taxa de limpeza e número de fotos também acompanham preços maiores.
- **Pergunta 4 (compra):** os maiores retornos estimados, por combinação de imóvel e bairro, são:
- **Apartamento · 2 quartos na Meia Praia** — retorno estimado de 5,18% (receita estimada de R$ 55.646 contra preço de venda de R$ 1.075.000)
- **Apartamento · 2 quartos em Morretes** — retorno estimado de 4,18% (receita estimada de R$ 33.000 contra preço de venda de R$ 790.000)
- **Apartamento · 2 quartos no Centro** — retorno estimado de 3,83% (receita estimada de R$ 44.007 contra preço de venda de R$ 1.150.000)

## Posição sobre a tese interna (compactos no Centro)

- Receita estimada por quarto: compactos R$ 33.807 vs. demais perfis R$ 56.640.
- Retorno anual estimado (%) de compactos no Centro: 3,74% (melhor combinação no Centro: 3,83%; melhor da cidade: 5,18%).

Os dados NÃO SUSTENTAM plenamente a tese dos compactos no Centro: há perfis e bairros com retorno estimado maior. A recomendação é priorizar **Apartamento · 2 quartos na Meia Praia** (retorno estimado de 5,18%) mantendo os compactos do Centro como alternativa de entrada com menor capital.

## Premissas e decisões
- O preço por noite de cada anúncio foi obtido mantendo a **última captura por (anúncio, data de estadia)**.
- Universo de receita = **22,5% da base (977 imóveis)**: os anúncios que estavam **com preço e com avaliações** no momento da coleta. Os demais (3.442) não tinham preço capturado, então não foi possível estimar receita para eles; entram apenas como contexto de mercado.
- **22 anúncios com preço mas sem nenhuma avaliação foram excluídos** (~2%): sem avaliações não há como estimar as noites alugadas (regra D1).
- A **estimativa de receita** usa as avaliações para estimar quantas noites por ano cada imóvel é alugado (`avaliações ÷ 0,5 × 3`, no máximo 365 noites). As colunas **Occ 25% / 35% / 45%** mostram a receita caso o imóvel fique ocupado 25%, 35% ou 45% do ano — servem para verificar se a recomendação muda conforme a premissa.
- Colunas sem dados válidos (`min_nights` e `response_*`) foram excluídas.
- Notas de avaliação com valor 0 (ou seja, "não avaliado") receberam a mediana do mercado.
- Bairros do VivaReal foram padronizados. **"Outros (Andorinha e Castelo Branco)"** reúne os anúncios de venda desses dois bairros (≈19% da oferta de venda) e entra apenas no cálculo do **preço de compra** (divisor do retorno agregado da cidade), já que lá não há dados de aluguel Airbnb — não inventamos uma receita que não existe.
- Bairros sem localização segura foram excluídos do VivaReal (Estreito, Itapema, Ocean Tower e registros sem bairro): 175 anúncios.
- Faixas de quartos: Studio (0q), 1, 2, 3, 4, 5+.
- A Pergunta 1 considera **dois critérios** para "melhor perfil": a **maior receita estimada**
  (resposta: 4 quartos) e o **maior retorno sobre o preço de venda** (resposta: 2 quartos).
  O retorno é o critério decisivo na Pergunta 4.

## Pergunta 1 — Melhor perfil de imóvel para investir na cidade

**Resposta:** a resposta depende do critério adotado. Pela **maior receita estimada**, o melhor perfil é o **Apartamento · 4 quartos** (cerca de R$ 108.000 por ano); pelo **maior retorno estimado sobre o preço de venda** — critério mais relevante para quem investe — é o **Apartamento · 2 quartos** (5,61% ao ano). Os dois critérios estão detalhados abaixo.

| Perfil | N de imóveis | Preço/noite (méd.) | Receita estimada | Occ 25% | Occ 35% | Occ 45% | Receita/quarto |
|---|---|---|---|---|---|---|---|
| Apartamento · 4 quartos | 65 | R$ 900 | R$ 108.000 | R$ 82.125 | R$ 114.975 | R$ 147.825 | R$ 27.000 |
| Apartamento · 3 quartos | 387 | R$ 655 | R$ 71.400 | R$ 59.792 | R$ 83.708 | R$ 107.625 | R$ 23.800 |
| Casa · 1 quarto | 21 | R$ 369 | R$ 56.640 | R$ 33.671 | R$ 47.140 | R$ 60.608 | R$ 56.640 |
| Apartamento · 2 quartos | 329 | R$ 458 | R$ 46.200 | R$ 41.792 | R$ 58.509 | R$ 75.226 | R$ 23.100 |
| Apartamento · 1 quarto | 98 | R$ 427 | R$ 33.807 | R$ 38.964 | R$ 54.549 | R$ 70.135 | R$ 33.807 |

O termo **"melhor"** é propositalmente aberto no enunciado: cabe a nós definir o critério. A tabela abaixo cruza, para cada perfil com dados dos dois lados (anúncio ativo de aluguel + oferta de venda no VivaReal), a receita estimada e o **retorno estimado** (receita anual ÷ preço mediano de venda):

| Perfil | N ativos | Preço/noite | Receita estimada | Preço (mediana) | Retorno (estim.) |
|---|---|---|---|---|---|
| Apartamento · 2 quartos | 329 | R$ 458 | R$ 46.200 | R$ 823.987 | 5,61 |
| Apartamento · 1 quarto | 98 | R$ 427 | R$ 33.807 | R$ 750.000 | 4,51 |
| Apartamento · 3 quartos | 387 | R$ 655 | R$ 71.400 | R$ 1.800.000 | 3,97 |
| Apartamento · 4 quartos | 65 | R$ 900 | R$ 108.000 | R$ 3.500.000 | 3,09 |

**Leitura:** o **Apartamento · 4 quartos** concentra a maior receita bruta, mas exige preço de entrada alto (mediana ~R$ 3,5 milhões) e entrega retorno de ~3,1% ao ano. Já o **Apartamento · 2 quartos**, mesmo com receita menor no absoluto, tem preço de venda acessível (mediana ~R$ 824 mil) e retorno estimado de **5,61% ao ano** — a melhor relação receita/preço da cidade. Por esse critério, a Pergunta 4 recomenda comprar esse perfil. Perfis sem oferta de venda suficiente (ex.: casas) ficam de fora do cruzamento de retorno.

> Perfil = tipo de anúncio + quantidade de quartos. As colunas "Occ" mostram a receita
> estimada se o imóvel ficasse ocupado 25%, 35% ou 45% do ano. Nos cenários de ocupação,
> imóveis de 1 e 2 quartos ficam praticamente empatados (veja a Pergunta 4).

## Pergunta 2 — Melhor localização em termos de receita

**Resposta:** a melhor localização em termos de receita é a **Meia Praia**, com receita estimada de R$ 66.723 por ano — bem à frente do Centro e de Morretes.

| Bairro | N de imóveis | Preço/noite (méd.) | Receita estimada | Occ 35% |
|---|---|---|---|---|
| Meia Praia | 628 | R$ 590 | R$ 66.723 | R$ 75.372 |
| Centro | 189 | R$ 500 | R$ 38.610 | R$ 63.875 |
| Morretes | 82 | R$ 470 | R$ 37.440 | R$ 60.106 |

> Considera bairros com pelo menos 20 imóveis ativos na amostra. A oferta total de anúncios
> por bairro está em `output/mercado_contexto.csv`.

## Pergunta 3 — Características que explicam as melhores receitas

**Resposta:** o tamanho do imóvel é o que mais influencia a receita: quanto mais quartos, maior o preço por noite e maior a receita estimada. Taxa de limpeza e número de fotos também andam junto com preços maiores. Notas e avaliações dos hóspedes têm pouca relação com o preço cobrado.

O foco aqui é o **preço médio por noite** (que compõe a receita) e suas associações com as
características do anúncio. A correlação varia de -1 a +1: quanto mais perto de 1, maior a
associação positiva com o preço por noite; perto de -1, associação inversa; perto de 0, sem
relação clara.

Correlação com o preço médio por noite:
| característica | correlação |
|---|---|
| Número de quartos | 0,58 |
| Taxa de limpeza | 0,39 |
| Número de fotos do anúncio | 0,23 |
| Nota de localização | 0,22 |
| Número de avaliações | -0,14 |
| Nota média (estrelas) | 0,10 |
| Superhost | -0,09 |
| Satisfação geral dos hóspedes | 0,08 |

Comparação por grupos (mediana de preço por noite e de receita estimada):
| Característica | Grupo | N de imóveis | Preço/noite (méd.) | Receita estimada |
|---|---|---|---|---|
| Nº de quartos | 1 quarto | 136 | R$ 384 | R$ 33.807 |
| Nº de quartos | 2 quartos | 346 | R$ 450 | R$ 45.000 |
| Nº de quartos | 3 quartos | 400 | R$ 650 | R$ 71.400 |
| Nº de quartos | 4 quartos | 75 | R$ 975 | R$ 108.000 |
| Tipo de imóvel | apartamento | 893 | R$ 557 | R$ 57.600 |
| Tipo de imóvel | casa | 66 | R$ 470 | R$ 61.500 |
| Superhost | Não | 544 | R$ 575 | R$ 42.000 |
| Superhost | Sim | 433 | R$ 518 | R$ 78.000 |
| Nota média | < 4,8 | 155 | R$ 523 | R$ 55.851 |
| Nota média | >= 4,8 | 822 | R$ 550 | R$ 57.000 |

## Pergunta 4 — O que a Seazone compraria hoje e estimativa de retorno

**Resposta:** a recomendação é comprar **Apartamento · 2 quartos**, com retorno anual estimado em aproximadamente 5,61%, pois combina boa receita estimada (R$ 46.200) com preço mediano de venda razoável (R$ 823.987). Pelo retorno por bairro, na Meia Praia é o melhor lugar.

O retorno é estimado como **receita anual estimada ÷ preço mediano de venda**. Por perfil,
considerando a cidade toda (o preço de venda inclui "Outros (Andorinha e Castelo Branco)"):
| Perfil | N ativos | Preço/noite | Receita estimada | Occ 35% | N de venda | Preço (mediana) | Retorno (estim.) | Retorno (Occ 35%) |
|---|---|---|---|---|---|---|---|---|
| Apartamento · 2 quartos | 329 | 458,0 | R$ 46.200 | R$ 58.509 | 1769 | R$ 823.987 | 5,6 | 7,1 |
| Apartamento · 1 quarto | 98 | 427,0 | R$ 33.807 | R$ 54.549 | 160 | R$ 750.000 | 4,5 | 7,3 |
| Apartamento · 3 quartos | 387 | 655,2 | R$ 71.400 | R$ 83.708 | 3171 | R$ 1.800.000 | 4,0 | 4,7 |
| Apartamento · 4 quartos | 65 | 900,0 | R$ 108.000 | R$ 114.975 | 2147 | R$ 3.500.000 | 3,1 | 3,3 |

Por perfil e bairro (onde há receita e oferta de venda ao mesmo tempo):
| Perfil | Bairro | N ativos | Receita estimada | Occ 35% | N de venda | Preço (mediana) | Retorno (estim.) | Retorno (Occ 35%) |
|---|---|---|---|---|---|---|---|---|
| Apartamento · 2 quartos | Meia Praia | 186 | R$ 55.646 | R$ 57.488 | 244 | R$ 1.075.000 | 5,2 | 5,3 |
| Apartamento · 2 quartos | Morretes | 51 | R$ 33.000 | R$ 59.276 | 1044 | R$ 790.000 | 4,2 | 7,5 |
| Apartamento · 2 quartos | Centro | 62 | R$ 44.007 | R$ 67.516 | 89 | R$ 1.150.000 | 3,8 | 5,9 |
| Apartamento · 3 quartos | Meia Praia | 327 | R$ 71.400 | R$ 83.708 | 1704 | R$ 1.884.860 | 3,8 | 4,4 |
| Apartamento · 1 quarto | Centro | 70 | R$ 33.300 | R$ 55.380 | 22 | R$ 890.000 | 3,7 | 6,2 |
| Apartamento · 1 quarto | Meia Praia | 20 | R$ 30.885 | R$ 56.338 | 58 | R$ 877.500 | 3,5 | 6,4 |
| Apartamento · 4 quartos | Meia Praia | 57 | R$ 108.000 | R$ 114.975 | 1328 | R$ 3.600.000 | 3,0 | 3,2 |
| Apartamento · 3 quartos | Centro | 42 | R$ 60.416 | R$ 95.749 | 438 | R$ 2.100.000 | 2,9 | 4,6 |

Robustez — melhor perfil em cada cenário (1 e 2 quartos empatam): `output/q4_robustez.csv`.

## Limitações
- A janela de preço é de janeiro a abril de 2025 (alta temporada). A estimativa de receita
  pelas avaliações cobre o ano inteiro; os cenários de ocupação verificam a sensibilidade.
- Receita estimada, não contabilizada; a base não traz a taxa de ocupação real.
- Compara universos diferentes (anúncios Airbnb ativos × anúncios de venda): compara-se
  medianas de perfil/bairro, nunca imóvel a imóvel.
- "Outros (Andorinha e Castelo Branco)" não gera retorno próprio (sem receita de aluguel).
