# LifeNavigator AI

Agente de simulação de decisões financeiras e de carreira focado em concurso público e custo de vida em São Paulo.

## O que faz

- Simula cenários financeiros para quem considera fazer concurso público em SP
- Compara salários do setor público com salário atual do usuário
- Calcula viabilidade de viver em São Paulo com base no perfil (solteiro ou família)
- Responde perguntas como:
  - "Vale a pena fazer concurso de professor ganhando R$5k?"
  - "Quanto ganha um médico no setor público de SP?"
  - "Consigo viver bem em SP com R$4.000?"

## Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | React + Vite + Tailwind |
| Backend | Django + Django REST Framework |
| Banco de dados | PostgreSQL |
| IA | Groq (Llama 3.3 70B) |
| Dados | pandas + datasets públicos SP |

## Arquitetura
```
Frontend React
    ↓ POST /api/chat/
Django REST Framework
    ↓
guardrails.py    → verifica se a mensagem é segura
intent_service.py → identifica intenção com Groq
data_service.py  → busca dados reais com pandas
prompt_builder.py → monta prompt com few-shot + dados
groq_service.py  → gera análise com Llama 3.3 70B
    ↓
Resposta JSON
```

## Datasets

- **Salários públicos SP** — 30.000 registros de funcionários ativos (2023), filtrados e amostrados proporcionalmente por departamento
- **Custo de vida SP** — 57 itens coletados do Numbeo (março/2026) em R$

## Como rodar

### Pré-requisitos

- Python 3.13+
- Node.js 18+
- PostgreSQL

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

Cria o arquivo `.env` em `backend/`:
```env
SECRET_KEY=sua_secret_key
DEBUG=True
DB_NAME=lifenavigator
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
GROQ_API_KEY=sua_chave_groq
```
```bash
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
```

Cria o arquivo `.env` em `frontend/`:
```env
VITE_API_URL=http://localhost:8000
```
```bash
npm run dev
```

Acessa `http://localhost:5173`

## Estrutura do projeto
```
LifeNavigatorAI/
├── backend/
│   ├── chat/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── services/
│   │       ├── data_service.py
│   │       ├── intent_service.py
│   │       ├── prompt_builder.py
│   │       ├── groq_service.py
│   │       ├── guardrails.py
│   │       └── prompts/
│   │           ├── system_prompt.txt
│   │           └── few_shot_examples.txt
│   ├── datasets/
│   │   ├── salarios_limpo.csv
│   │   └── custo_vida_sp_numbeo.csv
│   └── requirements.txt
└── frontend/
    └── src/
        └── App.jsx
```

## Autor

Mateus Candido — Mackenzie University, 3º ano de Ciência da Computação