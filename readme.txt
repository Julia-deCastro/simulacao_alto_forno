--> Sistema de Monitoramento e Controle
Este projeto é um sistema de monitoramento e controle que utiliza um servidor OPC UA para a comunicação.
Abaixo, você encontrará instruções sobre as bibliotecas necessárias, a configuração do servidor OPC UA e 
como iniciar o sistema.

--> Bibliotecas Necessárias
Este projeto utiliza algumas bibliotecas que não são nativas do Python e precisam ser instaladas separadamente. 
As bibliotecas necessárias são:

opcua: Biblioteca para comunicação OPC UA.
numpy: Biblioteca para operações matemáticas e manipulação de arrays.
matplotlib: Biblioteca para criação de gráficos e visualizações.
tkinter: Biblioteca para interfaces gráficas (já incluída na instalação padrão do Python).
threading: Biblioteca para manipulação de threads (já incluída na instalação padrão do Python).

Execute o seguinte comando para instalar as dependências caso não as tenha instaladas:

pip install opcua numpy matplotlib


--> Configuração do Servidor OPC UA
Este sistema foi projetado para funcionar com o servidor OPC UA Prosys. A URL de conexão pode ser configurada 
no arquivo configs.py. O valor padrão é:

OPC_SERVER_URL = "opc.tcp://localhost:53530/OPCUA/SimulationServer"

Além disso, o servidor OPC UA deve ter os seguintes nós configurados:

Fluxo de Calor: "ns=3;i=1008"
Temperatura: "ns=3;i=1009"
Constante Kp: "ns=3;i=1010"
Constante Ki: "ns=3;i=1011"
Temperatura de Referência: "ns=3;i=1012"

Certifique-se de que esses nós estejam configurados corretamente no servidor OPC UA para garantir que o 
sistema funcione corretamente.

--> Iniciando o Sistema
Para iniciar o sistema, estando no diretório do projeto, execute o script iniciar_sistema.py com o comando:

python iniciar_sistema.py. 

Este script abrirá os terminais e executará os programas necessários para o funcionamento do sistema.

Se o script iniciar_sistema.py não funcionar corretamente, você pode rodar cada arquivo individualmente:

python alto_forno.py
python clp.py
python cliente_tcp.py
python mes.py
