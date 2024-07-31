import numpy as np
import matplotlib.pyplot as plt
from threading import Thread, Event
import time
from opcua import Client, ua
from configs import OPC_SERVER_URL, NODE_FLUXO_CALOR, NODE_TEMPERATURA, NODE_KP, NODE_KI, NODE_TEMP_REF, clear_terminal

# Parâmetros do forno
C_m = 1000  # Capacidade térmica (J/K)
T_amb = 25  # Temperatura ambiente (°C)
R = 50      # Resistência térmica (K/W)

def print_styled(temperatura, fluxo_calor, t_ref):
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    
    message = (f"{BOLD}{YELLOW}Parâmetros Alto-forno{RESET}\n"
               f"{BOLD}{CYAN}Temperatura:{RESET} {GREEN}{temperatura:.2f} °C{RESET},\n"
               f"{BOLD}{CYAN}Fluxo de Calor:{RESET} {GREEN}{fluxo_calor:.2f} W{RESET},\n"
               f"{BOLD}{CYAN}Temperatura de referência:{RESET} {YELLOW}{t_ref:.2f}{RESET}")
    
    print(message)

# Função de derivada da temperatura
def derivada_temperatura(T, Q):
    return (Q / C_m) - ((T - T_amb) / R)

# Thread de simulação do alto-forno
class AltoForno(Thread):
    def __init__(self, stop_event, temp_list, time_list):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.temp_list = temp_list
        self.time_list = time_list

    def run(self):
        client = Client(OPC_SERVER_URL)
        client.connect()
        node_temp = client.get_node(NODE_TEMPERATURA)
        node_flux = client.get_node(NODE_FLUXO_CALOR)
        node_temp_ref = client.get_node(NODE_TEMP_REF)

        # Inicializa a temperatura no servidor como a temperatura ambiente
        node_temp.set_value(ua.Variant(T_amb, ua.VariantType.Double))

        tempo_total = 200  # Tempo total de simulação (s)
        dt = 1.0           # Passo de tempo da simulação (s)
        
        tempo = 0
        temperatura = T_amb

        while not self.stop_event.is_set() and tempo <= tempo_total:
            # Obtém o valor de fluxo de calor atual e temperatura de referência do nó
            fluxo_calor = node_flux.get_value()
            temp_ref = node_temp_ref.get_value()

            clear_terminal()
            print_styled(temperatura, fluxo_calor, temp_ref)
            
            # Calcula a nova temperatura usando o método de Runge-Kutta de quarta ordem (RK4)
            k1 = dt * derivada_temperatura(temperatura, fluxo_calor)
            k2 = dt * derivada_temperatura(temperatura + 0.5 * k1, fluxo_calor)
            k3 = dt * derivada_temperatura(temperatura + 0.5 * k2, fluxo_calor)
            k4 = dt * derivada_temperatura(temperatura + k3, fluxo_calor)
            
            temperatura += (k1 + 2*k2 + 2*k3 + k4) / 6
            
            # Atualiza a temperatura no servidor
            node_temp.set_value(ua.Variant(temperatura, ua.VariantType.Double))
            
            # Armazena o tempo e a temperatura para plotagem
            self.time_list.append(tempo)
            self.temp_list.append(temperatura)

            tempo += dt
            time.sleep(dt)

        client.disconnect()

# Thread de controle PI do alto-forno
class ControlePID(Thread):
    def __init__(self, stop_event):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.prev_error = 0
        self.integral = 0

    def run(self):
        client = Client(OPC_SERVER_URL)
        client.connect()
        node_temp = client.get_node(NODE_TEMPERATURA)
        node_flux = client.get_node(NODE_FLUXO_CALOR)
        node_kp = client.get_node(NODE_KP)
        node_ki = client.get_node(NODE_KI)
        node_temp_ref = client.get_node(NODE_TEMP_REF)

        # Inicializa os valores de Kp e Ki no servidor
        node_kp.set_value(ua.Variant(154, ua.VariantType.Double))
        node_ki.set_value(ua.Variant(2.883, ua.VariantType.Double))

        dt = 0.5  # Passo de tempo do controle (s)

        while not self.stop_event.is_set():
            temp_atual = node_temp.get_value()
            temp_ref = node_temp_ref.get_value()
            erro = temp_ref - temp_atual
            self.integral += erro * dt
            
            # Lê os valores atuais de Kp e Ki do servidor
            Kp = node_kp.get_value()
            Ki = node_ki.get_value()
            
            # Calcula a saída do PID
            Q = (Kp * erro) + (Ki * self.integral)

            node_flux.set_value(ua.Variant(Q, ua.VariantType.Double))
            
            # Atualiza o erro anterior
            self.prev_error = erro

            time.sleep(dt)
        client.disconnect()

# Inicialização das threads
stop_event = Event()
temp_list = []
time_list = []

# Inicialização dos valores no servidor
client = Client(OPC_SERVER_URL)
client.connect()
node_temp = client.get_node(NODE_TEMPERATURA)
node_flux = client.get_node(NODE_FLUXO_CALOR)
node_temp_ref = client.get_node(NODE_TEMP_REF)

# Setando valores iniciais
node_temp.set_value(ua.Variant(T_amb, ua.VariantType.Double))
node_flux.set_value(ua.Variant(1000, ua.VariantType.Double))
node_temp_ref.set_value(ua.Variant(1500, ua.VariantType.Double))  # Inicializa T_ref como 1500°C

client.disconnect()

auto_forno = AltoForno(stop_event, temp_list, time_list)
controle_pid = ControlePID(stop_event)

auto_forno.start()
controle_pid.start()

try:
    # Execução por um período determinado
    time.sleep(200)
except KeyboardInterrupt:
    print("Interrupção manual recebida. Finalizando...")
finally:
    # Parada das threads
    stop_event.set()
    
    # Aguardar a finalização das threads com um tempo limite
    auto_forno.join(timeout=10)
    controle_pid.join(timeout=10)

    # Plotar a temperatura
    plt.figure(figsize=(10, 6))
    plt.plot(time_list, temp_list, label='Temperatura no alto-forno')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Temperatura (°C)')
    plt.title('Simulação da Dinâmica de um Alto-Forno com Controle PID')
    plt.legend()
    plt.grid(True)
    plt.show()

    print("Simulação encerrada.")
