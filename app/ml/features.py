import pandas as pd

COLUNAS = ["desvio_fornecedor", "variacao_mensal", "freq_mes"]


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """features temporais e relativas ao fornecedor.

    cada coluna captura um padrão distinto:

    - desvio_fornecedor: superfaturamento (valor acima da mediana do próprio fornecedor)
    - variacao_mensal:   mudança abrupta de comportamento
    - freq_mes:          fracionamento de despesa (anomalia coletiva)
    """
    f = pd.DataFrame(index=df.index)

    mediana = df.groupby("fornecedor")["valor"].transform("median")
    f["desvio_fornecedor"] = df["valor"] / mediana

    # qnd o fornecedor tem dois contratos no msm mês, o shift compara com o outro contrato do mês e não com o mês anterior
    anterior = df.groupby("fornecedor")["valor"].transform(lambda s: s.shift(1).fillna(s.median()))

    f["variacao_mensal"] = (df["valor"] - anterior) / anterior.replace(0, 1)

    f["freq_mes"] = df.groupby(["fornecedor", "mes"])["valor"].transform("size")

    return f[COLUNAS]