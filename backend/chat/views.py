from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.guardrails import verificar_mensagem
from .services.intent_service import identificar_intencao
from .services.data_service import (
    buscar_salario_por_cargo,
    buscar_salario_por_departamento,
    calcular_custo_mensal,
    calcular_sobra_mensal,
    listar_maiores_salarios,
)
from .services.prompt_builder import montar_prompt
from .services.groq_service import gerar_resposta
from .models import PerfilUsuario, Conversa, Mensagem
import uuid



class ChatView(APIView):
    def post(self, request):
        
        mensagem = request.data.get("mensagem", "").strip()
        session_id = request.data.get("session_id") or str(uuid.uuid4())

        # valida se veio mensagem
        if not mensagem:
            return Response(
                {"erro": "Mensagem não pode ser vazia."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. guardrails — mensagem é segura?
        check = verificar_mensagem(mensagem)
        if not check["permitido"]:
            return Response({"resposta": check["resposta"]})

        # 2. identifica intenção
        intencao = identificar_intencao(mensagem)

        # 3. busca dados reais com base nas ações identificadas
        dados = {}
        acoes = intencao.get("acoes", [])

        if "buscar_salario_por_cargo" in acoes and intencao.get("cargo"):
            dados["salario"] = buscar_salario_por_cargo(intencao["cargo"])

        if "buscar_salario_por_departamento" in acoes and intencao.get("departamento"):
            dados["departamento"] = buscar_salario_por_departamento(intencao["departamento"])

        if "listar_maiores_salarios" in acoes:
            dados["maiores_salarios"] = listar_maiores_salarios()

        if "calcular_custo_mensal" in acoes:
            dados["custo_mensal"] = calcular_custo_mensal(
                intencao.get("perfil", "solteiro")
            )

        if "calcular_sobra_mensal" in acoes and intencao.get("salario_atual"):
            dados["sobra"] = calcular_sobra_mensal(
                intencao["salario_atual"],
                intencao.get("perfil", "solteiro")
            )

        # 4. busca histórico da conversa
        historico = _buscar_historico(session_id)

        # 5. monta prompt com dados reais
        messages = montar_prompt(mensagem, dados, historico)

        # 6. gera resposta com Groq
        resposta = gerar_resposta(messages)

        # 7. salva no banco
        _salvar_mensagem(session_id, mensagem, resposta, intencao, dados)

        return Response({
            "resposta": resposta,
            "dados_usados": dados,
        })


def _buscar_historico(session_id: str) -> list[dict]:
    try:
        # se não veio session_id válido, retorna vazio
        if not session_id:
            return []

        perfil = PerfilUsuario.objects.get(session_id=session_id)
        conversa = perfil.conversas.last()
        if not conversa:
            return []

        mensagens = conversa.mensagens.order_by("-criada_em")[:5]
        return [
            {"role": m.role, "content": m.conteudo}
            for m in reversed(mensagens)
        ]
    except PerfilUsuario.DoesNotExist:
        return []


def _salvar_mensagem(session_id, mensagem, resposta, intencao, dados):
    try:
        # se não veio session_id válido, não salva
        if not session_id:
            return

        perfil, _ = PerfilUsuario.objects.get_or_create(
            session_id=session_id,
            defaults={
                "cargo": intencao.get("cargo", ""),
                "salario_atual": intencao.get("salario_atual"),
            }
        )

        conversa, _ = Conversa.objects.get_or_create(perfil=perfil)

        Mensagem.objects.create(
            conversa=conversa,
            role="user",
            conteudo=mensagem,
            intencao=intencao.get("tipo", ""),
            dados_usados=dados,
        )

        Mensagem.objects.create(
            conversa=conversa,
            role="assistant",
            conteudo=resposta,
        )

    except Exception as e:
        print(f"Erro ao salvar mensagem: {e}")