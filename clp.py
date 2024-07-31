import socket
from threading import Thread
from opcua import Client, ua
import time
from configs import OPC_SERVER_URL, NODE_FLUXO_CALOR, NODE_TEMPERATURA, NODE_KP, NODE_KI, NODE_TEMP_REF, clear_terminal

class OPCClient(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.client = Client(OPC_SERVER_URL)
        self.client.connect()
        self.node_temp = self.client.get_node(NODE_TEMPERATURA)
        self.node_flux = self.client.get_node(NODE_FLUXO_CALOR)
        self.node_kp = self.client.get_node(NODE_KP)
        self.node_ki = self.client.get_node(NODE_KI)
        self.node_temp_ref = self.client.get_node(NODE_TEMP_REF) 

    def run(self):
        while True:
            time.sleep(1)

class TCPServer(Thread):
    def __init__(self, opc_client):
        Thread.__init__(self)
        self.opc_client = opc_client
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 65433))
        self.server_socket.listen(5)

    def run(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            clear_terminal()
            print("CLP\nLista de Conexões:\n")
            print(f"Conexão estabelecida com {addr}")
            try:
                data = client_socket.recv(1024)
                if data:
                    command = data.decode('utf-8')
                    if command == "read_temp":
                        try:
                            temp = self.opc_client.node_temp.get_value()
                            client_socket.sendall(str(temp).encode('utf-8'))
                        except Exception as e:
                            client_socket.sendall(f"Erro ao ler temperatura: {e}".encode('utf-8'))
                    elif command == "read_temp_ref":
                        try:
                            temp_ref = self.opc_client.node_temp_ref.get_value()
                            client_socket.sendall(str(temp_ref).encode('utf-8'))
                        except Exception as e:
                            client_socket.sendall(f"Erro ao ler temperatura de referência: {e}".encode('utf-8'))
                    elif command == "read_flux":
                        try:
                            flux = self.opc_client.node_flux.get_value()
                            client_socket.sendall(str(flux).encode('utf-8'))
                        except Exception as e:
                            client_socket.sendall(f"Erro ao ler fluxo de calor: {e}".encode('utf-8'))
                    elif command == "read_pi":
                        try:
                            kp = self.opc_client.node_kp.get_value()
                            ki = self.opc_client.node_ki.get_value()
                            response = f"{kp} {ki}"
                            client_socket.sendall(response.encode('utf-8'))
                        except Exception as e:
                            client_socket.sendall(f"Erro ao ler valores de PI: {e}".encode('utf-8'))
                    elif command.startswith("set_pi"):
                        try:
                            _, kp, ki = command.split()
                            self.opc_client.node_kp.set_value(float(kp))
                            self.opc_client.node_ki.set_value(float(ki))
                            client_socket.sendall(b"Kp e Ki atualizados")
                        except (IndexError, ValueError) as e:
                            client_socket.sendall(f"Erro ao definir valores de PI: {e}".encode('utf-8'))
                    elif command.startswith("set_temp_ref"):
                        try:
                            _, temp_ref = command.split()
                            self.opc_client.node_temp_ref.set_value(float(temp_ref))
                            client_socket.sendall(b"Temperatura de referencia atualizada")
                        except (IndexError, ValueError) as e:
                            client_socket.sendall(f"Erro ao definir temperatura de referência: {e}".encode('utf-8'))
            except Exception as e:
                client_socket.sendall(f"Erro de conexão: {e}".encode('utf-8'))
            finally:
                client_socket.close()

opc_client = OPCClient()
tcp_server = TCPServer(opc_client)

opc_client.start()
tcp_server.start()
