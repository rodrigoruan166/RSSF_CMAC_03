'''
Implementação do protocolo LEACH
'''
import math
import random
from collections import defaultdict

# --- Constantes de Energia baseadas no artigo do EESRA para comparação leal (https://ieeexplore.ieee.org/document/8765561) ---
E_ELEC = 50e-9      # J/bit (Energia para eletrônica)
E_FS = 10e-12       # J/bit/m² (Energia para espaço livre)
E_MP = 0.0013e-12   # J/bit/m^4 (Energia para multi-percurso)
D_THRESHOLD = 75   # Metros (Limiar de distância para modelo de energia)
E_DA = 5e-9         # J/bit (Energia para agregação de dados)
PACKET_SIZE = 2000  # bits (Tamanho do pacote)
INITIAL_ENERGY = 2.0 # Joules (Energia inicial dos nós)
P = 0.3             # Probabilidade de um nó se tornar CH (fixa)
E_SENSE = 8e-5    #Joules por segundo (energia do sensoriamento)
E_SLEEP = 15e-10  #Joules por intervalor de sleep
NETWORK_FUNCTIONAL_THRESHOLD = 0.12

# A rede é modelada em forma de um grafo ponderado. A classe SensorNode é considerada o vértice do grafo
# e a aresta é calculada dinâmicamente baseado na distância entre ERB, CH ou Sensor comum.
class SensorNode:
    def __init__(self, node_id, x, y, base_station):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.base_station = base_station
        self.energy = INITIAL_ENERGY
        self.data = []
        self.alive = True
        self.is_cluster_head = False
        self.cluster_head = None
        self.member_nodes = []
        self.last_ch_round = -1
        self.is_direct = False
        self.rounds_alive = 0

    # Calcula a distância euclidiana entre dois sensores no plano catersiano (x, y), conforme as posições passadas no dataset
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def sleep_mode(self):
        self.energy -= E_SLEEP
        return

    # Calcula a energia necessária para transmitir dados a partir do tamanho do pacote e distância
    def transmit_energy(self, k, d):
        if d <= D_THRESHOLD:
            return k * (E_ELEC + E_FS * d**2)
        else:
            return k * (E_ELEC + E_MP * d**4)

    def receive_energy(self, k):
        return k * E_ELEC

    # Calcula a quantidade de energia necessária para agregar os pacotes
    def aggregate_energy(self, num_packets):
        return num_packets * PACKET_SIZE * E_DA

    def become_cluster_head(self, round_num):
        self.is_cluster_head = True
        self.cluster_head = None
        self.member_nodes = []
        self.last_ch_round = round_num

    def reset_cluster_role(self):
        self.is_cluster_head = False
        self.cluster_head = None
        self.member_nodes = []
        self.is_direct = False

    # Método para o sensor sensoriar a temperatura
    def sense_environment(self, temperature):
        if not self.alive:
            return
        
        if self.energy < E_SENSE:
            self.alive = False
            self.energy = 0
            return

        self.energy -= E_SENSE
        self.data.append(temperature)

    # Envia dados diretamente à ERB em alguns casos, como ERB mais próxima do sensor que o CH mais próximo
    def send_data_direct_to_base(self):
        if not self.alive or self.is_cluster_head or self.cluster_head or not self.is_direct or not self.data:
            return False
        
        # Distância entre o sensor e a ERB
        distance = self.distance_to(self.base_station)

        # Energia que será necessária para transmitir o pacote à ERB
        tx_cost = self.transmit_energy(PACKET_SIZE, distance)
        
        # Energia não é mais suficiente para enviar dados
        if self.energy < tx_cost:
            self.energy = 0
            self.alive = False
            return False
        
        # Envia os dados à ERB e desconta a energia usada para a transmissão no sensor
        self.energy -= tx_cost
        self.base_station.receive_data(self.node_id, self.data.copy())
        self.data = []

        if self.energy <= 0:
            self.energy = 0
            self.alive = False
            
        return True

    # Envia dados para o CH
    def send_data_to_cluster_head(self):
        if not self.alive or self.is_cluster_head or not self.cluster_head or not self.data:
            return False

        ch = self.cluster_head
        # Verifica se o CH ainda está vivo, caso contrário remove o CH e retorna false para o sensor ser reconfigurado
        if not ch.alive:
            self.cluster_head = None
            return False

        distance = self.distance_to(ch)
        tx_cost = self.transmit_energy(PACKET_SIZE, distance)
        rx_cost_ch = ch.receive_energy(PACKET_SIZE)

        # Verifica se tem energia suficiente para enviar ao CH e o CH possui energia suficiente para receber
        if self.energy < tx_cost or ch.energy < rx_cost_ch:
            if self.energy < tx_cost:
                self.energy = 0
                self.alive = False
            return False

        # Deduz energia de envio do sensor
        self.energy -= tx_cost
        ch.energy -= rx_cost_ch

        # Envia os dados ao CH
        ch.receive_data_from_member(self.node_id, self.data.copy())
        self.data = []

        if ch.energy <= 0:
            ch.energy = 0
            ch.alive = False

        if self.energy <= 0:
            self.energy = 0
            self.alive = False
            
        return True

    def receive_data_from_member(self, member_id, data):
        if not self.alive or not self.is_cluster_head:
            return

        self.data.extend(data)

    # CH envia os dados agregados dos sensores membros à ERB
    def send_aggregated_data_to_base(self):
        if not self.alive or not self.is_cluster_head or not self.data:
            return False

        # Distância do CH à ERB
        distance_to_bs = self.distance_to(self.base_station)

        # Custo energético para enviar todos pacotes do cluster
        num_aggregated_packets = len(self.member_nodes)
        aggregate_cost = self.aggregate_energy(num_aggregated_packets)


        transmit_cost = self.transmit_energy(PACKET_SIZE + aggregate_cost, distance_to_bs)
        total_cost = transmit_cost

        # Energia não é suficiente para enviar os dados
        if self.energy < total_cost:
            self.energy = 0
            self.alive = False
            return False

        self.energy -= total_cost
        self.base_station.receive_data(self.node_id, self.data.copy())
        self.data = []

        if self.energy <= 0:
            self.energy = 0
            self.alive = False
            
        return True

