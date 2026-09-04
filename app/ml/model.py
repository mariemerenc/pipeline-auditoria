from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score, precision_score, recall_score

from app.ml.features import construir

CONTAMINACAO = 0.08  # proporção esperada de anomalias no histórico


class Detector:
    """isolation forest sobre features temporais de contratação pública.

    obs: a coluna `anomalia` do CSV nunca entra no treino, é usada apenas para medir precisão e recall depois.
    """

    def __init__(self) -> None:
        self.modelo: IsolationForest | None = None
        self.historico: pd.DataFrame | None = None
        self.metricas: dict[str, float] = {}

    def treinar(self, csv: Path | str) -> dict[str, float]:
        self.historico = pd.read_csv(csv)
        features = construir(self.historico)

        self.modelo = IsolationForest(contamination=CONTAMINACAO, random_state=42).fit(features)

        previsto = (self.modelo.predict(features) == -1).astype(int)
        real = self.historico["anomalia"].to_numpy()

        self.metricas = {
            "precisao": round(precision_score(real, previsto, zero_division=0), 3),
            "recall": round(recall_score(real, previsto, zero_division=0), 3),
            "f1": round(f1_score(real, previsto, zero_division=0), 3),
            "linhas": len(self.historico),
            "anomalias_conhecidas": int(real.sum()),
        }
        
        return self.metricas

    def avaliar(self, fornecedor: str, mes: int, valor: float) -> dict:
        if self.modelo is None or self.historico is None:
            raise RuntimeError("Detector não treinado.")

        nova = pd.DataFrame([{"fornecedor": fornecedor, "mes": mes, "valor": valor, "anomalia": 0}])
        combinado = pd.concat([self.historico, nova], ignore_index=True)
        features = construir(combinado).iloc[[-1]]

        score = float(self.modelo.decision_function(features)[0])

        return {
            "fornecedor": fornecedor,
            "mes": mes,
            "valor": valor,
            "score": round(score, 4),
            "anomalo": bool(self.modelo.predict(features)[0] == -1),
            # devolvidas para tornar o alerta auditável"
            "features": {k: round(float(v), 3) for k, v in features.iloc[0].items()},
        }


detector = Detector()