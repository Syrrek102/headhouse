from dataclasses import dataclass, field

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

@dataclass
class User:
    _id: str
    email: str
    password: str
    expenses: list[str] = field(default_factory=list)
    budgets: list[str] = field(default_factory=list)

