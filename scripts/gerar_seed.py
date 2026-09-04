import random
from pathlib import Path

import pandas as pd

random.seed(42) 

FORNECEDORES = {
    "Construtora Fachada": 120_000,
    "Limpeza Lambda": 45_000,
    "Indústrias Panacea": 200_000,
    "TI Alfa": 85_000,
    "Obras Beta": 310_000,
    "JojaMart Alimentos": 60_000,
    "Transportes Supercontinent": 95_000,
    "Papelaria Gama": 12_000,
    "Engenharia Delta": 260_000,
    "Manutencao Epsilon": 70_000,
    "Uniformes Zeta": 33_000,
    "Equipe Medicos Psi": 175_000,
}

SAZONAL = {
    1: 0.7,
    2: 0.8,
    3: 0.9,
    4: 1.0,
    5: 1.0,
    6: 1.1,
    7: 1.0,
    8: 1.0,
    9: 1.1,
    10: 1.2,
    11: 1.4,
    12: 1.8,
}

#valores mto acima da mediana do proprio fornecedor
SUPERFATURADOS = [("Construtora Fachada", 5, 11), ("TI Alfa", 8, 9), ("JojaMart Alimentos", 3, 13),] 

#fornecedor sem historico estreando c contrato alto
ESTREANTES = [("Consultoria Aurora", 6, 480_000.0), ("Locacao Meridiano", 9, 390_000.0), ("Eventos Boreal", 11, 520_000.0),] 

#varios contratos pequenos no msm mes p fugir da licitaçao
FRACIONAMENTOS = [("Papelaria Gama", 7), ("Manutencao Epsilon", 10)] 


def gerar() -> pd.DataFrame:
    linhas = []

    for fornecedor, base in FORNECEDORES.items():
        for mes in range(1, 13):
            # 1 ou 2 contratos por mes
            for _ in range(random.choices([1, 2], weights=[0.75, 0.25])[0]):
                valor = base * SAZONAL[mes] * random.uniform(0.88, 1.12)
                linhas.append(
                    {
                        "fornecedor": fornecedor,
                        "mes": mes,
                        "valor": round(valor, 2),
                        "anomalia": 0,
                    }
                )

    df = pd.DataFrame(linhas)

    for fornecedor, mes, multiplicador in SUPERFATURADOS:
        i = df[(df.fornecedor == fornecedor) & (df.mes == mes)].index[0]
        df.loc[i, ["valor", "anomalia"]] = [
            round(df.loc[i, "valor"] * multiplicador, 2),
            1,
        ]

    for fornecedor, mes, valor in ESTREANTES:
        df.loc[len(df)] = {
            "fornecedor": fornecedor,
            "mes": mes,
            "valor": valor,
            "anomalia": 1,
        }

    for fornecedor, mes in FRACIONAMENTOS:
        for _ in range(5):
            df.loc[len(df)] = {
                "fornecedor": fornecedor,
                "mes": mes,
                "valor": round(FORNECEDORES[fornecedor] * 0.24, 2),
                "anomalia": 1,
            }


    return df.sort_values(["fornecedor", "mes"]).reset_index(drop=True)


if __name__ == "__main__":
    df = gerar()
    destino = Path("data/seed/historico_financeiro.csv")
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False)
    print(f"{len(df)} linhas | {int(df.anomalia.sum())} anômalas -> {destino}")