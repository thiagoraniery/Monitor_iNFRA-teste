# Monitor iNFRA

> Pipeline automatizado para monitoramento e análise de dados dos setores de Infraestrutura.

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat-square&logo=streamlit)](https://monitor-infra-thiago.streamlit.app)
![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)
![Status](https://img.shields.io/badge/Status-Em%20Produ%C3%A7%C3%A3o-green.svg?style=flat-square)

## Sobre o Projeto

O objetivo deste projeto foi substituir o monitoramento manual do portal de notícias por uma solução de **Business Intelligence (BI)** dinâmica e 100% automatizada. 

O sistema realiza o scraping diário de dados, aplica regras de negócio para classificação e disponibiliza uma interface visual para suporte à tomada de decisão estratégica em infraestrutura.

## Funcionalidades

* 📊 **Dashboard Executivo:** KPIs de volume de notícias e temas predominantes.
* 🔍 **Filtragem Avançada:** Seleção dinâmica por período (Data), Tópicos (Saneamento, Energia, Mineração...) e busca textual.
* 📈 **Visualização de Dados:** Gráficos interativos para análise de tendências de mercado.
* 📰 **Feed Interativo:** Leitura rápida de manchetes com acesso direto à fonte original.

## Tecnologias Utilizadas

A arquitetura utiliza uma stack tecnológica integrada para automação de dados em nuvem:

* **Streamlit:** Interface de usuário e visualização de dados.
* **Supabase:** Banco de dados relacional na nuvem (PostgreSQL).
* **GitHub Actions:** Orquestração de rotinas automatizadas (CI/CD).
* **Selenium:** Automação de extração de dados (Web Scraping).
* **Pandas & NumPy:** Manipulação, limpeza e tratamento de dados.

## 📂 Estrutura dos Arquivos

| Arquivo | Descrição |
| :--- | :--- |
| `app.py` | Código principal do Dashboard Streamlit. |
| `infra_auto_completo.py` | Robô de extração de dados (Scraper). |
| `upload_supabase.py` | Script de integração e sincronização com o banco de dados. |
| `.github/workflows/` | Configurações da automação agendada. |
| `requirements.txt` | Lista de bibliotecas e dependências do projeto. |

---
**Desenvolvido por Thiago Raniery** 
