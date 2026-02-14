from dataclasses import dataclass, asdict
from typing import List, Union, Dict, Any
import json
from entidades.estrategias_descritivas.base import BaseEstrategiaDescritiva, CondicaoEntrada, StopConfig, AlvoConfig, CondicaoSaida

@dataclass
class DoubleEmaBreakout(BaseEstrategiaDescritiva):

    # @classmethod
    # def from_genome(cls, genome):
    #     return cls(
    #         nome="individuo",
    #         tipo="long",
    #         condicoes_entrada=[
    #             CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": genome["param_ema_curta"]}),
    #             CondicaoEntrada(tipo="fechamento_acima_ema", parametros={"periodo": genome["param_ema_longa"]}),
    #             CondicaoEntrada(tipo="rompe_maxima_anterior", parametros={})
    #         ],
    #         stop=StopConfig(tipo="minima_das_ultimas", parametros={"quantidade": genome["param_stop"]}),
    #         alvo=AlvoConfig(tipo="rr", parametros={"multiplicador": genome["param_rr"]})
    #     )
    # DoubleEmaBreakout.from_genome = from_genome

    @staticmethod
    def from_json(path: str) -> 'DoubleEmaBreakout':
        with open(path, 'r') as f:
            data = json.load(f)
            params = data.get("params_default", {})

            def resolve(valor):
                if isinstance(valor, str) and valor.startswith("param_"):
                    return params.get(valor, valor)
                return valor

            condicoes = [
                CondicaoEntrada(
                    tipo=ce['tipo'],
                    parametros={k: resolve(v) for k, v in ce.get('parametros', {'periodo': ce.get('periodo')}).items()}
                ) for ce in data['condicoes_entrada']
            ]

            stop = StopConfig(
                tipo=data['stop']['tipo'],
                parametros={k: resolve(v) for k, v in data['stop'].items() if k != 'tipo'}
            )

            alvo = AlvoConfig(
                tipo=data['alvo']['tipo'],
                parametros={k: resolve(v) for k, v in data['alvo'].items() if k != 'tipo'}
            )

            condicoes_saida = [
                CondicaoSaida(
                    tipo=cs['tipo'],
                    parametros={k: resolve(v) for k, v in cs.get('parametros', {}).items()}
                ) for cs in data.get('condicoes_saida', [])
            ]
            return DoubleEmaBreakout(
                nome=data['nome'],
                tipo=data['tipo'],
                condicoes_entrada=condicoes,
                condicoes_saida=condicoes_saida,
                stop=stop,
                alvo=alvo
            )

    def descricao(self) -> str:
        """Retorna uma descrição legível da estratégia."""
        p1 = self.condicoes_entrada[0].parametros.get("periodo")
        p2 = self.condicoes_entrada[1].parametros.get("periodo")
        q_stop = self.stop.parametros.get("quantidade")
        rr = self.alvo.parametros.get("multiplicador")

        return (
            f"Breakout com EMA {p1} e {p2}, stop na mínima das últimas {q_stop} velas, "
            f"e alvo com RR de {rr:.2f}."
        )

    def parametros_principais(self) -> Dict[str, Any]:
        """Retorna os parâmetros principais da estratégia para logs ou identificação."""
        return {
            "ema_curta": self.condicoes_entrada[0].parametros.get("periodo"),
            "ema_longa": self.condicoes_entrada[1].parametros.get("periodo"),
            "stop": self.stop.parametros.get("quantidade"),
            "rr": self.alvo.parametros.get("multiplicador")
        }

    def id_curto(self) -> str:
        """Gera um identificador simples da estratégia com base nos parâmetros."""
        p = self.parametros_principais()
        return f"ema_{p['ema_curta']}_{p['ema_longa']}_stop_{p['stop']}_rr_{p['rr']}"