from dataclasses import dataclass, field
from datetime import datetime, date

@dataclass
class Date:
    _id: str
    expenses: list[str] = field(default_factory=list)

@dataclass
class Budget:
    _id: str
    amount: float

@dataclass
class Expense:
    _id: str
    title: str
    type: str
    amount: float


