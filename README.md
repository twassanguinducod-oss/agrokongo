# AgroKongo 🚜🇦🇴
**Conectando a Terra ao Mercado com Segurança.**

O AgroKongo é uma plataforma de intermediação agrícola focada no mercado angolano, resolvendo o problema da falta de confiança entre produtores rurais e compradores urbanos através de um sistema de **Escrow (Custódia Financeira)** e validação de identidade (KYC).

---

## 🛡️ O Diferencial: Escrow Inteligente
Diferente de um classificado comum, o AgroKongo protege o capital transacionado:

1.  **Custódia Segura:** O dinheiro do comprador é retido pela plataforma até a confirmação da entrega.
2.  **Proteção ao Produtor:** O agricultor só inicia a colheita ou o envio após a garantia de que o valor já está em posse da plataforma.
3.  **Liquidação Automatizada (95/5):** Após a entrega, o sistema liquida 95% do valor ao produtor e retém 5% de comissão operacional.
4.  **Gestão de Disputas:** Mediação administrativa em casos de divergência na qualidade ou logística.

---

## 🏗️ Arquitetura e Tech Stack
O projeto foi migrado para uma arquitetura moderna e escalável:

*   **Backend:** Python 3.11 + **Django REST Framework** (API First).
*   **Frontend:** **React / Next.js 14** (App Router) + Tailwind CSS + Framer Motion.
*   **Base de Dados:** **PostgreSQL** (Relacional e Robusto).
*   **Autenticação:** JWT (JSON Web Tokens) com SimpleJWT.
*   **Background Jobs:** Celery + Redis (Processamento de faturas e auditoria).
*   **Documentação:** Swagger/OpenAPI via `drf-spectacular`.
*   **Infraestrutura:** Docker & Docker Compose.

---

## 📊 Estrutura do Projeto
```plaintext
├── accounts/           # Gestão de Usuários, Perfis e Autenticação
├── marketplace/        # Motor de Vendas, Safras, Transações e Escrow
├── locations/          # Geo-localização (Províncias e Municípios de Angola)
├── core/               # Lógica compartilhada, Notificações e Helpers
├── agrokongo/          # Configurações globais do Django (Settings/URLs)
├── frontend/           # Aplicação Next.js (Interface do Usuário)
│   ├── src/app/        # Páginas e Rotas (Next.js App Router)
│   ├── src/components/ # Componentes UI Reutilizáveis
│   └── src/contexts/   # Gerenciamento de Estado (Auth, etc.)
├── static/             # Arquivos estáticos globais
├── media/              # Uploads (Fotos de Safras, Documentos KYC)
├── logs/               # Registros de auditoria do sistema
├── docker-compose.yml  # Orquestração de serviços (Django, Postgres, Redis, Next.js)
└── modelo_relacional_agrokongo.txt # Documentação da Base de Dados
```

---

## 🚀 Como Executar (Desenvolvimento)

### 1. Requisitos
*   Docker & Docker Compose
*   Node.js 18+ (para desenvolvimento frontend local)
*   Python 3.11+ (para desenvolvimento backend local)

### 2. Configuração
Clone o repositório e configure as variáveis de ambiente:
```bash
git clone https://github.com/teu-usuario/agrokongo.git
cd agrokongo
```
Crie um arquivo `.env` na raiz seguindo o modelo das configurações em `agrokongo/settings.py`.

### 3. Execução via Docker
```bash
docker-compose up -d --build
```
*   **Backend API:** `http://localhost:8000/api/`
*   **Documentação (Swagger):** `http://localhost:8000/api/docs/`
*   **Frontend Web:** `http://localhost:3000`

---

## 🔐 Segurança e Compliance
*   **KYC (Know Your Customer):** Validação obrigatória de NIF e IBAN para produtores.
*   **RBAC (Role-Based Access Control):** Permissões distintas para Produtores, Compradores e Administradores.
*   **Audit Trail:** Histórico imutável de mudanças de status em todas as transações financeiras.

