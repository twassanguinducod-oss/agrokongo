# AgroKongo 🚜🇦🇴
**Marketplace Agrícola Resiliente para Angola.**

O AgroKongo é uma plataforma de intermediação agrícola de alto rigor técnico, focada em resolver o gap de confiança entre produtores e compradores através de um sistema de **Escrow Blindado** e validação rigorosa de identidade (KYC).

---

## 🛡️ Auditoria de Segurança & Integridade (Backend Sênior)
O backend foi submetido a uma auditoria rigorosa para garantir a segurança das transações financeiras:

*   **Atomicidade Financeira:** Uso de `@transaction.atomic` e `select_for_update()` do PostgreSQL para impedir Condições de Corrida (Race Conditions) em saldos e estoque.
*   **Impossibilidade de Gasto Duplo:** Lógica de bloqueio ao nível de linha (Locking) para levantamentos e liberações de pagamento.
*   **Escrow Administrativo:** Fluxo de 3 etapas (`Pago` -> `Recebido` -> `Liquidado`) mediado por auditoria administrativa para evitar cancelamentos indevidos de fundos em custódia.
*   **Validação IBAN ISO 7064:** Implementação do algoritmo Módulo 97-10 para validação matemática de IBANs angolanos (AO06).
*   **Proteção de Uploads:** Validação de MIME Type (Magic Numbers) em binários para prevenir ataques de execução remota (RCE).
*   **Privacidade:** Segregação de dados sensíveis entre perfis públicos e privados via Serializers distintos.
*   **Performance:** Dashboard otimizado com cache em memória via Redis.

---

## 🏗️ Tech Stack
*   **Backend:** Django 5 + Django REST Framework + Django-Filter.
*   **Frontend:** Next.js 14 (App Router) + Tailwind CSS + Framer Motion.
*   **Infraestrutura:** Redis (Cache), PostgreSQL (DB), Celery (Background Tasks).
*   **Autenticação:** JWT (Stateless).

---

## 📊 Estrutura de Pastas
```plaintext
├── accounts/           # Usuários, Saldo, Levantamentos e KYC
├── marketplace/        # Safras, Reservas, Escrow e Pagamentos
├── locations/          # Geo-localização (Províncias/Municípios)
├── core/               # Notificações, Mensagens e Logs de Auditoria
├── frontend/           # Aplicação Next.js
└── static/media/       # Ficheiros estáticos e uploads (protegidos)
```

---

## 🚀 Como Executar (Desenvolvimento)

1.  **Backend:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```

2.  **Worker Celery (em outro terminal):**
    ```bash
    celery -A agrokongo worker --loglevel=info
    ```

3.  **Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

---
© 2024 AgroKongo - Engenharia de Software para o Agronegócio Angolano.
