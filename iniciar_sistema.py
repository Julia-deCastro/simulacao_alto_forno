import subprocess
import platform
import time

# Comandos para executar os scripts
commands = [
    "python alto_forno.py",
    "python clp.py",
    "python cliente_tcp.py",
    "python mes.py"
]

def open_terminal_and_run(command):
    if platform.system() == "Windows":
        # Comando para abrir um novo terminal e executar o script
        subprocess.Popen(f"start cmd /k {command}", shell=True)
    elif platform.system() == "Linux":
        # Comando para abrir um novo terminal e executar o script
        # Substitua 'gnome-terminal' por 'xterm' ou outro terminal se necessário
        subprocess.Popen(f"gnome-terminal -- {command}", shell=True)
    else:
        print(f"Sistema operacional não suportado: {platform.system()}")

# Abrir terminais e executar os comandos
for cmd in commands:
    open_terminal_and_run(cmd)
    time.sleep(1)  # Aguarda para garantir que o terminal abra antes de tentar abrir o próximo
