
Instala o pacote de CORS do Django:

powershell
# entra na pasta backend
cd ../backend

pip install django-cors-headers
Adiciona no settings.py:

python
INSTALLED_APPS = [
    ...
    "corsheaders",  # ← adiciona
    "rest_framework",
    "chat",
    "data",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ← primeira linha do middleware
    "django.middleware.security.SecurityMiddleware",
    ...
]

# permite requisições do React
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]