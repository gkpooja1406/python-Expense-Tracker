"""Command-line entry point for the Expense Tracker project."""

from expense_tracker.tracker import Expense, calculate_total, category_total


def main() -> None:
    """Run a small real-world expense summary demonstration."""
    expenses = [
        Expense("Bus ticket", 45.0, "Travel"),
        Expense("Lunch", 120.0, "Food"),
        Expense("Coffee", 60.0, "Food"),
    ]

    print("Expense Tracker")
    print(f"Total expense: Rs.{calculate_total(expenses):.2f}")
    print(f"Food expense: Rs.{category_total(expenses, 'Food'):.2f}")


if __name__ == "__main__":
    main()
