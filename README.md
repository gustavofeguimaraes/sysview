# 🖥️ SysView
### Sistema de Monitoramento e Gerenciamento de Computadores

**SysView** é um projeto desenvolvido em Python com o objetivo de facilitar o monitoramento, a organização e o gerenciamento de computadores em uma rede.

A proposta é reunir informações importantes dos dispositivos em uma interface centralizada, permitindo acompanhar o desempenho das máquinas, consultar processos e serviços do sistema e, futuramente, realizar ações administrativas de maneira mais prática.

O projeto foi pensado para ambientes de suporte técnico, laboratórios de informática e pequenas redes corporativas.

---

## 🎯 Objetivo

Desenvolver uma ferramenta de gerenciamento que ajude a reduzir tarefas manuais de manutenção e diagnóstico, oferecendo uma visão organizada dos computadores e seus recursos.

O SysView busca unir **simplicidade, desempenho, organização e possibilidade de expansão**.

## ⚙️ Funcionalidades

O projeto contempla módulos voltados para:

- 📊 **Monitoramento de recursos:** informações de CPU, memória RAM e armazenamento.
- 🌐 **Informações de rede:** consulta de interfaces, tráfego e conexões de rede.
- 💻 **Informações do sistema:** identificação e características do computador.
- 📋 **Processos:** consulta e acompanhamento de processos em execução.
- 🛠️ **Serviços do Windows:** consulta de serviços; operações administrativas adicionais estão em desenvolvimento.
- 🖧 **Dispositivos:** cadastro, edição, exclusão, listagem e seleção de máquinas cadastradas.
- 🔗 **Comunicação remota:** estrutura inicial de Agent e transporte TCP/JSON para consultas de informações.
- 🖥️ **Interface gráfica:** painel com páginas de monitoramento e gerenciamento.
- 🗃️ **Persistência:** integração com MySQL para armazenar dispositivos cadastrados.
- 🧪 **Testes automatizados:** testes de componentes para auxiliar na validação do código.

> **Estado atual:** o monitoramento local está implementado. A seleção de um dispositivo cadastrado não significa que o monitoramento remoto já esteja conectado. A autenticação, a criptografia e a integração completa do Agent remoto ainda estão em desenvolvimento.
>
> Algumas funcionalidades dependem de permissões administrativas, configuração da rede e execução do Agent.

## 🧰 Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| Python | Desenvolvimento da aplicação e do Agent |
| PySide6 / Qt | Interface gráfica desktop |
| MySQL | Armazenamento dos dispositivos cadastrados |
| Windows | Plataforma principal nesta fase |
| Git | Controle de versões |
| GitHub | Hospedagem do código-fonte |
| VS Code | Ambiente de desenvolvimento |
| Pytest | Testes automatizados |
| TCP e JSON | Comunicação inicial entre aplicativo e Agent |

## 📁 Estrutura do projeto

```text
SysView/
│
├── app/
│   ├── agent/           # Servidor Agent, protocolo e handlers
│   ├── core/            # Configurações e recursos centrais
│   ├── data/            # Modelos, banco de dados e fontes de dados
│   ├── services/        # Monitoramento e operações do sistema
│   └── ui/              # Interface gráfica
│
├── tests/               # Testes do projeto
├── main.py              # Entrada principal da aplicação
├── requirements.txt     # Dependências Python
├── .gitignore           # Arquivos ignorados pelo Git
└── README.md            # Documentação do projeto
```

## 🚀 Como instalar e executar

### 1. Pré-requisitos

- Windows para executar a interface principal nesta fase.
- Python instalado (ambiente de desenvolvimento utilizado: Python 3.14).
- MySQL Server instalado e em execução, para carregar e gerenciar dispositivos persistidos.
- Git para clonar o repositório.
- PowerShell ou terminal do VS Code.
- Dependências listadas em `requirements.txt`.

> A instalação do MySQL, a criação do banco `sysview`, das tabelas e do usuário `sysview_app` devem ser realizadas conforme o esquema e os scripts SQL do projeto. O comando `python main.py` não substitui essa configuração inicial.

### 2. Clonar o projeto

```powershell
git clone https://github.com/gustavofeguimaraes/sysview.git
cd sysview
```

Se o projeto já estiver baixado, basta abrir a pasta dele no VS Code. No computador usado no desenvolvimento, o caminho era:

```powershell
cd C:\Users\gusta\Desktop\SysView
```

### 3. Criar e ativar o ambiente virtual

Na pasta raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

O terminal deve começar com `(.venv)`.

> Se o PowerShell bloquear a ativação, configure a política de execução apenas para o processo atual, conforme as regras do seu computador:
>
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

### 4. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 5. Configurar o acesso ao MySQL

O projeto lê o usuário e a senha pelas variáveis de ambiente `SYSVIEW_DB_USER` e `SYSVIEW_DB_PASSWORD` (configuração em `app/core/config.py`).

No mesmo terminal em que você vai iniciar o SysView:

```powershell
$env:SYSVIEW_DB_USER = "sysview_app"
$env:SYSVIEW_DB_PASSWORD = Read-Host "Digite a senha do usuario sysview_app"
```

Digite a senha configurada para o usuário `sysview_app` no MySQL. A senha não é a do usuário `root`, a menos que você tenha configurado isso explicitamente.

Essas variáveis ficam disponíveis somente na sessão atual do PowerShell. Ao abrir um novo terminal, será necessário configurá-las novamente.

**Não publique senhas no README, em arquivos versionados ou em capturas de tela.**

### 6. Iniciar a interface gráfica

```powershell
python main.py
```

Se o MySQL estiver configurado corretamente, o SysView abrirá a interface e carregará os dispositivos registrados.

