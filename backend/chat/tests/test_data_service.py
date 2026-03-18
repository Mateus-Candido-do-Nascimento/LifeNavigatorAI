from django.test import TestCase
from chat.services.data_service import (
    buscar_salario_por_cargo,
    buscar_salario_por_departamento,
    calcular_custo_mensal,
    calcular_sobra_mensal,
    listar_maiores_salarios,
)


class TestBuscarSalarioPorCargo(TestCase):
    # testa a função que busca salários por cargo no dataset

    def test_cargo_existente_retorna_disponivel(self):
        # PROFESSOR existe no dataset — deve retornar disponivel=True
        resultado = buscar_salario_por_cargo("PROFESSOR")
        self.assertTrue(resultado["disponivel"])

    def test_cargo_existente_retorna_mediana_positiva(self):
        # mediana de salário não pode ser zero ou negativa
        resultado = buscar_salario_por_cargo("PROFESSOR")
        self.assertGreater(resultado["mediana"], 0)

    def test_cargo_existente_retorna_amostras_suficientes(self):
        # precisa de pelo menos 10 registros pra mediana ser confiável
        resultado = buscar_salario_por_cargo("PROFESSOR")
        self.assertGreater(resultado["amostras"], 10)

    def test_cargo_existente_retorna_minimo_positivo(self):
        # salário mínimo não pode ser zero — dataset já foi tratado
        resultado = buscar_salario_por_cargo("PROFESSOR")
        self.assertGreater(resultado["minimo"], 0)

    def test_cargo_inexistente_retorna_indisponivel(self):
        # cargo que não existe no dataset deve retornar disponivel=False
        resultado = buscar_salario_por_cargo("CARGO_QUE_NAO_EXISTE_XYZ")
        self.assertFalse(resultado["disponivel"])

    def test_cargo_case_insensitive(self):
        # "professor" e "PROFESSOR" devem retornar o mesmo resultado
        resultado_maiusculo = buscar_salario_por_cargo("PROFESSOR")
        resultado_minusculo = buscar_salario_por_cargo("professor")
        self.assertEqual(resultado_maiusculo["disponivel"], resultado_minusculo["disponivel"])

    def test_medico_retorna_salario_maior_que_professor(self):
        # médico público ganha mais que professor — validação de senso comum
        professor = buscar_salario_por_cargo("PROFESSOR")
        medico = buscar_salario_por_cargo("MEDICO")
        if medico["disponivel"] and professor["disponivel"]:
            self.assertGreater(medico["mediana"], professor["mediana"])


class TestBuscarSalarioPorDepartamento(TestCase):
    # testa a função que busca salários por departamento

    def test_departamento_existente_retorna_disponivel(self):
        # SAUDE existe no dataset — deve retornar disponivel=True
        resultado = buscar_salario_por_departamento("SAUDE")
        self.assertTrue(resultado["disponivel"])

    def test_departamento_retorna_salario_positivo(self):
        # salário mediano do departamento deve ser positivo
        resultado = buscar_salario_por_departamento("SAUDE")
        self.assertGreater(resultado["salario_mediano"], 0)

    def test_departamento_retorna_salario_liquido(self):
        # resultado deve conter salário líquido calculado
        resultado = buscar_salario_por_departamento("SAUDE")
        self.assertIn("salario_liquido_mediano", resultado)
        self.assertGreater(resultado["salario_liquido_mediano"], 0)

    def test_salario_liquido_menor_que_bruto(self):
        # líquido sempre menor que bruto por causa dos descontos
        resultado = buscar_salario_por_departamento("SAUDE")
        self.assertLess(
            resultado["salario_liquido_mediano"],
            resultado["salario_mediano"]
        )

    def test_departamento_inexistente_retorna_indisponivel(self):
        # departamento que não existe deve retornar disponivel=False
        resultado = buscar_salario_por_departamento("DEPARTAMENTO_XYZ_INEXISTENTE")
        self.assertFalse(resultado["disponivel"])


