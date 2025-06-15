from direto import simulate_direct_communication
from LEACH import simulate_leach
from ELEACH import simulate_eleach
import matplotlib.pyplot as plt
import numpy as np

def calcular_vida_util(alive_list):
    # Conta quantas rodadas ainda havia nós vivos
    alive_filtered = list(filter(lambda n: n != 0, alive_list))
    return len(alive_filtered)

if __name__ == "__main__":
    ARQUIVO_COORDENADAS = "../dataset/400.txt"
    NUM_RODADAS = 20000 # altere
    NUM_SIMULACOES = 3  # Quantidade de simulações

    # # Simulações
    # _, _, alive_direct, energy_direct, media_vida_direct, first_node_death_round_direct = simulate_direct_communication(
    #     file_path=ARQUIVO_COORDENADAS,
    #     num_rounds=NUM_RODADAS
    # )

    # _, _, alive_leach, energy_leach, media_vida_leach, first_node_death_round_leach = simulate_leach(
    #     file_path=ARQUIVO_COORDENADAS,
    #     num_rounds=NUM_RODADAS
    # )

    # _, _, alive_eleach, energy_eleach, media_vida_eleach, first_node_death_round_eleach = simulate_eleach(
    #     file_path=ARQUIVO_COORDENADAS,
    #     num_rounds=NUM_RODADAS
    # )

    # # Rodadas (eixo X)
    # round_axis = range(1, NUM_RODADAS + 1)

    # # Definindo cores fixas para os protocolos
    # colors = {
    #     'Direta': 'blue',
    #     'LEACH': 'green',
    #     'E-LEACH': 'red'
    # }

    # # Criação da figura com 2 linhas e 2 colunas
    # plt.figure(figsize=(14, 10))

    # # Subplot 1: Nós Vivos
    # plt.subplot(2, 2, 1)
    # plt.plot(round_axis, alive_direct, label='Direta', linestyle='-', marker='.', color=colors['Direta'])
    # plt.plot(round_axis, alive_leach, label='LEACH', linestyle='--', marker='x', color=colors['LEACH'])
    # plt.plot(round_axis, alive_eleach, label='E-LEACH', linestyle='-.', marker='o', color=colors['E-LEACH'])
    # plt.title('Nós Vivos por Rodada')
    # plt.xlabel('Rodada')
    # plt.ylabel('Número de Nós Vivos')
    # plt.grid(True)
    # plt.legend()

    # # Subplot 2: Energia Média
    # plt.subplot(2, 2, 2)
    # plt.plot(round_axis, energy_direct, label='Direta', linestyle='-', marker='.', color=colors['Direta'])
    # plt.plot(round_axis, energy_leach, label='LEACH', linestyle='--', marker='x', color=colors['LEACH'])
    # plt.plot(round_axis, energy_eleach, label='E-LEACH', linestyle='-.', marker='o', color=colors['E-LEACH'])
    # plt.title('Energia Média por Rodada (Sensores Vivos)')
    # plt.xlabel('Rodada')
    # plt.ylabel('Energia Média (J)')
    # plt.grid(True)
    # plt.legend()

    # # Subplot 3: Média de Vida dos Nós
    # plt.subplot(2, 2, 3)
    # protocolos = ['Direta', 'LEACH', 'E-LEACH']
    # medias_vida = [media_vida_direct, media_vida_leach, media_vida_eleach]
    # plt.bar(protocolos, medias_vida, color=[colors[p] for p in protocolos])
    # plt.title('Média de Rodadas Vividas por Sensor')
    # plt.ylabel('Rodadas')
    # plt.grid(axis='y')

    # # Subplot 4: Rodada da Morte do Primeiro Nó (FND)
    # plt.subplot(2, 2, 4)
    # first_node_deaths = [first_node_death_round_direct, first_node_death_round_leach, first_node_death_round_eleach]
    # plt.bar(protocolos, first_node_deaths, color=[colors[p] for p in protocolos])
    # plt.title('Rodada da Morte do Primeiro Nó')
    # plt.ylabel('Rodada')
    # plt.grid(axis='y')

    # # Ajusta layout e salva
    # plt.tight_layout()
    # plt.savefig(f"../results/comparacao_protocolos_2x2_{ARQUIVO_COORDENADAS.replace('.txt', '').replace('../dataset/', '')}.png")
    # print("\nGráfico salvo como 'comparacao_protocolos_2x2.png'")
    # print(alive_direct[-1], alive_leach[-1], alive_eleach[-1])

    vidas_direct = []
    vidas_leach = []
    vidas_eleach = []

    for i in range(NUM_SIMULACOES):
        print(f"Simulação {i+1} de {NUM_SIMULACOES}...")

        _, _, alive_direct, _, _, _ = simulate_direct_communication(
            file_path=ARQUIVO_COORDENADAS,
            num_rounds=NUM_RODADAS
        )

        _, _, alive_leach, _, _, _ = simulate_leach(
            file_path=ARQUIVO_COORDENADAS,
            num_rounds=NUM_RODADAS
        )

        _, _, alive_eleach, _, _, _ = simulate_eleach(
            file_path=ARQUIVO_COORDENADAS,
            num_rounds=NUM_RODADAS
        )

        vidas_direct.append(calcular_vida_util(alive_direct))
        vidas_leach.append(calcular_vida_util(alive_leach))
        vidas_eleach.append(calcular_vida_util(alive_eleach))

    # Configuração do gráfico de barras agrupadas
    indices = np.arange(NUM_SIMULACOES)
    largura_barra = 0.25

    plt.figure(figsize=(10, 6))

    # Ordem: Direta (esquerda, azul), LEACH (meio, verde), E-LEACH (direita, vermelho)
    plt.bar(indices - largura_barra, vidas_direct, width=largura_barra, label='Direta', color='blue')
    plt.bar(indices, vidas_leach, width=largura_barra, label='LEACH', color='green')
    plt.bar(indices + largura_barra, vidas_eleach, width=largura_barra, label='E-LEACH', color='red')

    plt.xlabel(f"Índice da simulação - {ARQUIVO_COORDENADAS.replace('.txt', '').replace('../dataset/', '')} Sensores")
    plt.ylabel('Vida Útil da Rede (Round)')
    plt.title('Comparação da Vida Útil da Rede')
    plt.xticks(indices, [str(i + 1) for i in indices])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"../results/vida_util_barras_simulacoes_{ARQUIVO_COORDENADAS.replace('.txt', '').replace('../dataset/', '')}.png")
    plt.show()
