import platform
import os

# Definição das configurações do servidor OPC UA
OPC_SERVER_URL = "opc.tcp://localhost:53530/OPCUA/SimulationServer"
NODE_FLUXO_CALOR = "ns=3;i=1008"  # Nó do fluxo de calor no servidor OPC UA
NODE_TEMPERATURA = "ns=3;i=1009"  # Nó da temperatura no servidor OPC UA
NODE_TEMP_REF = "ns=3;i=1012" # Nó da temperatura de referência no servidor OPC UA
NODE_KP = "ns=3;i=1010"  # Nó da constante Kp
NODE_KI = "ns=3;i=1011"  # Nó da constante Ki

def clear_terminal():
    system_name = platform.system()
    if system_name == 'Windows':
        os.system('cls')
    else:
        os.system('clear')