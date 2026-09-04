import os

import httpx
from fastmcp import FastMCP

mcp = FastMCP("auditoria")

API = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = 30.0


@mcp.tool
async def buscar_documentos(consulta: str, limite: int = 5) -> list[dict]:
    """busca trechos de documentos orçamentários e contratos públicos.
    combina busca textual e semântica, fundindo os dois rankings. 
    use para encontrar cláusulas, fornecedores, valores ou qualquer
    conteúdo dos documentos indexados.

    os trechos retornados já estão anonimizados. nomes e CPFs aparecem como
    marcadores do tipo [PESSOA_1] e [CPF_1].

    Args:
        consulta: o que procurar, em linguagem natural
        limite: quantos trechos retornar (padrão 5)
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as cliente:
        r = await cliente.get(f"{API}/busca", params={"q": consulta, "limite": limite})
        r.raise_for_status()

        return r.json()["resultados"]


@mcp.tool
async def detalhar_documento(documento_id: str) -> dict:
    """retorna os dados de um documento, incluindo as entidades extraídas.

    as entidades vêm agrupadas por tipo: LEGISLACAO (leis, decretos, artigos),
    JURISPRUDENCIA (acórdãos do TCU, súmulas) e VALOR (valores monetários).
    use depois de `buscar_documentos`, com o `documento_id` de um resultado,
    para saber em que normas o documento se fundamenta e quais valores cita.

    Args:
        documento_id: o UUID do documento
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as cliente:
        r = await cliente.get(f"{API}/documentos/{documento_id}")

        if r.status_code == 404:
            return {"[erro]": f"documento {documento_id} não encontrado"}
        
        r.raise_for_status()

        return r.json()


@mcp.tool
async def avaliar_anomalia(fornecedor: str, mes: int, valor: float) -> dict:
    """avalia se um contrato foge do padrão histórico daquele fornecedor.

    compara o valor com a mediana histórica do fornecedor, a variação diante 
    do contrato anterior e a frequência de contratos no mês. retorna o score,
    o veredito e as features que o justificam.

    args:
        fornecedor: razão social como aparece no histórico.
        mes: mês do contrato, de 1 a 12
        valor: valor do contrato em reais
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as cliente:
        r = await cliente.post(
            f"{API}/anomalias/avaliar",
            json={"fornecedor": fornecedor, "mes": mes, "valor": valor},
        )
        
        r.raise_for_status()

        return r.json()


if __name__ == "__main__":
    mcp.run()
