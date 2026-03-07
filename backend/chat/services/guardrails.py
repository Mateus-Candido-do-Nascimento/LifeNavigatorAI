from groq import Groq
import json
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

# camada 1 — filtro rápido sem chamada à API
TOPICOS_BLOQUEADOS = [
    "fraude", "fraudar", "colar", "cola",
    "manipular", "esquema", "ilegal",
    "corrupção", "propina", "suborno",
]

DADOS_SENSIVEIS = [
    "cpf", "rg", "senha", "conta bancária",
    "cartão de crédito", "número do cartão",
    "cvv", "agência",
]


def _contem_termo(mensagem: str, termos: list[str]) -> bool:
    return any(termo in mensagem.lower() for termo in termos)


def _bloquear(motivo: str, resposta: str) -> dict:
    # helper pra não repetir código
    return {"permitido": False, "motivo": motivo, "resposta": resposta}


def _verificar_com_groq(mensagem: str) -> dict:
    # camada 2 — Groq classifica casos ambíguos
    prompt = f"""
Analise se essa mensagem é apropriada para um assistente especializado
em concurso público e custo de vida em São Paulo.

Retorne APENAS um JSON válido, sem explicações:
{{
    "permitido": true ou false,
    "motivo": "topico_bloqueado" | "dado_sensivel" | "fora_do_escopo" | null,
    "resposta": "mensagem curta ao usuário se bloqueado, null se permitido"
}}

Bloquear se:
- Pedir ajuda com fraude, corrupção ou atividades ilegais
- Conter dados pessoais sensíveis (CPF, senha, conta bancária)
- For completamente fora do escopo (receitas, esportes, entretenimento)

Permitir se:
- For sobre salários, concursos, custo de vida, carreira, finanças pessoais

Mensagem: "{mensagem}"
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150,
        )
        texto = response.choices[0].message.content.strip()
        texto = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto)

    except Exception:
        # se der erro na API, permite por padrão (não bloqueia o usuário)
        return {"permitido": True, "motivo": None, "resposta": None}


def verificar_mensagem(mensagem: str) -> dict:
    """
    Verifica se a mensagem pode ser processada pelo agente.

    Fluxo:
        1. Lista de palavras — casos óbvios, sem custo de API
        2. Groq — casos ambíguos, mais inteligente

    Retorna:
        permitido: True se pode seguir
        motivo: qual regra foi violada
        resposta: mensagem ao usuário se bloqueado
    """

    # camada 1 — lista de palavras (instantâneo)
    if _contem_termo(mensagem, TOPICOS_BLOQUEADOS):
        return _bloquear(
            "topico_bloqueado",
            "Não posso ajudar com essa solicitação. Estou especializado em análises de concurso público e custo de vida dentro da legalidade."
        )

    if _contem_termo(mensagem, DADOS_SENSIVEIS):
        return _bloquear(
            "dado_sensivel",
            "Por favor, não compartilhe dados pessoais sensíveis. Preciso apenas de informações como cargo, salário e perfil de vida."
        )

    # camada 2 — Groq (casos ambíguos)
    return _verificar_com_groq(mensagem)