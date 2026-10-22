# 🖥️ SysView
### Sistema de Monitoramento e Gerenciamento de Computadores

**SysView** é um projeto desenvolvido em Python com o objetivo de facilitar o monitoramento, a organização e o gerenciamento de computadores em uma rede.

A proposta é reunir informações importantes dos dispositivos em uma interface centralizada, permitindo acompanhar o desempenho das máquinas, consultar processos e serviços do sistema e realizar ações administrativas de maneira mais prática.

O projeto foi pensado para ambientes de suporte técnico, laboratórios de informática e pequenas redes corporativas.

---

## 🎯 Objetivo

Desenvolver uma ferramenta de gerenciamento que ajude a reduzir tarefas manuais de manutenção e diagnóstico, oferecendo uma visão organizada dos computadores e seus recursos.

O SysView busca unir **simplicidade, desempenho, organização e possibilidade de expansão**.

## ⚙️ Funcionalidades

O projeto contempla módulos voltados para:

- 📊 **Monitoramento de recursos:** informações de CPU, memória RAM e armazenamento.
- 🌐 **Informações de rede:** consulta de interfaces e conexões de rede.
- 💻 **Informações do sistema:** identificação e características do computador.
- 📋 **Gerenciamento de processos:** consulta e acompanhamento de processos em execução.
- 🛠️ **Serviços do Windows:** consulta e gerenciamento de serviços.
- 🖧 **Dispositivos:** organização e identificação de máquinas monitoradas.
- 🔗 **Comunicação remota:** estrutura de agente e transporte de comandos entre dispositivos.
- 🖥️ **Interface gráfica:** painel para visualização e interação com os recursos do sistema.
- 🧪 **Testes automatizados:** módulos de testes para auxiliar na validação do código.

> Algumas funcionalidades podem depender de permissões administrativas, configuração da rede e execução do agente remoto.

## 🧰 Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| Python | Desenvolvimento da aplicação |
| Windows | Plataforma inicial do projeto |
| Git | Controle de versões |
| GitHub | Hospedagem do código-fonte |
| VS Code | Ambiente de desenvolvimento |
| Pytest | Testes automatizados |

## 📁 Estrutura do projeto

```text
SysView/
│
├── app/
│   ├── agent/           # Agente de comunicação remota
│   ├── core/            # Configurações e recursos centrais
│   ├── data/            # Modelos e fontes de dados
│   ├── services/        # Monitoramento e operações do sistema
│   └── ui/              # Interface gráfica
│
├── tests/               # Testes do projeto
├── main.py              # Entrada principal da aplicação
├── requirements.txt     # Dependências Python
├── .gitignore           # Arquivos ignorados pelo Git
└── README.md            # Documentação do projeto
```

## 🚀 Como executar

### 1. Pré-requisitos

- Windows
- Python instalado
- Git, para clonar o repositório
- Dependências disponíveis no `requirements.txt`

### 2. Clonar o projeto

```bash
git clone https://github.com/gustavofeguimaraes/sysview.git
cd sysview
```

### 3. Criar um ambiente virtual

```powershell
python -m venv .venv
```

Ativar o ambiente virtual no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 5. Iniciar a aplicação

```powershell
python main.py
```

> A execução de determinadas operações poderá exigir configurações adicionais ou permissões de administrador.

## 🧪 Testes

O projeto possui testes para diferentes componentes, incluindo modelos de dispositivos, fontes de dados, monitoramento, comunicação e serviços.

Para executar os testes:

```powershell
python -m pytest tests/
```

Os testes auxiliam na identificação de falhas e na manutenção da qualidade do código durante o desenvolvimento.

## 🏗️ Arquitetura

O SysView utiliza uma estrutura modular, separando responsabilidades em diferentes camadas.

- **Interface (`ui`):** apresenta informações e permite a interação do usuário.
- **Serviços (`services`):** concentra as operações de monitoramento e gerenciamento.
- **Dados (`data`):** organiza os modelos e as fontes de informações.
- **Agente (`agent`):** estrutura a comunicação com dispositivos remotos.
- **Núcleo (`core`):** reúne configurações e funcionalidades compartilhadas.

Essa organização facilita a manutenção do código e a implementação de novos recursos.

## 🔮 Evolução do projeto

Entre as possibilidades de expansão estão:

- Melhorias no gerenciamento remoto de computadores.
- Autenticação e controle de permissões.
- Histórico de monitoramento e armazenamento de dados.
- Alertas sobre problemas de desempenho e disponibilidade.
- Ampliação do suporte a dispositivos e plataformas.
- Otimizações de desempenho e experiência do usuário.

## 🔐 Segurança

O SysView é voltado ao gerenciamento autorizado de dispositivos.

A utilização de recursos administrativos e remotos deve ocorrer apenas em computadores e redes para os quais o operador possua autorização.

Credenciais, arquivos de configuração privados e dados sensíveis não devem ser publicados no repositório.

## 🎓 Contexto acadêmico

Projeto desenvolvido como parte das atividades acadêmicas da **Faculdade de Tecnologia de Indaiatuba (FATEC Indaiatuba)**, aplicando conceitos de desenvolvimento de software, organização de código, monitoramento de sistemas e comunicação em rede.

## 👨‍💻 Desenvolvedor

**Gustavo Ferreira Guimarães**

Estudante da FATEC Indaiatuba.

GitHub: [@gustavofeguimaraes](https://github.com/gustavofeguimaraes)

---

**SysView — Monitoramento e gerenciamento de computadores em uma única solução.**

*Projeto acadêmico em desenvolvimento contínuo.*