class BaseStation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = float('inf')
        self.received_data = defaultdict(list)
        self.alerts = []

    def receive_data(self, node_id, data):
        self.received_data[node_id].extend(data)
        for temp in data:
            if temp > 60:
                self.alerts.append((node_id, temp))
                print(f"ALERTA DE INCÊNDIO! CH {node_id} reportou temperatura {temp}°C")

def setup_leach(nodes, round_num):
    '''Seleção de CHs usando o mecanismo probabilístico do LEACH'''
    for node in nodes:
        node.reset_cluster_role()

    alive_nodes = [node for node in nodes if node.alive]

    if not alive_nodes:
        return []

    cluster_heads = []

    for node in alive_nodes:
        # https://s3.ap-northeast-2.amazonaws.com/journal-home/journal/jips/fullText/456/10.pdf
        # É utilizado o limiar T(n) = P/(1-P*(r mod (1/P))) do LEACH original, desprezando a energia residual
        if round_num - node.last_ch_round >= 1/P:
            if P/(1 - P * (round_num % (1/P))) > random.random():
                node.become_cluster_head(round_num)
                cluster_heads.append(node)

    # Formação dos clusters
    non_ch_nodes = [node for node in alive_nodes if not node.is_cluster_head]
    # Configura os sensores para enviarem mensagem pro cluster head mais próximo
    for node in non_ch_nodes:
        if len(cluster_heads) != 0:
            closest_ch = min(cluster_heads, key=lambda ch: node.distance_to(ch))
            dist_to_base = node.distance_to(node.base_station)
            dist_to_ch = node.distance_to(closest_ch)

            # Caso a distância entre o sensor e a ERB seja menor que o sensor e o CH, envie diretamente para a ERB
            if dist_to_base < dist_to_ch:
                node.is_direct = True
                node.cluster_head = None
            else:
                node.cluster_head = closest_ch
                closest_ch.member_nodes.append(node)
        else:
            # Caso não exista nenhum cluster head, os nós enviam diretamente para a ERB
            node.is_direct = True

    return cluster_heads

# Lê os dados de um arquivo, onde:
# 1º linha é referente a quantidade de sensores na RSSF
# 2º linha: coordenada no plano cartesiano da ERB
# 3º linha em diante: coordenadas no plano cartesiano dos sensores
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

