import socket
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
from configs import clear_terminal

# Função para ler a temperatura do servidor
def read_temperature():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 65433))
            s.sendall(b"read_temp")
            data = s.recv(1024)
            try:
                temp = float(data.decode('utf-8'))
                return temp
            except ValueError:
                messagebox.showerror("Erro de Conversão", "Não foi possível converter a temperatura para float.")
                return None
    except Exception as e:
        messagebox.showerror("Erro", f"Erro de conexão: {e}")
        return None

# Função para ler o fluxo de calor do servidor
def read_fluxo_calor():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 65433))
            s.sendall(b"read_flux")
            data = s.recv(1024).decode('utf-8').strip()
            try:
                fluxo_calor = float(data)
                return fluxo_calor
            except ValueError:
                messagebox.showerror("Erro de Conversão", "Não foi possível converter o fluxo de calor para float.")
                return None
    except Exception as e:
        messagebox.showerror("Erro", f"Erro de conexão: {e}")
        return None

# Função para ler os valores de Kp e Ki do servidor
def read_pi_values():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 65433))
            s.sendall(b"read_pi")
            data = s.recv(1024).decode('utf-8')
            try:
                kp, ki = map(float, data.split())
                return kp, ki
            except ValueError:
                messagebox.showerror("Erro de Conversão", "Não foi possível converter Kp ou Ki para float.")
                return None, None
    except Exception as e:
        messagebox.showerror("Erro", f"Erro de conexão: {e}")
        return None, None

# Função para ler a temperatura de referência inicial do servidor
def read_initial_temp_ref():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 65433))
            s.sendall(b"read_temp_ref")
            data = s.recv(1024)
            try:
                temp_ref = float(data.decode('utf-8'))
                return temp_ref
            except ValueError:
                messagebox.showerror("Erro de Conversão", "Não foi possível converter a temperatura de referência para float.")
                return None
    except Exception as e:
        messagebox.showerror("Erro", f"Erro de conexão: {e}")
        return None

def print_styled(temperatura, fluxo_calor, kp, ki):
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    
    # Mensagem formatada
    message = (f"{BOLD}{YELLOW}Cliente Sinótico:{RESET}\n"
               f"{BOLD}{CYAN}Temperatura:{RESET} {GREEN}{temperatura:.2f} °C{RESET}\n"
               f"{BOLD}{CYAN}Fluxo de Calor:{RESET} {GREEN}{fluxo_calor:.2f} W{RESET}\n"
               f"{BOLD}{CYAN}Kp:{RESET} {YELLOW}{kp:.2f}{RESET}\n"
               f"{BOLD}{CYAN}Ki:{RESET} {YELLOW}{ki:.2f}{RESET}")
    
    print(message)

def log_to_file(message):
    """Log a message to 'historico.txt'."""
    with open("historico.txt", "a") as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Função para atualizar a temperatura, o fluxo de calor, e os valores de Kp e Ki
def update_data():
    while True:
        temp = read_temperature()
        fluxo_calor = read_fluxo_calor()
        kp, ki = read_pi_values()

        if temp is not None:
            temperatures.append(temp)
            times.append(time.time() - start_time)

            # Limitar o número de pontos para manter a performance
            if len(temperatures) > max_points:
                temperatures.pop(0)
                times.pop(0)

            label_temp.config(text=f"Temperatura atual: {temp:.2f} °C")
            label_fluxo.config(text=f"Fluxo de Calor: {fluxo_calor:.2f} W")
            ax.clear()
            ax.plot(times, temperatures, label='Temperatura (°C)')
            ax.set_xlabel('Tempo (s)')
            ax.set_ylabel('Temperatura (°C)')
            ax.legend()
            ax.grid(True)
            canvas.draw()
        clear_terminal()
        print_styled(temp, fluxo_calor, kp, ki)

        time.sleep(1)

# Função para enviar valores de Kp e Ki ao servidor
def send_pi_values():
    kp = entry_kp.get()
    ki = entry_ki.get()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 65433))
            pi_data = f"set_pi {kp} {ki}"
            s.sendall(pi_data.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            log_to_file(f"Comando enviado: {pi_data} - Resposta do servidor: {response}")
            messagebox.showinfo("Resposta do Servidor", response)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro de conexão: {e}")

# Função para enviar a nova temperatura de referência ao servidor
def send_temp_reference():
    temp_ref = entry_temp_ref.get()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 65433))
            temp_data = f"set_temp_ref {temp_ref}"
            s.sendall(temp_data.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            log_to_file(f"Comando enviado: {temp_data} - Resposta do servidor: {response}")
            messagebox.showinfo("Resposta do Servidor", response)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro de conexão: {e}")

# Função para ler os valores iniciais de Kp e Ki do servidor
def read_initial_pi_values():
    kp, ki = read_pi_values()
    if kp is not None and ki is not None:
        entry_kp.insert(0, kp)
        entry_ki.insert(0, ki)

# Função para ler o valor inicial da temperatura de referência e configurá-lo
def read_initial_temp_ref_value():
    temp_ref = read_initial_temp_ref()
    if temp_ref is not None:
        entry_temp_ref.insert(0, temp_ref)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Cliente de Temperatura")

label_temp = tk.Label(root, text="Temperatura atual: ", font=("Arial", 16))
label_temp.pack(pady=20)

label_fluxo = tk.Label(root, text="Fluxo de Calor: ", font=("Arial", 14))
label_fluxo.pack(pady=20)

# Entrada para Kp e Ki
frame_pi = tk.Frame(root)
frame_pi.pack(pady=10)

label_kp = tk.Label(frame_pi, text="Kp:")
label_kp.grid(row=0, column=0, padx=5)
entry_kp = tk.Entry(frame_pi)
entry_kp.grid(row=0, column=1, padx=5)

label_ki = tk.Label(frame_pi, text="Ki:")
label_ki.grid(row=1, column=0, padx=5)
entry_ki = tk.Entry(frame_pi)
entry_ki.grid(row=1, column=1, padx=5)

button_send_pi = tk.Button(frame_pi, text="Enviar PI", command=send_pi_values)
button_send_pi.grid(row=2, columnspan=2, pady=10)

# Entrada para a temperatura de referência
frame_temp_ref = tk.Frame(root)
frame_temp_ref.pack(pady=10)

label_temp_ref = tk.Label(frame_temp_ref, text="Temperatura de Referência:")
label_temp_ref.grid(row=0, column=0, padx=5)
entry_temp_ref = tk.Entry(frame_temp_ref)
entry_temp_ref.grid(row=0, column=1, padx=5)

button_send_temp_ref = tk.Button(frame_temp_ref, text="Enviar Temperatura", command=send_temp_reference)
button_send_temp_ref.grid(row=1, columnspan=2, pady=10)

# Configuração do gráfico
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Variáveis para armazenar os dados
temperatures = []
times = []
start_time = time.time()
max_points = 200  # Número máximo de pontos a serem mostrados no gráfico

read_initial_pi_values()
read_initial_temp_ref_value()

# Inicializa a atualização da temperatura e dos dados no terminal
update_thread = threading.Thread(target=update_data, daemon=True)
update_thread.start()

# Inicializa a interface gráfica
root.mainloop()
