"""Business logic for a small command-line expense tracker."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Expense:
    """Represents one expense entry."""

    description: str
    amount: float
    category: str


def calculate_total(expenses: Iterable[Expense]) -> float:
    """Return the total amount of all expenses."""
    return round(sum(expense.amount for expense in expenses), 2)


def category_total(expenses: Iterable[Expense], category: str) -> float:
    """Return the total amount for one category, ignoring case."""
    normalized_category = category.strip().lower()
    return round(
        sum(
            expense.amount
            for expense in expenses
            if expense.category.strip().lower() == normalized_category
        ),
        2,
    )


def validate_expense(description: str, amount: float, category: str) -> Expense:
    """Validate user input and create an Expense object."""
    if not description.strip():
        raise ValueError("Description cannot be empty.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    if not category.strip():
        raise ValueError("Category cannot be empty.")

    return Expense(
        description=description.strip(),
        amount=round(float(amount), 2),
        category=category.strip(),
    )
