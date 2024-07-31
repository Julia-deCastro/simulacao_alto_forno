from opcua import Client
import time
from configs import OPC_SERVER_URL, NODE_TEMPERATURA, NODE_FLUXO_CALOR, clear_terminal

class MES:
    def __init__(self):
        self.client = Client(OPC_SERVER_URL)
        try:
            self.client.connect()
            self.node_temp = self.client.get_node(NODE_TEMPERATURA)
            self.node_fluxo_calor = self.client.get_node(NODE_FLUXO_CALOR)
        except Exception as e:
            print(f"Erro ao conectar ao servidor OPC UA ou obter o nó: {e}")
            self.client.disconnect()
            raise

    def run(self):
        try:
            with open("mes.txt", "a") as f:
                while True:
                    try:
                        temp = self.node_temp.get_value()
                        fluxo = self.node_fluxo_calor.get_value()
                        f.write(f"Temperatura: {temp}, Fluxo: {fluxo},  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.flush()  # Garantir que os dados sejam gravados imediatamente
                        clear_terminal()
                        print("------- Sistema MES -------\n")
                        print(f"Dados atualizados em: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    except Exception as e:
                        print(f"Erro ao ler o valor do nó: {e}")
                    time.sleep(1)
        finally:
            self.client.disconnect()  # Garante que a conexão seja desconectada

mes = MES()
mes.run()

