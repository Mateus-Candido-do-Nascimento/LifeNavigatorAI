import pandas as pd
from functools import lru_cache

# ─── CARREGAR DATASETS ─────────────────────────────────────

@lru_cache(maxsize=2)
def carregar_datasets():
    """
    Carrega os dois CSVs em memória apenas UMA vez.
    
    lru_cache = "guarda o resultado na memória"
    Sem isso, toda requisição leria o arquivo do disco novamente — muito lento.
    maxsize=2 = guarda cache de até 2 chamadas diferentes
    """
    return {
        "salarios": pd.read_csv("datasets/salarios_limpo.csv"),
        "custo_vida": pd.read_csv("datasets/custo_vida_sp_numbeo.csv"),
    }


# ─── SALÁRIOS ──────────────────────────────────────────────

def buscar_salario_por_cargo(cargo: str) -> dict:
    """
    Recebe o nome de um cargo e retorna estatísticas de salário.
    
    Exemplo:
        buscar_salario_por_cargo("PROFESSOR")
        → { mediana: 4200, minimo: 2800, maximo: 9500, amostras: 342 }
    
    O str.contains() busca por correspondência parcial:
        "PROF" também encontra "PROFESSOR DE ENSINO FUNDAMENTAL"
    
    case=False → ignora maiúsculas/minúsculas
    na=False   → ignora células vazias sem dar erro
    """
    df = carregar_datasets()["salarios"]

    # filtra apenas as linhas onde o cargo contém o termo buscado
    filtro = df["POSITION"].str.contains(cargo, case=False, na=False)
    resultado = df[filtro]["MONTH_TOTAL"]  # pega só a coluna de salário
    resultado = resultado[resultado > 0]  # ← filtro para nao deixar que valores nulos passem
    # se não achou nenhum cargo com esse nome, avisa
    if resultado.empty:
        return {"disponivel": False, "cargo": cargo}

    # retorna as estatísticas do salário bruto
    return {
        "disponivel": True,
        "cargo": cargo,
        "mediana": round(resultado.median(), 2),  # valor do meio — menos afetado por outliers
        "minimo": round(resultado.min(), 2),
        "maximo": round(resultado.max(), 2),
        "media": round(resultado.mean(), 2),       # média — pode ser distorcida por salários muito altos
        "amostras": int(len(resultado)),            # quantos registros foram encontrados
    }


def buscar_salario_por_departamento(departamento: str) -> dict:
    """
    Recebe o nome de um departamento e retorna salários e cargos.
    
    Exemplo:
        buscar_salario_por_departamento("SAUDE")
        → { salario_mediano: 5800, cargos: {"MEDICO": 45, "ENFERMEIRO": 120} }
    
    Útil para perguntas como:
        "Quanto ganha quem trabalha na Secretaria de Saúde de SP?"
    """
    df = carregar_datasets()["salarios"]

    # filtra pelo nome do departamento
    filtro = df["DEPARTMENT"].str.contains(departamento, case=False, na=False)
    resultado = df[filtro]

    if resultado.empty:
        return {"disponivel": False, "departamento": departamento}

    return {
        "disponivel": True,
        "departamento": departamento,
        "salario_mediano": round(resultado["MONTH_TOTAL"].median(), 2),
        "salario_liquido_mediano": round(resultado["NET_TOTAL"].median(), 2),  # já com descontos
        "total_funcionarios": int(len(resultado)),
        # top 5 cargos mais comuns nesse departamento
        "cargos": resultado["POSITION"].value_counts().head(5).to_dict(),
    }


def listar_maiores_salarios(top: int = 10) -> dict:
    """
    Retorna o ranking dos cargos com maiores salários medianos.
    
    Exemplo:
        listar_maiores_salarios(top=5)
        → { ranking: {"DELEGADO": 18500, "PROCURADOR": 16200, ...} }
    
    Usa mediana (não média) para evitar distorção por valores extremos.
    Útil para: "Quais os cargos públicos que mais pagam em SP?"
    """
    df = carregar_datasets()["salarios"]

    ranking = (
        df.groupby("POSITION")["MONTH_TOTAL"]  # agrupa por cargo
        .median()                               # calcula a mediana de cada cargo
        .sort_values(ascending=False)           # ordena do maior pro menor
        .head(top)                              # pega só os top N
        .round(2)
        .to_dict()                              # converte pra dicionário
    )

    return {"disponivel": True, "ranking": ranking}


# ─── CUSTO DE VIDA ─────────────────────────────────────────