'''Executa a simulação do LEACH'''
def simulate_leach(file_path, num_rounds):
    num_nodes, bs_pos, sensor_coords = read_coordinates_from_file(file_path)

    base_station = BaseStation(bs_pos[0], bs_pos[1])
    nodes = [
        SensorNode(i, x, y, base_station)
        for i, (x,y) in enumerate(sensor_coords)
    ]

    alive_history = [0 for _ in range(num_rounds)]
    energy_history = [0 for _ in range(num_rounds)]

    print(f"Iniciando simulação LEACH com {num_nodes} nós.")
    print(f"Energia Inicial: {INITIAL_ENERGY} J, Pacote: {PACKET_SIZE} bits, P={P}")
    print("-" * 30)

    first_node_death_round = None

    for round_num in range(num_rounds):
        alive_nodes = sum(node.alive for node in nodes)
        percent_network_alive = alive_nodes/num_nodes

        if alive_nodes != num_nodes and first_node_death_round == None:
            first_node_death_round = round_num + 1

        if percent_network_alive <= NETWORK_FUNCTIONAL_THRESHOLD:
            break

        # Fase de Setup

        nodes_sent_to_ch = 0
        nodes_sent_direct = 0

        # Fase de Set-Up (https://iris.uniroma1.it/retrieve/e3835329-b073-15e8-e053-a505fe0a3de9/Zanaj_post-print_LEACH_2015.pdf)
        cluster_heads = setup_leach(nodes, round_num)
        ch_ids = [ch.node_id for ch in cluster_heads if ch.alive]
        print(f"\n--- Rodada {round_num + 1} ---")
        print(f"CHs Eleitos ({len(ch_ids)}): {ch_ids}")

        if not any(node.alive for node in nodes):
            print("Todos os nós morreram. Fim da simulação.")
            break

        alive_nodes = [node for node in nodes if node.alive]
        # Fase de Steady-State
        # Todos os nós sensoreiam (membros e CHs)
        for node in alive_nodes:
            node.rounds_alive += 1
            temp = random.uniform(20, 70)
            node.sense_environment(temp)

        # Sensores não CH enviam os dados sensoriados para o CH ou diretamente à ERB, dependendo da distância 
        for node in nodes:
            if node.alive and not node.is_cluster_head:
                if node.is_direct:
                    if node.send_data_direct_to_base():
                        nodes_sent_direct += 1
                elif node.cluster_head:
                    if node.send_data_to_cluster_head():
                        nodes_sent_to_ch += 1

        print(f"Dados enviados para CHs: {nodes_sent_to_ch}, Direto para BS: {nodes_sent_direct}")

        # CHs enviam dados agregados dos sensores membros do cluster à ERB
        chs_sent_to_bs = 0
        for ch in cluster_heads:
            if ch.alive and ch.data:
                if ch.send_aggregated_data_to_base():
                    chs_sent_to_bs += 1

        print(f"CHs que enviaram dados para BS: {chs_sent_to_bs}")

        # representa o sensor entrar em modo sleep
        for node in nodes:
            if node.alive:
                node.sleep_mode()

        # Estatísticas da rodada
        alive_nodes = sum(1 for node in nodes if node.alive)
        total_energy = sum(node.energy for node in nodes if node.alive)
        avg_energy = total_energy / len(nodes)
        
        alive_history[round_num] = alive_nodes
        energy_history[round_num] = avg_energy

        print(f"Nós vivos: {alive_nodes}/{num_nodes}")
        print(f"Energia média dos nós vivos: {avg_energy:.6f} J")

        if alive_nodes == 0:
            print("\nTodos os nós morreram. Fim da simulação.")
            break
            
    print(f"\n--- Fim da Simulação (Após {len(alive_history)} rodadas) ---")
    show_final_results(nodes, base_station)

    rounds_vividas = [node.rounds_alive for node in nodes]
    media_vida_nos = sum(rounds_vividas) / len(rounds_vividas)
    print(f"Média de rodadas vividas por nó: {media_vida_nos:.2f}")

    return nodes, base_station, alive_history, energy_history, media_vida_nos, first_node_death_round

def show_final_results(nodes, base_station):
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