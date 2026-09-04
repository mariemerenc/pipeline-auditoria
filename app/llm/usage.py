from dataclasses import dataclass

PRECOS = { 
    "claude-opus-5": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
} # dolar por mi de tokens ~ (entrada, saida)


@dataclass
class Consumo:
    modelo: str
    entrada: int = 0
    saida: int = 0
    chamadas: int = 0

    def somar(self, usage) -> None:
        self.entrada += usage.input_tokens
        self.saida += usage.output_tokens
        self.chamadas += 1

    @property
    def custo_usd(self) -> float:
        preco_entrada, preco_saida = PRECOS.get(self.modelo, (0.0, 0.0))
        return (
            self.entrada / 1_000_000 * preco_entrada
            + self.saida / 1_000_000 * preco_saida
        )

    def resumo(self) -> dict:
        return {
            "modelo": self.modelo,
            "chamadas": self.chamadas,
            "tokens_entrada": self.entrada,
            "tokens_saida": self.saida,
            "custo_usd": round(self.custo_usd, 6),
        }
