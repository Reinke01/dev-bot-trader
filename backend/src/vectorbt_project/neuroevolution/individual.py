from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class Individual:
    genome: Dict[str, Any]
    fitness: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def clone(self) -> 'Individual':
        """Create a copy of the individual"""
        return Individual(
            genome=self.genome.copy(),
            fitness=self.fitness,
            metadata=self.metadata.copy() if self.metadata else None
        )