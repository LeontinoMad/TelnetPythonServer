# Documentação do Protótipo de Servidor TCP/Telnet

## 1. Introdução

Este documento detalha o desenvolvimento de um protótipo de servidor TCP/Telnet para a Tech UniSenac. No contexto de nossa missão de expandir as capacidades de comunicação em redes, este projeto visa transformar a forma como dispositivos se comunicam na era digital. O servidor oferece uma interface de linha de comando para interação, simulando funcionalidades essenciais de automação de rede.

---

## 2. Visão Geral do Sistema

O sistema adota uma arquitetura cliente-servidor. O servidor, desenvolvido em Python, atua como um ponto de comunicação TCP/Telnet, enquanto clientes como o Windows Subsystem for Linux (WSL) com Ubuntu são utilizados para interagir via linha de comando.

### 2.1. Tecnologias Utilizadas

- **Python 3:** Linguagem de programação principal.
- **Módulo `socket`:** Para a comunicação de rede (TCP).
- **Módulos `time`, `datetime`, `random`:** Utilizados para implementar funcionalidades específicas do servidor.
- **Biblioteca `requests`:** Essencial para realizar requisições HTTP e integrar com APIs externas (como a de previsão do tempo).
- **Cliente Telnet:** Ferramenta padrão para teste e interação com a interface de linha de comando do servidor.
- **Windows Subsystem for Linux (WSL) / Ubuntu:** Recomendado como ambiente cliente para testes, superando as limitações do cliente Telnet nativo do Windows.

### 2.2. Funcionalidades Implementadas

O servidor oferece um menu de opções interativo:

- **1. Dizer olá:** Exibe uma mensagem de boas-vindas.
- **2. Ver hora atual:** Informa a hora do sistema do servidor.
- **3. Ver tempo de atividade do servidor:** Mostra o tempo total que o servidor está online (`uptime`).
- **4. Ver temperatura local:** Busca e exibe a temperatura atual de Pelotas, Brasil, através de uma API externa.
- **5. Encerrar comunicação:** Permite ao cliente desconectar-se do servidor.
- **6. Verificar status de serviço:** Simula o status de serviços de rede (ex: `http`, `ftp`, `db`).

---

## 3. Detalhes de Implementação e Desafios Superados

Nosso protótipo de servidor Telnet foi desenvolvido com foco em robustez, segurança básica e capacidade de expansão. Durante a implementação, enfrentamos e superamos desafios técnicos importantes.

### 3.1. Configuração de Rede e Portas

O servidor utiliza TCP via módulo `socket` do Python. Ele opera no IP `0.0.0.0` e na porta `50000`. A escolha de `0.0.0.0` permite aceitar conexões de qualquer interface de rede, e a porta `50000` (faixa dinâmica/privada) evita a necessidade de privilégios de administrador.

- **Desafio Superado: `WinError 10048` (Endereço Já em Uso):** Este erro ocorria ao tentar reiniciar o servidor rapidamente. A solução foi aplicar a opção `socket.SO_REUSEADDR` (`server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)`), que permite a reutilização imediata da porta, mesmo em estado `TIME_WAIT`.

### 3.2. Codificação de Caracteres (`ENCODING`)

Garantir a exibição correta de caracteres entre sistemas operacionais foi um ponto chave.

- **Problema de Caracteres Especiais:** Caracteres acentuados apareciam distorcidos em clientes Linux (Ubuntu/WSL) devido à diferença entre a codificação `cp850` (Windows) e `UTF-8` (Linux).
- **Solução:** Padronizamos a codificação para `ENCODING = 'utf-8'`. Isso assegura a correta exibição de todos os caracteres em ambos os ambientes.

### 3.3. Controle de Acesso e Autenticação

Implementamos uma camada de segurança básica para controlar o acesso ao servidor.

- **Autenticação por Senha:** O servidor agora exige uma senha (`"senhaforte"`) para acesso. O cliente tem 3 tentativas (`MAX_LOGIN_ATTEMPTS`) para inseri-la corretamente.
- **Encerramento por Falha:** Após tentativas esgotadas, a conexão é automaticamente encerrada, bloqueando acessos não autorizados.

### 3.4. Gerenciamento de Entrada e Interatividade

A capacidade de o servidor receber e processar comandos do cliente de forma confiável foi crucial para a interatividade.

- **Função `receive_data` Robusta:** Desenvolvemos uma função `receive_data` dedicada para lidar com a leitura do socket. Esta função é responsável por:
  - **Limpeza de Entrada:** Remove explicitamente caracteres de quebra de linha (`\r`, `\n`) e espaços em branco extras do input do cliente, garantindo que apenas o comando puro seja processado. Isso resolveu problemas de comparação de strings (como na autenticação da senha) causados pelas variações de quebra de linha de diferentes clientes Telnet.
  - **Controle de Timeout:** Incorpora um `timeout` de 30 segundos (`timeout=30`) na leitura. Isso impede que o servidor fique bloqueado indefinidamente esperando por uma entrada do cliente, encerrando a conexão se houver inatividade. Esse ajuste foi vital para melhorar a experiência do usuário após a autenticação, dando tempo suficiente para a leitura do menu e a digitação de comandos.