### 7. Como visualizar o projeto

Ao abrir o SysView, utilize o menu lateral para navegar entre as páginas:

- **Dashboard:** visão geral do computador local.
- **Computador:** informações do sistema.
- **CPU:** dados de processamento.
- **Memória:** utilização de RAM.
- **Disco:** informações de armazenamento.
- **Rede:** interfaces e atividade de rede.
- **Conexões de rede:** conexões detectadas.
- **Processos:** lista e informações dos processos.
- **Serviços:** serviços do Windows.
- **Dispositivos:** lista de máquinas cadastradas e ações de cadastro.

Na página **Dispositivos**, é possível selecionar um alvo cadastrado. Nesta fase, a seleção é visual/organizacional e **não ativa automaticamente o monitoramento remoto**; as páginas de monitoramento continuam mostrando o computador local até a integração remota ser concluída.

## 🔌 Como iniciar e testar o SysView Agent

O Agent é o servidor responsável por receber requisições do protocolo SysView e devolver informações do computador em que está executando.

**Importante:** a versão atual do Agent ainda não possui autenticação e criptografia implementadas. Portanto, **mantenha-o restrito ao endereço local `127.0.0.1` e não exponha a porta 8765 à rede ou à internet**.

### Terminal 1 — iniciar o Agent

Abra um terminal na raiz do projeto e ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.agent.server
```

Saída esperada:

```text
SysView Agent iniciado em 127.0.0.1:8765
```

Deixe esse terminal aberto durante o teste.

### Terminal 2 — verificar a comunicação

Abra outro terminal na mesma pasta do projeto, ative o ambiente virtual e execute:

```powershell
.\.venv\Scripts\Activate.ps1
python -c "from app.data.sources.remote_transport import RemoteTransport; print(RemoteTransport('127.0.0.1').send_request('ping', 'teste-001'))"
```

Resposta esperada:

```python
{'version': 1, 'type': 'response', 'request_id': 'teste-001', 'success': True, 'payload': {'message': 'pong'}}
```

Esse retorno confirma a comunicação local TCP/JSON entre cliente e Agent. **Não comprova ainda a comunicação entre dois computadores.**

Para parar o Agent, pressione `Ctrl+C` no Terminal 1.

## 🧪 Testes automatizados

Com o ambiente virtual ativado, execute:

```powershell
python -m pytest tests/ -q
```

O projeto já registrou **148 testes passando** durante o desenvolvimento; essa quantidade pode mudar conforme novas funcionalidades e testes forem adicionados.

## 🛠️ Solução de problemas

### `ModuleNotFoundError: No module named 'app'`

Verifique se o terminal está na raiz do projeto (pasta que contém `main.py` e `app/`):

```powershell
Get-Location
```

Se necessário, entre na pasta correta e ative o ambiente virtual antes de executar os comandos.

### `Access denied for user 'sysview_app'@'localhost' (using password: NO)`

A aplicação tentou conectar ao MySQL sem enviar senha. Configure `SYSVIEW_DB_PASSWORD` no terminal atual e execute `python main.py` novamente.

### Falha de conexão ao Agent

Confirme que o Agent está rodando no Terminal 1 e que a porta local `8765` não está ocupada por outro processo. Não altere o host para `0.0.0.0` como solução rápida: primeiro serão necessários autenticação e transporte protegido.

## 🏗️ Arquitetura

O SysView utiliza uma estrutura modular, separando responsabilidades:

- **Interface (`app/ui`):** apresenta informações e permite a interação do usuário.
- **Serviços (`app/services`):** concentra operações de monitoramento e gerenciamento.
- **Dados (`app/data`):** modelos de dispositivos, persistência e fontes de informações locais/remotas.
- **Agente (`app/agent`):** servidor, protocolo e handlers de requisições.
- **Núcleo (`app/core`):** configurações e funcionalidades compartilhadas.

Essa organização facilita a manutenção do código e a implementação de novos recursos.

## 🔮 Evolução do projeto

Entre as próximas etapas planejadas estão:

- Autenticação de clientes no Agent.
- Criptografia da comunicação antes de habilitar acesso pela rede.
- Integração real do dispositivo selecionado com o monitoramento remoto.
- Operações administrativas remotas com controle de permissões.
- Histórico de monitoramento e armazenamento de métricas.
- Alertas sobre problemas de desempenho e disponibilidade.
- Ampliação do suporte a dispositivos e plataformas.
- Otimizações de desempenho e experiência do usuário.

> O foco atual do aplicativo é Windows. O suporte a Linux e Android não deve ser considerado implementado nesta etapa.

## 🔐 Segurança

O SysView é voltado ao gerenciamento **autorizado** de dispositivos.

Recursos administrativos e remotos devem ser usados somente em computadores e redes para os quais o operador possua autorização. Não exponha o Agent atual à rede pública ou à internet, pois ainda faltam mecanismos de autenticação e criptografia.

Credenciais, arquivos de configuração privados e dados sensíveis não devem ser publicados no repositório. Evite executar a aplicação com privilégios de administrador quando eles não forem necessários.

## 🎓 Contexto acadêmico

Projeto desenvolvido como parte das atividades acadêmicas da **Faculdade de Tecnologia de Indaiatuba (FATEC Indaiatuba)**, aplicando conceitos de desenvolvimento de software, organização de código, monitoramento de sistemas e comunicação em rede.

## 👨‍💻 Desenvolvedor

**Gustavo Ferreira Guimarães**

Estudante da FATEC Indaiatuba.

GitHub: [@gustavofeguimaraes](https://github.com/gustavofeguimaraes)

---

**SysView — Monitoramento e gerenciamento de computadores em uma única solução.**

*Projeto acadêmico em desenvolvimento contínuo.*
