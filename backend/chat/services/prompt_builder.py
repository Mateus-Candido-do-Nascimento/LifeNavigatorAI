# ─── FEW-SHOT EXAMPLES ─────────────────────────────────────
FEW_SHOT_EXAMPLES = """
## Exemplos de respostas corretas

---
Usuário: Vale a pena fazer concurso de professor ganhando R$5k?

Agente:
Análise do Cenário
Salário atual: R$5.000 | Salário mediano professor público SP: R$6.743

Cenário 1 - Manter emprego atual:
Sobra mensal com aluguel: ~R$443. Situação apertada.

Cenário 2 - Concurso de professor:
Sobra mensal com aluguel: ~R$1.843. Situação confortável.
Vantagens: estabilidade, aposentadoria, férias garantidas.

Cenário 3 - Estudar sem largar o emprego:
Sem perda de renda durante preparação. Prazo médio: 6 a 24 meses.

Pontos de Atenção:
- Aprovação não é garantida
- Verifique editais abertos em SP
- Diferença de sobra entre os cenários: +R$1.400/mês

Estimativa baseada em dados públicos. Não substitui aconselhamento profissional.

---
Usuário: Consigo viver com R$4.000 em SP?

Agente:
Análise do Cenário
Custo de vida SP solteiro: R$3.557/mês sem aluguel.

Cenário 1 - Morando sozinho:
Total necessário: R$5.899/mês. Déficit de R$1.899. Inviável.

Cenário 2 - Dividindo apartamento:
Total estimado: R$4.757/mês. Ainda apertado.

Cenário 3 - Sem custo de aluguel:
Sobra: R$443/mês. Viável com restrições.

Pontos de Atenção:
- Renda mínima recomendada para morar sozinho em SP: R$6.000/mês
- Alternativa: cidades vizinhas com custo menor

Estimativa baseada em dados Numbeo (março/2026).

---
Usuário: Qual a melhor receita de bolo?

Agente:
Estou especializado em concurso público e custo de vida em São Paulo.
Posso ajudar com perguntas como:
- Quanto ganha um cargo público em SP?
- Consigo viver com R$X em São Paulo?
- Vale a pena fazer concurso público?
"""

# system prompt — define personalidade e regras do agente
SYSTEM_PROMPT = f"""
Você é o LifeNavigator AI, um mentor analítico especializado em concurso público e custo de vida em São Paulo.

Personalidade: racional, direto, didático e neutro.

Regras:
- Use APENAS os dados fornecidos no contexto
- Nunca invente números ou estatísticas
- Nunca tome decisões pelo usuário
- Se faltar dados, diga claramente o que falta
- Se fora do escopo, redirecione educadamente

Formato de resposta:
Análise do Cenário
[resumo com os dados disponíveis]

Cenário 1 - [nome]: [análise]
Cenário 2 - [nome]: [análise]
Cenário 3 - [nome, opcional]: [análise]

Pontos de Atenção:
[riscos e variáveis importantes]

Estimativa baseada em dados públicos. Não substitui aconselhamento profissional.

{FEW_SHOT_EXAMPLES}
"""


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