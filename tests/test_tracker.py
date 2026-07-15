import pytest

from expense_tracker.tracker import (
    Expense,
    calculate_total,
    category_total,
    validate_expense,
)


def test_calculate_total() -> None:
    expenses = [
        Expense("Lunch", 100.0, "Food"),
        Expense("Bus", 50.0, "Travel"),
    ]
    assert calculate_total(expenses) == 150.0


def test_category_total_is_case_insensitive() -> None:
    expenses = [
        Expense("Lunch", 100.0, "Food"),
        Expense("Coffee", 50.0, "food"),
        Expense("Bus", 30.0, "Travel"),
    ]
    assert category_total(expenses, "FOOD") == 150.0


def test_validate_expense_returns_clean_object() -> None:
    expense = validate_expense("  Books  ", 250.456, " Education ")
    assert expense == Expense("Books", 250.46, "Education")


@pytest.mark.parametrize(
    "description,amount,category",
    [
        ("", 100.0, "Food"),
        ("Lunch", 0, "Food"),
        ("Lunch", -10, "Food"),
        ("Lunch", 100.0, ""),
    ],
)
def test_validate_expense_rejects_invalid_data(
    description: str,
    amount: float,
    category: str,
) -> None:
    with pytest.raises(ValueError):
        validate_expense(description, amount, category)
