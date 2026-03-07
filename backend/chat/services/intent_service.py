from groq import Groq
import json
from django.conf import settings

# instancia o cliente Groq com a chave do .env
client = Groq(api_key=settings.GROQ_API_KEY)


def identificar_intencao(mensagem: str) -> dict:
    """
    Recebe a mensagem do usuário em linguagem natural e retorna
    um dicionário estruturado com as informações extraídas.

    Exemplo:
        entrada: "Vale a pena fazer concurso de professor ganhando R$5k?"
        saída: {
            "cargo": "PROFESSOR",
            "salario_atual": 5000,
            "perfil": "solteiro",
            "acoes": ["buscar_salario_por_cargo", "calcular_sobra_mensal"]
        }
    """

    prompt = f"""
Você é um extrator de informações. Analise a mensagem abaixo e retorne 
APENAS um JSON válido, sem explicações, sem markdown, sem texto adicional.

Extraia as seguintes informações da mensagem:

- "cargo": cargo público mencionado em MAIÚSCULAS (ex: "PROFESSOR", "MEDICO", "POLICIAL"). 
   Se não mencionou nenhum cargo, retorne null.

- "departamento": departamento ou secretaria mencionada (ex: "SAUDE", "EDUCACAO"). 
   Se não mencionou, retorne null.

- "salario_atual": salário atual mencionado como número (ex: 5000). 
   Se não mencionou, retorne null.

- "perfil": perfil de vida mencionado. 
   Opções: "solteiro", "familia". 
   Se não mencionou, assuma "solteiro".

- "acoes": lista de ações necessárias para responder a pergunta.
   Opções disponíveis:
   - "buscar_salario_por_cargo"        → quando pergunta sobre salário de um cargo
   - "buscar_salario_por_departamento" → quando pergunta sobre um departamento
   - "listar_maiores_salarios"         → quando pergunta quais cargos pagam mais
   - "calcular_custo_mensal"           → quando pergunta sobre custo de vida em SP
   - "calcular_sobra_mensal"           → quando pergunta se consegue viver com X salário

- "fora_do_escopo": true se a pergunta não tem nada a ver com 
   concurso público, salários ou custo de vida em SP. false caso contrário.

Mensagem do usuário: "{mensagem}"

Retorne APENAS o JSON. Exemplo de saída esperada:
{{
    "cargo": "PROFESSOR",
    "departamento": null,
    "salario_atual": 5000,
    "perfil": "solteiro",
    "acoes": ["buscar_salario_por_cargo", "calcular_sobra_mensal"],
    "fora_do_escopo": false
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # modelo gratuito do Groq
            messages=[
                {
                    "role": "system",
                    "content": "Você é um extrator de informações. Retorne APENAS JSON válido, sem markdown, sem explicações."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # baixo — queremos respostas consistentes e precisas
            max_tokens=300,   # JSON pequeno, não precisa de muito
        )

        # extrai o texto da resposta
        texto = response.choices[0].message.content.strip()
        texto = texto.replace("```json", "").replace("```", "").strip()

        # converte pra dicionário Python
        intencao = json.loads(texto)
        return intencao

    except Exception as e:
        return {
            "cargo": None,
            "departamento": None,
            "salario_atual": None,
            "perfil": "solteiro",
            "acoes": ["calcular_custo_mensal"],
            "fora_do_escopo": False,
            "erro": str(e),
        }