### 3.5. Lógica de Comandos e Funcionalidades

O servidor oferece um menu interativo de opções, mapeando entradas numéricas a funções específicas.

- **Mapeamento Flexível:** O dicionário `COMMANDS` centraliza a associação entre as opções numéricas (`'1'`, `'2'`, etc.) e as funções Python que as implementam. Isso torna a adição ou modificação de comandos simples e organizada.
- **Comandos Atuais:**
  - **Olá (`1`):** Uma saudação básica.
  - **Hora Atual (`2`):** Exibe a hora do sistema do servidor.
  - **Tempo de Atividade (`3`):** Calcula e mostra por quanto tempo o servidor está online (`uptime`), formatando o tempo em dias, horas, minutos e segundos.
  - **Ver temperatura local (`4`):** Realiza uma requisição HTTP a uma API externa (OpenWeatherMap) para obter a temperatura atual de Pelotas, Brasil, e a exibe ao cliente. Inclui tratamento de erros para problemas de conexão ou dados inválidos da API.
  - **Sair (`5`):** Permite que o cliente encerre sua sessão de forma controlada.
  - **Verificar Status de Serviço (`6`, `status_servico`):** Esta funcionalidade simula o monitoramento de serviços de rede. Ao selecionar esta opção, o servidor solicita o nome do serviço (ex: `http`, `ftp`, `db`). Ele então retorna um status "Rodando" ou "Parado" simulado aleatoriamente para os serviços reconhecidos, demonstrando uma capacidade rudimentar de gerenciamento e automação.

---

## 4. Como Executar e Testar

Para utilizar o servidor Telnet, siga os passos abaixo:

### 4.1. Pré-requisitos

Certifique-se de ter **Python 3** instalado em seu sistema operacional Windows. Para o cliente Telnet, recomenda-se o uso do **Windows Subsystem for Linux (WSL) com Ubuntu** , devido às limitações e à desativação padrão do cliente Telnet nativo do Windows.

### 4.2. Iniciando o Servidor (no Windows)

1.  **Navegue até o diretório** onde o arquivo `servidor_telnet.py` está salvo utilizando o Prompt de Comando ou PowerShell.
2.  **Importante: Garanta que apenas uma instância do servidor esteja rodando.** Antes de iniciar, feche quaisquer janelas de terminal abertas que possam ter iniciado o script anteriormente. Se encontrar problemas de "endereço já em uso" (`WinError 10048`), utilize o comando `netstat -ano | findstr :50000` para identificar PIDs (`Process IDs`) que estão usando a porta e finalize-os com `taskkill /PID <PID> /F`. Repita o `netstat` até que a porta `50000` esteja completamente livre.
3.  Execute o servidor com o comando:
    ```bash
    python servidor_telnet.py
    ```
    Você deverá ver a mensagem `[*] Escutando em 0.0.0.0:50000...` indicando que o servidor está pronto para aceitar conexões.

### 4.3. Conectando e Interagindo com o Cliente (no Ubuntu/WSL)

1.  Abra uma nova janela de terminal no seu **Ubuntu (WSL)**.
2.  Para conectar ao servidor, digite o comando:
    ```bash
    telnet localhost 50000
    ```
    (A porta pode ser ajustada se você a modificou no código).
3.  Após a conexão, o servidor solicitará a senha: **"Por favor, digite a senha: "**
    - Digite `senhaforte` e pressione **Enter**. Digite rapidamente para evitar o timeout inicial.
4.  Se a autenticação for bem-sucedida, o servidor apresentará o `MAIN_MENU`. Você terá 30 segundos para digitar sua opção.
5.  Interaja com o servidor digitando os números das opções (1 a 6) e pressionando **Enter**.
6.  Os logs de depuração (`[DEBUG]`) mostrando a entrada do cliente serão exibidos no terminal do servidor (no Windows), auxiliando no monitoramento da interação.

---

## 5. Conclusão

# Este protótipo de servidor Telnet da Tech UniSenac representa um avanço significativo em nossas capacidades de comunicação em rede. Ao implementar funcionalidades interativas, controle de acesso por senha e a integração com serviços externos para dados em tempo real (como a temperatura), expandimos as capacidades de um sistema de comunicação básica. A superação dos desafios técnicos, como a gestão de portas, a compatibilidade de codificação e o consumo de APIs, demonstra a robustez e a adaptabilidade da nossa solução, alinhando-se diretamente à nossa missão de transformar a comunicação na era digital. Este projeto serve como uma base sólida para futuras expansões e integrações em ambientes de rede mais complexos.

# TelnetPythonServer

> > > > > > > 3a052df8e8dce8acee4ea444124d3ba3efad3400
