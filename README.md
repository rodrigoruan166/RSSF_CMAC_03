# 📡 Roteamento em Redes de Sensores Sem Fio para Monitoramento Ambiental

Este projeto foi desenvolvido como parte da disciplina **CMAC03 – Algoritmos em Grafos** (1º semestre de 2025 - UNIFEI) e tem como objetivo comparar algoritmos de roteamento em Redes de Sensores Sem Fio (RSSF) voltadas ao monitoramento de incêndios florestais e condições ambientais em florestas plantadas.

## 🔍 Contexto

A aplicação de RSSFs em áreas florestais é uma solução moderna para o monitoramento contínuo de indicadores ambientais, como temperatura e umidade do solo. Um dos grandes desafios é o consumo de energia dos sensores (motes), que afeta diretamente o tempo de vida da rede. O projeto visa avaliar estratégias de roteamento com foco na **eficiência energética** e **vida útil da rede**.

## 🎯 Objetivos

- Simular e comparar três estratégias de roteamento:
  - **Comunicação Direta**
  - **LEACH (Low-Energy Adaptive Clustering Hierarchy)**
  - **E-LEACH (Enhanced LEACH)**
- Avaliar métricas como:
  - Vida útil média dos sensores
  - Tempo até a morte do primeiro nó
  - Energia média dos sensores vivos por rodada
- Identificar a melhor estratégia em termos de balanceamento de energia e prolongamento da rede.

## 🧠 Modelagem

A RSSF foi modelada como um grafo ponderado:
- Cada sensor representa um **vértice**.
- A **distância euclidiana** entre sensores ou até a estação base define as **arestas**.
- Os sensores podem enviar dados diretamente à estação base (ERB) ou por meio de **Cluster Heads (CHs)**.

## 🛠️ Implementação

O projeto é composto por diferentes módulos de simulação:

- `main.py` – Executa as simulações e gera gráficos comparativos.
- `direto.py` – Implementação da estratégia de Comunicação Direta.
- `LEACH.py` – Implementação do protocolo LEACH clássico.
- `ELEACH.py` – Implementação do protocolo E-LEACH, com decisões baseadas na energia residual.

Todos os algoritmos foram desenvolvidos com **parâmetros energéticos** baseados no artigo do EESRA (https://ieeexplore.ieee.org/document/8765561), para garantir comparação justa.

## 📊 Resultados

As simulações geram gráficos comparativos salvos na pasta `results/`, incluindo:

- Número de nós vivos por rodada
- Energia média dos nós vivos por rodada
- Vida útil da rede (número médio de rodadas por sensor)
- Rodada de morte do primeiro nó

## ▶️ Como Executar

A partir da pasta raíz execute o seguinte comando:

```bash
pip install -r requirements.txt
cd code
python main.py
