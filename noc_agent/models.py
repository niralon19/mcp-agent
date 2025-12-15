from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Action:
    name: str
    args: Dict
    risk: str

@dataclass
class Decision:
    recommendation: str
    confidence: float
    actions: List[Action]
    close_message: str
