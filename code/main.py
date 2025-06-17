from direto import simulate_direct_communication
from LEACH import simulate_leach
from ELEACH import simulate_eleach
import matplotlib.pyplot as plt
import os.path

def plota_informacoes_com_vida_util(NUM_RODADAS, ARQUIVO_COORDENADAS):
    # Simulações
    _, _, alive_direct, energy_direct, media_vida_direct, _ = simulate_direct_communication(
        file_path=ARQUIVO_COORDENADAS,
        num_rounds=NUM_RODADAS,
    )

    _, _, alive_leach, energy_leach, media_vida_leach, _ = simulate_leach(
        file_path=ARQUIVO_COORDENADAS,
        num_rounds=NUM_RODADAS,
    )

    _, _, alive_eleach, energy_eleach, media_vida_eleach, _ = simulate_eleach(
        file_path=ARQUIVO_COORDENADAS,
        num_rounds=NUM_RODADAS,
    )

    # Calcula a vida útil para cada abordagem
    vida_direct = calcular_vida_util(alive_direct)
    vida_leach = calcular_vida_util(alive_leach)
    vida_eleach = calcular_vida_util(alive_eleach)

    # Determina o limite do eixo X com base na menor vida útil
    menor_vida_util = min(vida_direct, vida_leach, vida_eleach)
    round_axis = range(1, menor_vida_util + 1)

    # Definindo cores fixas para os protocolos
    colors = {
        'Direta': 'blue',
        'LEACH': 'green',
        'E-LEACH': 'red'
    }

    # Criação da figura com 2 linhas e 2 colunas
    plt.figure(figsize=(14, 10))

    # Subplot 4: Vida Útil da Rede
    plt.subplot(2, 2, 4)
    protocolos = ['Direta', 'LEACH', 'E-LEACH']
    vidas = [vida_direct, vida_leach, vida_eleach]
    plt.bar(protocolos, vidas, color=[colors[p] for p in protocolos])
    plt.title('Vida Útil da Rede')
    plt.ylabel('Rodadas')
    plt.grid(axis='y')

    # Subplot 2: Nós Vivos
    plt.subplot(2, 2, 1)
    plt.plot(round_axis, alive_direct[:menor_vida_util], label='Direta', linestyle='-', marker='.', color=colors['Direta'])
    plt.plot(round_axis, alive_leach[:menor_vida_util], label='LEACH', linestyle='--', marker='x', color=colors['LEACH'])
    plt.plot(round_axis, alive_eleach[:menor_vida_util], label='E-LEACH', linestyle='-.', marker='o', color=colors['E-LEACH'])
    plt.title('Nós Vivos por Rodada')
    plt.xlabel('Rodada')
    plt.ylabel('Número de Nós Vivos')
    plt.grid(True)
    plt.legend()

    # Subplot 3: Energia Média
    plt.subplot(2, 2, 2)
    plt.plot(round_axis, energy_direct[:menor_vida_util], label='Direta', linestyle='-', marker='.', color=colors['Direta'])
    plt.plot(round_axis, energy_leach[:menor_vida_util], label='LEACH', linestyle='--', marker='x', color=colors['LEACH'])
    plt.plot(round_axis, energy_eleach[:menor_vida_util], label='E-LEACH', linestyle='-.', marker='o', color=colors['E-LEACH'])
    plt.title('Energia Média por Rodada (Sensores Vivos)')
    plt.xlabel('Rodada')
    plt.ylabel('Energia Média (J)')
    plt.grid(True)
    plt.legend()

    # Subplot 1: Média de Vida dos Nós
    plt.subplot(2, 2, 3)
    medias_vida = [media_vida_direct, media_vida_leach, media_vida_eleach]
    plt.bar(protocolos, medias_vida, color=[colors[p] for p in protocolos])
    plt.title('Média de Rodadas Vividas por Sensor')
    plt.ylabel('Rodadas')
    plt.grid(axis='y')

    # Ajusta layout e salva
    plt.tight_layout()
    nome_base = ARQUIVO_COORDENADAS.replace('.txt', '').replace('../dataset/', '')
    plt.savefig(f"../results/comparacao_protocolos_2x2_MEDIA_VIVA_{nome_base}.png")
    print(f"\nGráfico salvo como 'comparacao_protocolos_2x2_MEDIA_VIVA_{nome_base}.png'")
    print(f"Vida útil (últimos nós vivos): Direta={vida_direct}, LEACH={vida_leach}, E-LEACH={vida_eleach}")
    plt.show()

    return round(max(vida_direct, vida_leach, vida_eleach))

def calcular_vida_util(alive_list):
    # Conta quantas rodadas ainda havia nós vivos
    alive_filtered = list(filter(lambda n: n != 0, alive_list))
    return len(alive_filtered)

def main():
    print('**Caso deseje adicionar novos arquivos, inclua-os à pasta "dataset" com o nome "quantidade de sensores".txt**')
    print('Inicialmente, estão disponíveis quatro arquivos com 50, 100, 200 e 400 sensores.')
    quantidade_sensores = input('Digite a quantidade de sensores desejada (50, 100, 200, 400): ')

    ARQUIVO_COORDENADAS=f"../dataset/{quantidade_sensores}.txt"

    if not os.path.isfile(ARQUIVO_COORDENADAS):
        print('Arquivo não encontrado.')
        return

    try:
        NUM_RODADAS = int(input('Digite a quantidade de rodadas: '))
    except:
        print('Quantidade de rodadas inválida.')
        return

    plota_informacoes_com_vida_util(NUM_RODADAS, ARQUIVO_COORDENADAS)

if __name__ == "__main__":
    main()