def buscar_custo_vida(categoria: str = None) -> dict:
    """
    Retorna itens de custo de vida de SP, opcionalmente filtrado por categoria.
    
    Categorias disponíveis:
        alimentacao, mercado, transporte, utilities,
        lazer, educacao, vestuario, aluguel, imovel, referencia
    
    Exemplos:
        buscar_custo_vida()                    → todos os itens
        buscar_custo_vida("aluguel")           → só aluguéis
        buscar_custo_vida("transporte")        → só transporte
    """
    df = carregar_datasets()["custo_vida"]

    # se passou uma categoria, filtra só ela
    if categoria:
        df = df[df["categoria"] == categoria]

    if df.empty:
        return {"disponivel": False}

    # retorna lista de dicionários com item, valor e categoria
    return {
        "disponivel": True,
        "itens": df[["item", "valor_brl", "categoria"]].to_dict(orient="records"),
    }


def calcular_custo_mensal(perfil: str = "solteiro") -> dict:
    """
    Estima o custo total mensal em SP para um perfil de vida.
    
    Perfis disponíveis:
        'solteiro' → baseado na estimativa Numbeo para 1 pessoa
        'familia'  → baseado na estimativa Numbeo para família de 4
    
    Os valores do Numbeo já incluem:
        alimentação + transporte + lazer + utilidades básicas
        MAS NÃO incluem aluguel (calculado separado)
    
    Por isso retornamos:
        total_sem_aluguel          → só o custo de vida básico
        total_com_aluguel_centro   → custo + aluguel no centro
        total_com_aluguel_fora_centro → custo + aluguel fora do centro (mais barato)
    
    Útil para:
        "Consigo viver em SP com R$5.000?"
        "Quanto preciso ganhar pra morar bem em SP?"
    """
    custos = {
        "solteiro": {
            "estimativa_numbeo": 3557.00,       # custo de vida sem aluguel (Numbeo)
            "aluguel_1q_fora_centro": 2342.23,   # aluguel 1 quarto fora do centro
            "transporte_mensal": 246.50,
            "utilities": 436.16,                 # luz, água, gás
            "internet": 107.11,
            "celular": 84.75,
            "total_sem_aluguel": 3557.00,
            # custo total = custo de vida + aluguel
            "total_com_aluguel_fora_centro": round(3557.00 + 2342.23, 2),
            "total_com_aluguel_centro": round(3557.00 + 3469.11, 2),
        },
        "familia": {
            "estimativa_numbeo": 13152.10,       # custo de vida família de 4 sem aluguel
            "aluguel_3q_fora_centro": 4943.86,
            "transporte_mensal": 246.50 * 2,     # dois adultos
            "total_sem_aluguel": 13152.10,
            "total_com_aluguel_fora_centro": round(13152.10 + 4943.86, 2),
            "total_com_aluguel_centro": round(13152.10 + 7467.50, 2),
        },
    }

    # se o perfil não existir, usa solteiro como padrão
    dados = custos.get(perfil, custos["solteiro"])
    return {"disponivel": True, "perfil": perfil, "cidade": "São Paulo", **dados}
    # ** "desempacota" o dicionário — é como copiar todas as chaves


def calcular_sobra_mensal(salario_liquido: float, perfil: str = "solteiro") -> dict:
    """
    Calcula quanto sobra por mês dado um salário líquido.
    
    Exemplo:
        calcular_sobra_mensal(5000, "solteiro")
        → {
            sobra_sem_aluguel: 1443.00,         (5000 - 3557)
            sobra_com_aluguel_fora_centro: -899.23,  (5000 - 5899.23)
            vive_confortavelmente: False
          }
    
    vive_confortavelmente = True se sobrar mais de R$500 após todas as despesas
    
    Útil para:
        "Consigo viver com R$5k em SP?"
        "Vale a pena aceitar emprego público que paga R$8k em SP?"
    """
    custo = calcular_custo_mensal(perfil)

    sobra_sem_aluguel = round(salario_liquido - custo["total_sem_aluguel"], 2)
    sobra_com_aluguel = round(salario_liquido - custo["total_com_aluguel_fora_centro"], 2)

    return {
        "disponivel": True,
        "salario_liquido": salario_liquido,
        "perfil": perfil,
        "sobra_sem_aluguel": sobra_sem_aluguel,
        "sobra_com_aluguel_fora_centro": sobra_com_aluguel,
        # considera confortável se sobrar pelo menos R$500 após tudo
        "vive_confortavelmente": sobra_com_aluguel > 500,
    }