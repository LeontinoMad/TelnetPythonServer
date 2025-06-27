import socket
import time
import datetime
import random
import requests

HOST = '0.0.0.0'
PORT = 50000
ENCODING = 'utf-8'
CLEAR_VISUALLY = "\n" * 3

server_start_time = datetime.datetime.now()

PASSWORD = "senhaforte"
MAX_LOGIN_ATTEMPTS = 3

OPENWEATHER_API_KEY = 'API_KEI' 
CITY_NAME = "Pelotas"
COUNTRY_CODE = "BR"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME},{COUNTRY_CODE}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"

def send_message(client_socket, message):
    try:
        client_socket.sendall(message.encode(ENCODING))
    except socket.error as e:
        print(f"[-] Erro ao enviar dados para o cliente: {e}")
        return False
    return True

def receive_data(client_socket, timeout=30):
    client_socket.settimeout(timeout)
    try:
        data = client_socket.recv(1024)
        if not data:
            return None

        decoded_data = data.decode(ENCODING)
        cleaned_data = decoded_data.strip('\r\n').strip()

        return cleaned_data
    except socket.timeout:
        print("[-] Cliente inativo (timeout de leitura).")
        return None
    except socket.error as e:
        print(f"[-] Erro ao receber dados do cliente: {e}")
        return None

def cmd_hello(client_socket):
    send_message(client_socket, "Olá mundo! Bem-vindo ao meu servidor de automação!\n")

def cmd_time(client_socket):
    send_message(client_socket, f"Hora atual do servidor: {time.strftime('%H:%M:%S')}\n")

def cmd_uptime(client_socket):
    current_time = datetime.datetime.now()
    delta = current_time - server_start_time

    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    uptime_str = ""
    if days > 0:
        uptime_str += f"{days} dias, "
    uptime_str += f"{hours:02}h:{minutes:02}m:{seconds:02}s"

    send_message(client_socket, f"O servidor está ativo há: {uptime_str}\n")

def cmd_temperatura_local(client_socket):
    try:
        response = requests.get(WEATHER_URL, timeout=5)
        response.raise_for_status()
        
        weather_data = response.json()
        
        if weather_data and 'main' in weather_data and 'temp' in weather_data['main']:
            temperatura = weather_data['main']['temp']
            descricao = weather_data['weather'][0]['description'] if 'weather' in weather_data and weather_data['weather'] else 'N/A'
            cidade = weather_data['name'] if 'name' in weather_data else CITY_NAME

            send_message(client_socket, f"Temperatura em {cidade}: {temperatura}°C ({descricao.capitalize()})\n")
        else:
            send_message(client_socket, "Erro: Não foi possível obter dados de temperatura válidos da API.\n")
            print(f"[-] Erro na API: Dados incompletos. Resposta da API: {weather_data}")
            
    except requests.exceptions.RequestException as e:
        send_message(client_socket, f"Erro ao conectar com o serviço de temperatura: {e}\n")
        print(f"[-] Erro na requisição HTTP da API: {e}")
    except Exception as e:
        send_message(client_socket, f"Ocorreu um erro inesperado ao buscar a temperatura: {e}\n")
        print(f"[-] Erro geral na função de temperatura: {e}")

def cmd_exit(client_socket):
    send_message(client_socket, "Até breve! Encerrando a conexão.\n")
    return True

def cmd_status_servico(client_socket):
    send_message(client_socket, "Qual serviço você quer verificar (ex: http, ftp, db)? \n")
    service_name = receive_data(client_socket)

    if service_name is None:
        send_message(client_socket, "Nenhum serviço especificado ou erro na comunicação.\n")
        return

    service_name = service_name.lower()

    if service_name == "http":
        status = "Rodando" if random.choice([True, False]) else "Parado"
        send_message(client_socket, f"Serviço HTTP: {status}\n")
    elif service_name == "ftp":
        status = "Rodando" if random.choice([True, False]) else "Parado"
        send_message(client_socket, f"Serviço FTP: {status}\n")
    elif service_name == "db":
        status = "Rodando" if random.choice([True, False]) else "Parado"
        send_message(client_socket, f"Serviço Banco de Dados: {status}\n")
    else:
        send_message(client_socket, f"Serviço '{service_name}' não reconhecido ou sem monitoramento.\n")

COMMANDS = {
    '1': cmd_hello,
    '2': cmd_time,
    '3': cmd_uptime,
    '4': cmd_temperatura_local,
    '5': cmd_exit,
    '6': cmd_status_servico
}

MAIN_MENU = """========= MENU DE OPERAÇÕES =======
  1. Dizer olá
  2. Ver hora atual
  3. Ver tempo de atividade do servidor
  4. Ver temperatura local
  5. Encerrar comunicação
  6. Verificar status de serviço

Digite sua opção: \n"""

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"[*] Escutando em {HOST}:{PORT}...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"[*] Conexão aceita de: {client_address[0]}:{client_address[1]}")

            authenticated = False
            for attempt in range(MAX_LOGIN_ATTEMPTS):
                if not send_message(client_socket, "Por favor, digite a senha: \n"):
                    break

                password_input = receive_data(client_socket)

                if password_input is None:
                    break

                if password_input == PASSWORD:
                    authenticated = True
                    send_message(client_socket, CLEAR_VISUALLY)
                    send_message(client_socket, "Senha correta! Bem-vindo ao servidor.\n")
                    print(f"[*] Cliente {client_address} autenticado com sucesso.")
                    time.sleep(1)
                    break
                else:
                    send_message(client_socket, "Senha incorreta. Tente novamente.\n")
                    print(f"[-] Cliente {client_address} - Tentativa de senha incorreta ({attempt + 1}/{MAX_LOGIN_ATTEMPTS}).")
                    time.sleep(1)

            if not authenticated:
                send_message(client_socket, "Número máximo de tentativas excedido. Conexão encerrada.\n")
                print(f"[-] Cliente {client_address} não autenticado. Conexão encerrada.")
                client_socket.close()
                continue

            while True:
                if not send_message(client_socket, CLEAR_VISUALLY): break
                if not send_message(client_socket, MAIN_MENU): break

                raw_input = receive_data(client_socket)

                if raw_input is None:
                    print(f"[-] Cliente {client_address} inativo ou desconectado.")
                    break

                print(f"[DEBUG] Cliente {client_address} digitou: '{raw_input}'")

                option_chosen = raw_input

                if option_chosen in COMMANDS:
                    if option_chosen == '5':
                        send_message(client_socket, "Até breve! Encerrando a conexão.\n")
                        print(f"[*] Cliente {client_address} solicitou encerramento da conexão.")
                        break
                    else:
                        COMMANDS[option_chosen](client_socket)
                else:
                    send_message(client_socket, "Opção inválida. Digite '4' para ver as opções.\n")

                time.sleep(5)

            client_socket.close()
            print(f"[*] Conexão com {client_address} encerrada.")

    except Exception as e:
        print(f"[-] Ocorreu um erro geral no servidor: {e}")
    finally:
        print("[*] Encerrando o socket do servidor.")
        if 'server_socket' in locals() and server_socket:
            server_socket.close()

if __name__ == "__main__":
    run_server()