---
© 2024 AgroKongo - Soluções Agrícolas Digitais para Angola.
# AgroKongo 🚜🇦🇴
**Conectando a Terra ao Mercado com Segurança.**

O AgroKongo é uma plataforma de intermediação agrícola focada no mercado angolano, resolvendo o problema da falta de confiança entre produtores rurais e compradores urbanos através de um sistema de **Escrow (Custódia Financeira)** e validação de identidade (KYC).

---

## 🛡️ O Diferencial: Escrow Inteligente
Diferente de um classificado comum, o AgroKongo protege o capital transacionado:

1.  **Custódia Segura:** O dinheiro do comprador é retido pela plataforma até a confirmação da entrega.
2.  **Proteção ao Produtor:** O agricultor só inicia a colheita ou o envio após a garantia de que o valor já está em posse da plataforma.
3.  **Liquidação Automatizada (95/5):** Após a entrega, o sistema liquida 95% do valor ao produtor e retém 5% de comissão operacional.
4.  **Gestão de Disputas:** Mediação administrativa em casos de divergência na qualidade ou logística.

---

## 🏗️ Arquitetura e Tech Stack
O projeto foi migrado para uma arquitetura moderna e escalável:

*   **Backend:** Python 3.11 + **Django REST Framework** (API First).
*   **Frontend:** **React / Next.js 14** (App Router) + Tailwind CSS + Framer Motion.
*   **Base de Dados:** **PostgreSQL** (Relacional e Robusto).
*   **Autenticação:** JWT (JSON Web Tokens) com SimpleJWT.
*   **Background Jobs:** Celery + Redis (Processamento de faturas e auditoria).
*   **Documentação:** Swagger/OpenAPI via `drf-spectacular`.
*   **Infraestrutura:** Docker & Docker Compose.

---

## 📊 Estrutura do Projeto
```plaintext
├── accounts/           # Gestão de Usuários, Perfis e Autenticação
├── marketplace/        # Motor de Vendas, Safras, Transações e Escrow
├── locations/          # Geo-localização (Províncias e Municípios de Angola)
├── core/               # Lógica compartilhada, Notificações e Helpers
├── agrokongo/          # Configurações globais do Django (Settings/URLs)
├── frontend/           # Aplicação Next.js (Interface do Usuário)
│   ├── src/app/        # Páginas e Rotas (Next.js App Router)
│   ├── src/components/ # Componentes UI Reutilizáveis
│   └── src/contexts/   # Gerenciamento de Estado (Auth, etc.)
├── static/             # Arquivos estáticos globais
├── media/              # Uploads (Fotos de Safras, Documentos KYC)
├── logs/               # Registros de auditoria do sistema
├── docker-compose.yml  # Orquestração de serviços (Django, Postgres, Redis, Next.js)
└── modelo_relacional_agrokongo.txt # Documentação da Base de Dados
```

---

## 🚀 Como Executar (Desenvolvimento)

### 1. Requisitos
*   Docker & Docker Compose
*   Node.js 18+ (para desenvolvimento frontend local)
*   Python 3.11+ (para desenvolvimento backend local)

### 2. Configuração
Clone o repositório e configure as variáveis de ambiente:
```bash
git clone https://github.com/teu-usuario/agrokongo.git
cd agrokongo
```
Crie um arquivo `.env` na raiz seguindo o modelo das configurações em `agrokongo/settings.py`.

### 3. Execução via Docker
```bash
docker-compose up -d --build
```
*   **Backend API:** `http://localhost:8000/api/`
*   **Documentação (Swagger):** `http://localhost:8000/api/docs/`
*   **Frontend Web:** `http://localhost:3000`

---

## 🔐 Segurança e Compliance
*   **KYC (Know Your Customer):** Validação obrigatória de NIF e IBAN para produtores.
*   **RBAC (Role-Based Access Control):** Permissões distintas para Produtores, Compradores e Administradores.
*   **Audit Trail:** Histórico imutável de mudanças de status em todas as transações financeiras.

---
© 2024 AgroKongo - Soluções Agrícolas Digitais para Angola.

└── run.py              # Entry point da aplicação
