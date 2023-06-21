from dataclasses import dataclass, field
from datetime import datetime, date


@dataclass
class Budget:
    _id: str
    amount: float
    date: str

@dataclass
class Expense:
    _id: str
    title: str
    type: str
    amount: float
    date: str


