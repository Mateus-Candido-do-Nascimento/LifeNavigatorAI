No Django a separação é assim:
models.py   → estrutura dos dados (tabelas)
views.py    → recebe requisição, devolve resposta
services/   → REGRAS DE NEGÓCIO (a lógica em si)

# No nosso projeto cada service tem uma responsabilidade:
data_service.py    → regra: como buscar e filtrar os dados
intent_service.py  → regra: como identificar o que o usuário quer
prompt_builder.py  → regra: como montar o prompt pro Gemini
gemini_service.py  → regra: como chamar a API e tratar a resposta
guardrails.py      → regra: o que pode e o que não pode 

# depois de ajustar
python manage.py shell

O python manage.py shell abre um terminal Python interativo que já carrega todo o ambiente do Django automaticamente.

A diferença pro Python normal:
powershell# Python normal — não sabe nada do Django
python
>>> from chat.services.data_service import *
# ❌ pode dar erro — Django não está configurado

# Django shell — já carrega tudo
python manage.py shell
>>> from chat.services.data_service import *
# ✅ funciona — conhece settings, banco, models
```
from chat.services.data_service import *

print(buscar_salario_por_cargo("PROFESSOR"))
print(calcular_custo_mensal("solteiro"))
print(calcular_sobra_mensal(5000, "solteiro"))
---

**O que ele carrega automaticamente:**
```
✅ settings.py          → configurações do projeto
✅ conexão com banco     → PostgreSQL já conectado
✅ todos os models       → PerfilUsuario, Conversa, Mensagem
✅ todas as apps         → chat, data
✅ variáveis do .env     → API keys, credenciais

Pra que serve na prática:
É como um "playground" do seu projeto. Você pode testar qualquer coisa antes de colocar em produção:
python# testar uma query no banco
from chat.models import PerfilUsuario
PerfilUsuario.objects.all()

# testar um service
from chat.services.data_service import buscar_salario_por_cargo
buscar_salario_por_cargo("PROFESSOR")

# testar qualquer lógica
from django.utils import timezone
timezone.now()

Analogia:
É como o console do navegador pro JavaScript — você testa o código em tempo real sem precisar criar um endpoint ou rodar o servidor. 🐍
Pode executar agora!

Cria a pasta e os arquivos necessários:
powershell# dentro de backend/
mkdir chat/services

# cria o arquivo __init__.py (obrigatório pro Python reconhecer como módulo)
New-Item chat/services/__init__.py

# cria o arquivo do service
New-Item chat/services/data_service.py
```

---

**Por que o `__init__.py`?**
```
chat/
├── services/
│   ├── __init__.py      ← sem isso o Python não reconhece como módulo
│   └── data_service.py  ← nosso código
O Python só reconhece uma pasta como módulo importável se ela tiver um __init__.py dentro — pode ser vazio mesmo, só precisa existir.