class TestCalcularCustoMensal(TestCase):
    # testa o cálculo de custo de vida mensal em SP

    def test_solteiro_retorna_disponivel(self):
        # perfil solteiro deve retornar dados disponíveis
        resultado = calcular_custo_mensal("solteiro")
        self.assertTrue(resultado["disponivel"])

    def test_familia_retorna_disponivel(self):
        # perfil familia deve retornar dados disponíveis
        resultado = calcular_custo_mensal("familia")
        self.assertTrue(resultado["disponivel"])

    def test_solteiro_retorna_valores_positivos(self):
        # todos os totais devem ser positivos
        resultado = calcular_custo_mensal("solteiro")
        self.assertGreater(resultado["total_sem_aluguel"], 0)
        self.assertGreater(resultado["total_com_aluguel_fora_centro"], 0)
        self.assertGreater(resultado["total_com_aluguel_centro"], 0)

    def test_custo_com_aluguel_maior_que_sem_aluguel(self):
        # adicionar aluguel sempre aumenta o custo total
        resultado = calcular_custo_mensal("solteiro")
        self.assertGreater(
            resultado["total_com_aluguel_fora_centro"],
            resultado["total_sem_aluguel"]
        )

    def test_aluguel_centro_maior_que_fora_centro(self):
        # morar no centro de SP é mais caro que fora do centro
        resultado = calcular_custo_mensal("solteiro")
        self.assertGreater(
            resultado["total_com_aluguel_centro"],
            resultado["total_com_aluguel_fora_centro"]
        )

    def test_familia_custa_mais_que_solteiro(self):
        # família tem mais gastos que solteiro
        solteiro = calcular_custo_mensal("solteiro")
        familia = calcular_custo_mensal("familia")
        self.assertGreater(
            familia["total_sem_aluguel"],
            solteiro["total_sem_aluguel"]
        )


class TestCalcularSobraMensal(TestCase):
    # testa o cálculo de sobra mensal após descontar custo de vida

    def test_salario_alto_vive_confortavelmente(self):
        # R$10.000 em SP — deve viver confortavelmente
        resultado = calcular_sobra_mensal(10000, "solteiro")
        self.assertTrue(resultado["vive_confortavelmente"])

    def test_salario_baixo_nao_vive_confortavelmente(self):
        # R$1.500 em SP — não consegue viver confortavelmente
        resultado = calcular_sobra_mensal(1500, "solteiro")
        self.assertFalse(resultado["vive_confortavelmente"])

    def test_sobra_sem_aluguel_maior_que_com_aluguel(self):
        # sem aluguel sempre sobra mais
        resultado = calcular_sobra_mensal(6000, "solteiro")
        self.assertGreater(
            resultado["sobra_sem_aluguel"],
            resultado["sobra_com_aluguel_fora_centro"]
        )

    def test_retorna_salario_informado(self):
        # o salário informado deve ser retornado no resultado
        resultado = calcular_sobra_mensal(5000, "solteiro")
        self.assertEqual(resultado["salario_liquido"], 5000)

    def test_retorna_perfil_informado(self):
        # o perfil informado deve ser retornado no resultado
        resultado = calcular_sobra_mensal(5000, "familia")
        self.assertEqual(resultado["perfil"], "familia")


class TestListarMaioresSalarios(TestCase):
    # testa o ranking dos maiores salários do setor público SP

    def test_retorna_lista_nao_vazia(self):
        # deve retornar pelo menos um cargo
        resultado = listar_maiores_salarios()
        self.assertGreater(len(resultado), 0)

    def test_retorna_top_10_por_padrao(self):
        # ranking padrão tem no máximo 10 cargos
        resultado = listar_maiores_salarios(top=10)
        self.assertLessEqual(len(resultado["ranking"]), 10)

    def test_primeiro_salario_maior_que_ultimo(self):
        # primeiro do ranking deve ter salário maior ou igual ao último
        resultado = listar_maiores_salarios(top=5)
        ranking = list(resultado["ranking"].values())
        if len(ranking) >= 2:
            self.assertGreaterEqual(ranking[0], ranking[-1])