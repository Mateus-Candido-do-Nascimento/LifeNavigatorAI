# Agora, PostgreSQL:
# A forma mais fácil no Windows é instalar o pgAdmin + PostgreSQL juntos num único instalador.

Acesse: postgresql.org/download/windows
Baixe o instalador
Durante a instalação, anote a senha do usuário postgres — você vai precisar dela
Porta padrão: 5432 — pode deixar assim

pg admin e criar a base 

# Passo 1 — Criar o banco de dados
# Abra o pgAdmin (foi instalado junto com o PostgreSQL), conecte com sua senha e rode essa query:
sqlCREATE DATABASE lifenavigator;
# Ou se preferir pelo terminal, abra o SQL Shell (psql) que veio na instalação e rode o mesmo comando.

agora criar o .env.

# Passo 3 — Atualizar o settings.py
# Abra config/settings.py e substitua o bloco DATABASES e adicione o dotenv: