# 🛠️ Plataforma de Conexão de Serviços (Marketplace)

### 📌 Visão Geral

Este projeto é uma plataforma web *Full Stack* desenvolvida para criar um canal direto entre **prestadores de serviços** (MEI/CNPJ) e **clientes** (CPF, Empresas e Condomínios). O objetivo é desintermediar a comunicação, oferecendo total transparência e controle sobre a busca e a seleção de profissionais.

Atualmente, o projeto é um MVP (Produto Mínimo Viável) focado na arquitetura de autenticação, cadastro e visualização de perfis.

---

### 💡 Lógica de Negócio e Funcionalidades

A principal lógica da plataforma se baseia na transparência mútua e na relevância regional.

#### 👤 Tipos de Usuários
1.  **Clientes CPF:** Usuários individuais buscando serviços.
2.  **Clientes CNPJ (Condomínios/Empresas):** Foco em gestão de manutenção e serviços corporativos.
3.  **Prestadores de Serviço (MEI/CNPJ):** Profissionais ofertando suas especialidades.

#### 🔎 Busca e Proximidade
* O sistema exibe Prestadores de Serviço ao Cliente **por proximidade regional**, garantindo relevância geográfica.
* A busca é organizada por **Serviço Principal**, apresentando uma lista de profissionais que se encaixam na categoria solicitada.
* **Transparência Mútua:** O Prestador também terá uma página de Clientes, permitindo a pesquisa e visualização do histórico e avaliações dos clientes (por proximidade, futura implementação).

#### ⭐ Sistema de Avaliações
* **Para Clientes:** A página de detalhes do Prestador exibe a **média de avaliações**. Ao clicar, o cliente vê todos os comentários, que são **sigilosos** (anônimos para o público, visíveis apenas para o ADM <s>e para o Prestador avaliado</s>), visando evitar intrigas.
* **Para Prestadores:** O mesmo modelo de avaliação anônima será implementado para que Prestadores possam comentar sobre a experiência com o Cliente.

---

### ⚙️ Stack Tecnológico e Módulos Python

A aplicação foi estruturada em Python, utilizando Flask como micro-framework, com alta modularidade e foco em segurança e gestão de formulários.

| Categoria | Ferramenta | Módulos Principais |
| :--- | :--- | :--- |
| **Backend (Web)** | Python 3, Flask | `flask`, `werkzeug`, `secrets` |
| **Banco de Dados** | SQLAlchemy | Gerenciamento de persistência de dados (SQL). |
| **Segurança/Forms** | WTForms | `flask_wtf`, `wtforms` (Validação robusta de formulários). |
| **Utilidades** | Diversos | `datetime`, `functools`, `os`, `io`, `PIL`, `typing` |
| **Comunicação** | E-mail | `smtplib`, `email.message` (Futura implementação de notificação). |

### 🚧 Status do Projeto e Próximos Passos

O projeto está em desenvolvimento ativo, focado em estabelecer o núcleo de autenticação e visualização.

| Status | Módulos Concluídos |
| :--- | :--- |
| **Concluído** | Cadastro de Usuários (Clientes/Prestadores), Login, Página Home, Página de Visualização de Prestadores (Lista). |
| **Em Andamento** | Funções de Suporte (contato, e-mail, FAQ), Implementação de Bot/Chatbot para WhatsApp. |

#### Próximos Passos:
1.  [ ] Criação completa da página de **Clientes** (Visão do Prestador).
2.  [ ] Implementação das funções de **Avaliações** (média e listagem detalhada).
3.  [ ] Desenvolvimento do painel administrativo (**Página ADM**).
4.  [ ] Implementação das funções de **Busca** por região e categoria.
5.  [ ] **Planejamento de Migração:** Revisão da arquitetura para futura transição de Flask para **Django**.

---

### 💻 Como Rodar o Projeto (Localmente)

Como o projeto está rodando na máquina fisíca do usuário (eu), é essencial que qualquer recrutador saiba como instalá-lo em ambiente local para teste.

1.  **Clone o Repositório:**
    ```bash
    git clone [COLE O SEU LINK AQUI]
    ```

2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Você deve criar este arquivo. Veja as instruções abaixo.)*

3.  **Execute a Aplicação:**
    ```bash
    python app.py
    # Ou o comando que você usa para iniciar o Flask
    ```
    *O sistema usará o banco de dados SQLite localmente.*

---

## 3. Essenciais do GitHub e `requirements.txt`

### 3.1. O que mais colocar no GitHub?

Além de seus arquivos `.py`, `.html`, `.css` e do **README.md**, você deve incluir:

1.  **`requirements.txt` (Obrigatório!):** Lista todas as bibliotecas que o seu código usa (Flask, SQLAlchemy, WTForms, etc.). Sem este arquivo, ninguém consegue rodar seu projeto.
2.  **Screenshot/Imagens (.png ou .jpg):** Coloque uma imagem da sua página inicial do site! Isso deixa o `README` muito mais atraente e prova que o código gera uma interface. (Você pode colocar essa imagem no topo do README).
3.  **Licença (Opcional, mas profissional):** Arquivo `LICENSE` que define se as pessoas podem usar seu código. Para projetos pessoais, o MIT License é o mais comum. O GitHub tem uma ferramenta que cria isso para você.

### 3.2. Como criar o `requirements.txt`

Este é o comando que você precisa rodar no seu terminal (aquele mesmo do VS Code) para criar o arquivo que lista todas as dependências que você citou:

```bash
pip freeze > requirements.txt
