#Startar o projeto

django-admin startproject config .
python manage.py startapp chat
python manage.py startapp data


# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual (Windows)
# No PowerShell, use:
.\venv\Scripts\Activate.ps1

# Primeiro, permita a execução de scripts (como administrador)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Depois tente ativar novamente
.\venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install django djangorestframework python-dotenv pandas psycopg2-binary google-generativeai

# Gerar o arquivo com todas as dependências instaladas
pip freeze > requirements.txt
# crie os apps 
python manage.py startapp data
python manage.py startapp chat
# depois executei 
python manage.py runserver 0.0.0.0:8000

# quando eu rodo o comando acima eu ja crio o db ou seja tudo que esta no config da nossa aplicação roda.

# You have 18 unapplied migrations → Django tem tabelas internas dele mesmo (usuários, sessões, admin) que ainda não foram criadas no banco. É normal num projeto novo. Resolve com:
python manage.py migrate