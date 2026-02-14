from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
import json

# Condições comuns a todas as estratégias
@dataclass
class CondicaoEntrada:
    tipo: str
    parametros: Dict[str, Any] = None

@dataclass
class CondicaoSaida:
    tipo: str
    parametros: Dict[str, Any] = None

@dataclass
class StopConfig:
    tipo: str
    parametros: Dict[str, Any] = None

@dataclass
class AlvoConfig:
    tipo: str
    parametros: Dict[str, Any] = None

# Classe base para qualquer estratégia descritiva
@dataclass
class BaseEstrategiaDescritiva:
    nome: str
    tipo: str  # "long" ou "short"
    condicoes_entrada: List[CondicaoEntrada]
    condicoes_saida: List[CondicaoSaida] = field(default_factory=list)
    stop: Optional[StopConfig] = None
    alvo: Optional[AlvoConfig] = None

    def to_json(self, path):
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def from_json(cls, path):
        with open(path, 'r') as f:
            data = json.load(f)
            params = data.get("params_default", {})

            def resolve(valor):
                if isinstance(valor, str) and valor.startswith("param_"):
                    return params.get(valor, valor)
                return valor

            condicoes_entrada = [
                CondicaoEntrada(
                    tipo=ce['tipo'],
                    parametros={k: resolve(v) for k, v in ce.get('parametros', {'periodo': ce.get('periodo')}).items()}
                ) for ce in data['condicoes_entrada']
            ]

            condicoes_saida = [
                CondicaoSaida(
                    tipo=cs['tipo'],
                    parametros={k: resolve(v) for k, v in cs.get('parametros', {}).items()}
                ) for cs in data.get('condicoes_saida', [])
            ]

            stop = None
            if 'stop' in data:
                stop = StopConfig(
                    tipo=data['stop']['tipo'],
                    parametros={k: resolve(v) for k, v in data['stop'].items() if k != 'tipo'}
                )

            alvo = None
            if 'alvo' in data:
                alvo = AlvoConfig(
                    tipo=data['alvo']['tipo'],
                    parametros={k: resolve(v) for k, v in data['alvo'].items() if k != 'tipo'}
                )

            return cls(
                nome=data['nome'],
                tipo=data['tipo'],
                condicoes_entrada=condicoes_entrada,
                condicoes_saida=condicoes_saida,
                stop=stop,
                alvo=alvo
            )