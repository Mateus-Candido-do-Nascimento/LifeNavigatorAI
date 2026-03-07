from pathlib import Path

# carrega os arquivos de texto externos
_BASE = Path(__file__).resolve().parent / "prompts"

SYSTEM_PROMPT = (
    (_BASE / "system_prompt.txt").read_text(encoding="utf-8")
    + "\n"
    + (_BASE / "few_shot_examples.txt").read_text(encoding="utf-8")
)

def _formatar_salario(dados_salario: dict) -> list[str]:
    """Formata dados de salário para exibição."""
    linhas = []
    linhas.append(f"- Salário mediano de {dados_salario['cargo']} no setor público SP: R${dados_salario['mediana']:,.2f}/mês")
    linhas.append(f"  Faixa: R${dados_salario['minimo']:,.2f} a R${dados_salario['maximo']:,.2f} ({dados_salario['amostras']} registros)")
    return linhas


def _formatar_departamento(dados_depto: dict) -> list[str]:
    """Formata dados de departamento para exibição."""
    linhas = []
    linhas.append(f"- Salário mediano em {dados_depto['departamento']}: R${dados_depto['salario_mediano']:,.2f}/mês bruto")
    linhas.append(f"  Líquido mediano: R${dados_depto['salario_liquido_mediano']:,.2f}/mês")
    return linhas


def _formatar_custo_vida(dados_custo: dict) -> list[str]:
    """Formata dados de custo de vida para exibição."""
    linhas = []
    linhas.append(f"- Custo de vida SP ({dados_custo['perfil']}) sem aluguel: R${dados_custo['total_sem_aluguel']:,.2f}/mês")
    linhas.append(f"  Com aluguel fora do centro: R${dados_custo['total_com_aluguel_fora_centro']:,.2f}/mês")
    linhas.append(f"  Com aluguel no centro: R${dados_custo['total_com_aluguel_centro']:,.2f}/mês")
    return linhas


def _formatar_sobra(dados_sobra: dict) -> list[str]:
    """Formata dados de sobra mensal para exibição."""
    linhas = []
    linhas.append(f"- Sobra mensal com R${dados_sobra['salario_liquido']:,.2f}:")
    linhas.append(f"  Sem aluguel: R${dados_sobra['sobra_sem_aluguel']:,.2f}")
    linhas.append(f"  Com aluguel fora do centro: R${dados_sobra['sobra_com_aluguel_fora_centro']:,.2f}")
    situacao = 'Sim' if dados_sobra['vive_confortavelmente'] else 'Não'
    linhas.append(f"  Vive confortavelmente: {situacao}")
    return linhas


def formatar_dados(dados: dict) -> str:
    """Transforma o dict do data_service em texto formatado para o prompt."""
    linhas = []

    # Processa cada seção de dados se disponível
    if (salario := dados.get("salario")) and salario.get("disponivel"):
        linhas.extend(_formatar_salario(salario))

    if (departamento := dados.get("departamento")) and departamento.get("disponivel"):
        linhas.extend(_formatar_departamento(departamento))

    if (custo := dados.get("custo_mensal")) and custo.get("disponivel"):
        linhas.extend(_formatar_custo_vida(custo))

    if (sobra := dados.get("sobra")) and sobra.get("disponivel"):
        linhas.extend(_formatar_sobra(sobra))

    return "\n".join(linhas) if linhas else "Nenhum dado encontrado para esta consulta."


def montar_prompt(
    mensagem: str,
    dados: dict,
    historico: list[dict] | None = None,
) -> list[dict]:
    """Monta as mensagens no formato esperado pela API Groq.
    
    Args:
        mensagem: A pergunta do usuário
        dados: Dicionário com dados de contexto (salário, custo de vida, etc.)
        historico: Lista anterior de mensagens da conversa
    
    Returns:
        Lista de dicionários com role e content para a API
    """
    if historico is None:
        historico = []

    contexto_dados = formatar_dados(dados)

    mensagem_com_contexto = f"""Dados disponíveis:
{contexto_dados}

Pergunta: {mensagem}"""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(historico)
    messages.append({"role": "user", "content": mensagem_com_contexto})

    return messages