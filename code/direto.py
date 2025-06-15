'''
Código adaptado de comunicação direta entre sensores e estação base
com parâmetros de energia equivalentes ao EESRA e LEACH adaptado
para fins de comparação.
'''
import math
import random
from collections import defaultdict
import numpy as np

# --- Constantes de Energia (Baseadas no EESRA) ---
E_ELEC = 50e-9      # J/bit (Energia para eletrônica)
E_FS = 10e-12       # J/bit/m² (Energia para espaço livre)
E_MP = 0.0013e-12   # J/bit/m^4 (Energia para multi-percurso)
D_THRESHOLD = 75   # Metros (Limiar de distância para modelo de energia)
E_DA = 5e-9         # J/bit (Energia para agregação de dados)
PACKET_SIZE = 2000  # bits (Tamanho do pacote)
INITIAL_ENERGY = 2.0 # Joules (Energia inicial dos nós)
E_SENSE = 8e-5
E_SLEEP = 15e-10
NETWORK_FUNCTIONAL_THRESHOLD = 0.2 # 20% dos nós devem estar vivos para considerar a rede funcional sem problemas (comparação justa)

class SensorNode:
    def __init__(self, node_id, x, y, base_station):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.base_station = base_station
        self.energy = INITIAL_ENERGY  # Energia inicial em Joules (igual ao EESRA)
        self.data = []
        self.alive = True
        self.sleeping = False
        self.rounds_alive = 0
        
    def distance_to(self, other):
        '''Calcula a distância Euclidiana para outro nó ou estação base.'''
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        
    def transmit_energy(self, k, d):
        '''Calcula a energia gasta para transmitir k bits a uma distância d.'''
        if d <= D_THRESHOLD:
            return k * (E_ELEC + E_FS * d**2)
        else:
            return k * (E_ELEC + E_MP * d**4)

    def receive_energy(self, k):
        '''Calcula a energia gasta para receber k bits.'''
        return k * E_ELEC
    
    
    def sense_environment(self, temperature):
        """Simula a detecção de temperatura"""
        if not self.alive or self.sleeping:
            return

        if self.energy <= E_SENSE:
            self.alive = False
            self.energy = 0
            return

        self.energy -= E_SENSE            
        self.data.append(temperature)
    
    def send_data_to_base(self):
        """Envia dados diretamente para a estação base"""
        if not self.alive or self.sleeping or not self.data:
            return False
        
        # Calcula distância até a base
        distance = self.distance_to(self.base_station)
        
        # Calcula consumo de energia para envio usando o modelo do EESRA
        tx_energy = self.transmit_energy(PACKET_SIZE, distance)
        
        # Verifica se tem energia suficiente
        if self.energy < tx_energy:
            self.energy = 0
            self.alive = False
            return False
        
        # Deduz energia do envio
        self.energy -= tx_energy
        
        # Envia os dados para a base
        self.base_station.receive_data(self.node_id, self.data.copy())
        self.data = []  # Limpa os dados após envio

        return True
    
    def sleep_mode(self):
        if self.energy <= E_SLEEP:
            self.alive = False
            self.energy = 0
            return
        
        self.energy -= E_SLEEP
        return

class BaseStation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = float('inf')  # Energia infinita
        self.received_data = defaultdict(list)
        self.alerts = []
    
    def receive_data(self, node_id, data):
        """Recebe dados dos nós sensores"""
        self.received_data[node_id].extend(data)
        
        # Verifica alertas de incêndio
        for temp in data:
            if temp > 60:  # Limite de temperatura para incêndio
                self.alerts.append((node_id, temp))
                print(f"ALERTA DE INCÊNDIO! Nó {node_id} detectou temperatura {temp}°C")

def read_coordinates_from_file(file_path):
    with open(file_path, 'r') as file:
        num_nodes = int(file.readline().strip())
        
        bs_line = file.readline().strip()
        bs_line = bs_line.replace('"', '').replace("'", "")
        bs_parts = bs_line.replace(',', ' ').split()
        bs_pos = (float(bs_parts[0]), float(bs_parts[1]))
        
        sensor_coords = []
        for _ in range(num_nodes):
            line = file.readline().strip()
            if not line:
                continue
            line = line.replace('"', '').replace("'", "")
            parts = line.replace(',', ' ').split()
            x = float(parts[0])
            y = float(parts[1])
            sensor_coords.append((x, y))
            
    return num_nodes, bs_pos, sensor_coords

