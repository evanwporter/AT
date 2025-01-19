from dataclasses import dataclass, field
from pandas import Timestamp

from typing import List

@dataclass
class BarEvent:
    type_: str  = field(init=False, default="BAR")
    symbols: list = field(init=False, default_factory=list)
    date: Timestamp

@dataclass
class SentimentEvent:
    type_: str  = field(init=False, default="SENTIMENT")
    symbols: List[str] = field(init=False, default_factory=dict)
    date: Timestamp
