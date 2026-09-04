import json
import time

import httpx
from anthropic import (
    Anthropic,
    APIConnectionError,
    APIStatusError,
    RateLimitError,
)

from app.config import settings
from app.llm.usage import Consumo

cliente = Anthropic(api_key=settings.anthropic_api_key)
API = "http://localhost:8000"
MAX_TENTATIVAS = 4

SISTEMA = """Você é um assistente de auditoria de contratos públicos.

REGRAS:
- Comece SEMPRE chamando `buscar_documentos`. Nunca peça esclarecimento antes
  de ter buscado: a base é pequena e a busca aceita linguagem natural.
- Se a pergunta envolver leis, acórdãos ou valores, chame em seguida
  `detalhar_documento` com o `documento_id` do resultado da busca.
- Responda apenas com o que veio das ferramentas. Se não encontrar, diga que
  não encontrou — nunca invente valores, leis ou números de contrato.

Os documentos estão anonimizados: [PESSOA_1] e [CPF_1] são marcadores de dados
pessoais removidos, não valores reais."""

TOOLS = [
    {
        "name": "buscar_documentos",
        "description": (
            "busca trechos de documentos orçamentários e contratos públicos por relevância textual e semântica."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "consulta": {"type": "string", "description": "o que procurar"},
                "limite": {"type": "integer", "description": "quantos trechos"},
            },
            "required": ["consulta"],
        },
    },
    {
        "name": "detalhar_documento",
        "description": (
            "retorna um documento e as entidades extraídas dele: LEGISLACAO, JURISPRUDENCIA e VALOR."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"documento_id": {"type": "string"}},
            "required": ["documento_id"],
        },
    },
    {
        "name": "avaliar_anomalia",
        "description": (
            "avalia se um contrato foge do padrão histórico do fornecedor. devolve score, veredito e as features que o justificam."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "fornecedor": {"type": "string"},
                "mes": {"type": "integer", "description": "1 a 12"},
                "valor": {"type": "number", "description": "valor em reais"},
            },
            "required": ["fornecedor", "mes", "valor"],
        },
    },
]


def _executar(nome: str, args: dict) -> str:
    """executa a ferramenta chamando a própria API da pipeline"""
    with httpx.Client(timeout=30.0) as http:
        if nome == "buscar_documentos":
            r = http.get(
                f"{API}/busca",
                params={"q": args["consulta"], "limite": args.get("limite", 5)},
            )
        elif nome == "detalhar_documento":
            r = http.get(f"{API}/documentos/{args['documento_id']}")
        elif nome == "avaliar_anomalia":
            r = http.post(f"{API}/anomalias/avaliar", json=args)
        else:
            return json.dumps({"erro": f"ferramenta desconhecida: {nome}"})
        r.raise_for_status()
        return json.dumps(r.json(), ensure_ascii=False)


def _com_retry(chamada):
    """backoff exponencial. repete o que é transitório, desiste do que não é"""
    ultimo_erro: Exception | None = None
    for tentativa in range(MAX_TENTATIVAS):
        try:
            return chamada()
        except RateLimitError as e: # transitório
            ultimo_erro = e
        except APIStatusError as e:
            if e.status_code < 500: # 400, 401, 404 n adianta repetir
                raise
            ultimo_erro = e
        except APIConnectionError as e: # falha de rede
            ultimo_erro = e
        if tentativa < MAX_TENTATIVAS - 1:
            time.sleep(2**tentativa) # 1s, 2s, 4s
    raise ultimo_erro


def perguntar(pergunta: str) -> dict:
    consumo = Consumo(modelo=settings.llm_model)
    mensagens = [{"role": "user", "content": pergunta}]

    while True:
        resposta = _com_retry(
            lambda: cliente.messages.create(
                model=settings.llm_model,
                max_tokens=4096,
                system=SISTEMA,
                tools=TOOLS,
                messages=mensagens,
            )
        )
        consumo.somar(resposta.usage)

        if resposta.stop_reason != "tool_use":
            texto = "".join(b.text for b in resposta.content if b.type == "text")
            return {"resposta": texto, "consumo": consumo.resumo()}

        mensagens.append({"role": "assistant", "content": resposta.content})
        # tool_result vão numa unica msg de usuário
        mensagens.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": bloco.id,
                        "content": _executar(bloco.name, bloco.input),
                    }
                    for bloco in resposta.content
                    if bloco.type == "tool_use"
                ],
            }
        )