def simulate_direct_communication(file_path, num_rounds):
    '''Executa a simulação de comunicação direta.'''
    num_nodes, bs_pos, sensor_coords = read_coordinates_from_file(file_path)

    base_station = BaseStation(bs_pos[0], bs_pos[1])
    # Cria nós sensores com posições aleatórias
    nodes = [
        SensorNode(i, x, y, base_station)
        for i, (x,y) in enumerate(sensor_coords)
    ]

    alive_history = [0 for _ in range(num_rounds)]
    energy_history = [0 for _ in range(num_rounds)]

    print(f"Iniciando simulação de Comunicação Direta com {num_nodes} nós.")
    print(f"Energia Inicial: {INITIAL_ENERGY} J, Pacote: {PACKET_SIZE} bits")
    print("-" * 30)

    first_node_death_round = None

    for round_num in range(num_rounds):
        alive_nodes = sum(node.alive for node in nodes)
        percent_network_alive = alive_nodes/num_nodes

        if alive_nodes != num_nodes and first_node_death_round == None:
            first_node_death_round = round_num + 1

        if percent_network_alive <= NETWORK_FUNCTIONAL_THRESHOLD:
            break

        print(f'\n--- Rodada {round_num + 1} ---')

        if not any(node.alive for node in nodes):
            print("Todos os nós morreram. Fim da simulação.")
            break
                
        # Alguns nós detectam temperatura e enviam dados
        nodes_sent = 0
        for node in nodes:
            #if node.alive and random.random() < 0.3:  # 30% chance de atividade por rodada
            if node.alive:
                node.rounds_alive += 1
                # Simula detecção de temperatura
                if random.random() < 0.1:  # 10% chance de incêndio
                    temp = random.uniform(60, 100)
                else:
                    temp = random.uniform(20, 50)
                
                node.sense_environment(temp)
                
                # Tenta enviar dados para a BS
                if node.alive and node.data:
                    if node.send_data_to_base():
                        nodes_sent += 1

        print(f"Nós que enviaram dados para BS: {nodes_sent}")

        for node in nodes:
            if node.alive:
                node.sleep_mode()

        # Relatórios da rodada
        alive_nodes = sum(1 for node in nodes if node.alive)
        total_energy = sum(node.energy for node in nodes if node.alive)
        avg_energy = total_energy / max(1, num_nodes)
        
        alive_history[round_num] = alive_nodes
        energy_history[round_num] = avg_energy

        print(f"Nós vivos: {alive_nodes}/{num_nodes}")
        print(f"Energia média dos nós vivos: {avg_energy:.6f} J")

        if alive_nodes == 0:
            print("\nTodos os nós morreram. Fim da simulação.")
            break
            
    print(f"\n--- Fim da Simulação (Após {round_num + 1} rodadas) ---")
    show_final_results(nodes, base_station)

    rounds_vividas = [node.rounds_alive for node in nodes]
    media_vida_nos = sum(rounds_vividas) / len(rounds_vividas)

    print(media_vida_nos)

    return nodes, base_station, alive_history, energy_history, media_vida_nos, first_node_death_round

def show_final_results(nodes, base_station):
    '''Mostra os resultados finais da simulação.'''
    num_nodes = len(nodes)
    alive_nodes_list = [node for node in nodes if node.alive]
    dead_nodes_list = [node for node in nodes if not node.alive]
    alive_count = len(alive_nodes_list)
    dead_count = len(dead_nodes_list)

    print(f"\n--- Resultados Finais ---")
    print(f"Total de alertas de incêndio: {len(base_station.alerts)}")
    print(f"Nós Vivos: {alive_count}/{num_nodes}")
    print(f"Nós Mortos: {dead_count}/{num_nodes}")

    if alive_nodes_list:
        avg_energy_alive = sum(node.energy for node in alive_nodes_list) / alive_count
        print(f"Energia média final dos nós vivos: {avg_energy_alive:.6f} J")
    else:
        print("Nenhum nó sobreviveu.")

# --- Exemplo de Uso --- 
if __name__ == "__main__":
    # Parâmetros da Simulação (semelhantes ao EESRA para comparação)
    ARQUIVO_COORDENADAS = "400.txt"
    NUM_RODADAS = 300       # Número máximo de rodadas

    nodes, bs, alive_hist, energy_hist, media_vida_nos, first_node_death_round = simulate_direct_communication(
        file_path= ARQUIVO_COORDENADAS,
        num_rounds=NUM_RODADAS
    )

    # Geração de gráficos
    try:
        import matplotlib.pyplot as plt
        
        rounds_executed = len(alive_hist)
        round_axis = range(1, rounds_executed + 1)

        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.plot(round_axis, alive_hist, marker='.')
        plt.title('Nós Vivos por Rodada')
        plt.xlabel('Rodada')
        plt.ylabel('Número de Nós Vivos')
        plt.grid(True)

        plt.subplot(1, 2, 2)
        plt.plot(round_axis, energy_hist, marker='.', color='orange')
        plt.title('Energia Média por Rodada (Nós Vivos)')
        plt.xlabel('Rodada')
        plt.ylabel('Energia Média (J)')
        plt.grid(True)

        plt.tight_layout()
        plt.savefig("comunicacao_direta_resultados.png")
        print("\nGráficos salvos em 'comunicacao_direta_resultados.png'")
        #plt.show() # Descomente para mostrar o gráfico interativamente

    except ImportError:
        print("\nMatplotlib não encontrado. Instale com 'pip install matplotlib' para gerar gráficos.")
