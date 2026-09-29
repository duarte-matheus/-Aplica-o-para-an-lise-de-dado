# 📊 Fintech Analytics — Análise de Transações

Aplicação desenvolvida em Python para o exercício de Ciência de Dados em uma Fintech.

O projeto realiza:

- ingestão do `transacoes.csv` com encoding `latin1`;
- imputação de `NaN` em `valor` usando a mediana por estado;
- criação da coluna `plataforma = "Mobile"`;
- conversão de datas e aplicação do fuso `America/Sao_Paulo`;
- criação de dia da semana e mês;
- remoção de duplicidades;
- classificação de risco com `.map()`;
- filtro vetorizado usando `&` e `|`;
- tabela dinâmica com `pivot_table(..., margins=True)`;
- cálculo vetorizado de Z-Score por estado;
- identificação de possíveis anomalias com `Z > 2.5`;
- gráfico Matplotlib usando a API Orientada a Objetos;
- média móvel de 7 dias;
- dashboard interativo em Streamlit.

## 1. Gerar os dados

O arquivo `criar_dados.py` fornecido no exercício gera:

- `transacoes.csv`
- `cotacoes.csv`

Execute:

```bash
python criar_dados.py
```

O gerador cria as transações de setembro de 2026, incluindo valores ausentes e duplicidades para testar o pipeline.

## 2. Instalar dependências

Recomendado usar um ambiente virtual:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Depois:

```bash
pip install -r requirements.txt
```

## 3. Executar a aplicação

```bash
streamlit run app.py
```

O navegador abrirá o dashboard.

## 4. Estrutura

```text
fintech_analise_transacoes/
├── app.py
├── criar_dados.py
├── requirements.txt
├── README.md
├── .gitignore
├── transacoes.csv
└── cotacoes.csv
```

Os CSVs podem ser gerados localmente pelo script e não precisam ser versionados no GitHub se a entrega preferir manter apenas os arquivos-fonte.

## 5. Publicar no GitHub

Crie um repositório no GitHub e, dentro desta pasta, execute:

```bash
git init
git add .
git commit -m "Projeto de análise de transações fintech"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git push -u origin main
```

Substitua a URL pelo seu repositório.

## Observação sobre `cotacoes.csv`

O enunciado informa a existência do arquivo de cotações, e o script gerador cria esse arquivo. A aplicação o carrega e apresenta a cotação USD como informação auxiliar no dashboard. As métricas obrigatórias do exercício são calculadas a partir de `transacoes.csv`, conforme os requisitos descritos.
