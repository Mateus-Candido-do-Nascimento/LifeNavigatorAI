from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def gerar_resposta(messages: list[dict]) -> str:
    """
    Recebe a lista de mensagens montada pelo prompt_builder
    e retorna a resposta gerada pelo Groq.

    Args:
        messages: lista no formato [{"role": "...", "content": "..."}]

    Returns:
        texto da resposta gerada
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,  # baixo = mais consistente e analítico
            max_tokens=1000,  # suficiente para 2-3 cenários
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"