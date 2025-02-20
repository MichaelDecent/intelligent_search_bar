import decimal
from os import getenv

from dotenv import load_dotenv

from app.database.execute_sql import execute_sql
from app.database.sql_queries import (
    get_all_transactions,
    get_current_balance,
    get_deposits,
    get_recent_transactions,
    get_transactions_below,
    get_transactions_between_amounts_and_category,
    get_transactions_between_dates,
    get_transactions_by_bank_and_category,
    get_transactions_by_bank_name,
    get_transactions_by_category,
    get_transactions_by_date,
    get_transactions_created_last_week,
    get_transactions_last_month,
    get_transactions_over,
    get_transactions_updated_since,
    get_withdrawals,
    get_withdrawals_over_last_days,
)

load_dotenv()

ID = getenv("TEST_ID")


def test_execute_sql():
    result = execute_sql(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'new_table')"
    )
    assert result[0]["exists"] is True


def test_get_recent_transactions():
    result = get_recent_transactions(ID)

    # Basic assertions
    assert isinstance(result, list)  # Should return a list
    assert len(result) <= 3  # Should return max 3 transactions

    # If there are results, verify the structure
    if result:
        transaction = result[0]
        assert "amount" in transaction
        assert "transaction_type" in transaction
        assert "category" in transaction
        assert "bank_name" in transaction
        assert "balance_after" in transaction
        assert "total_amount_of_3_transactions" in transaction


def test_get_current_balance():
    # Execute the function with test ID
    result = get_current_balance(ID)

    # Basic assertions
    assert isinstance(result, list)  # Should return a list

    balance_info = result[0]
    assert "balance_after" in balance_info
    assert isinstance(balance_info["balance_after"], (int, float, decimal.Decimal))


def test_get_all_transactions():
    result = get_all_transactions(ID)

    assert isinstance(result, list)

    transaction_summary = result[0]
    expected_fields = [
        "total_amount",
        "total_credit",
        "total_debit",
        "highest_credit_category",
        "highest_credit_amount",
        "highest_debit_category",
        "highest_debit_amount",
    ]
    for field in expected_fields:
        assert field in transaction_summary

    numeric_fields = [
        "total_amount",
        "total_credit",
        "total_debit",
        "highest_credit_amount",
        "highest_debit_amount",
    ]
    for field in numeric_fields:
        if transaction_summary[field] is not None:
            assert isinstance(transaction_summary[field], (int, float, decimal.Decimal))


def test_get_transactions_by_date():
    date = "2024-01-20"
    result = get_transactions_by_date(date, ID)

    assert isinstance(result, list)

    transaction = result[0]
    expected_fields = ["amount", "category", "transaction_type", "bank_name"]
    for field in expected_fields:
        assert field in transaction

    assert isinstance(transaction["amount"], (int, float, decimal.Decimal))
    assert isinstance(transaction["category"], str)
    assert isinstance(transaction["transaction_type"], str)
    assert isinstance(transaction["bank_name"], str)


def test_get_transactions_between_dates():
    start_date = "2024-01-10"
    end_date = "2024-01-20"
    result = get_transactions_between_dates(start_date, end_date, ID)

    assert isinstance(result, list)

    transaction = result[0]
    expected_fields = [
        "amount",
        "category",
        "transaction_type",
        "bank_name",
    ]
    for field in expected_fields:
        assert field in transaction

    # Verify data types
    assert isinstance(transaction["amount"], (int, float, decimal.Decimal))
    assert isinstance(transaction["category"], str)
    assert isinstance(transaction["transaction_type"], str)
    assert isinstance(transaction["bank_name"], str)


def test_get_transactions_last_month():
    # Execute function with test ID
    result = get_transactions_last_month(ID)

    # Basic assertions
    assert isinstance(result, list)

    monthly_summary = result[0]
    expected_fields = [
        "total_transactions_last_month",
        "total_received",
        "total_spent",
        "highest_spent_category",
        "highest_spent_amount",
    ]
    for field in expected_fields:
        assert field in monthly_summary

    # Verify numeric fields have correct type
    numeric_fields = [
        "total_transactions_last_month",
        "total_received",
        "total_spent",
        "highest_spent_amount",
    ]
    for field in numeric_fields:
        if monthly_summary[field] is not None:
            assert isinstance(monthly_summary[field], (int, float, decimal.Decimal))

        # Verify category field is string if present
    if monthly_summary["highest_spent_category"]:
        assert isinstance(monthly_summary["highest_spent_category"], str)


def test_get_transactions_over():
    # Test with a threshold amount
    threshold = 1000.00
    result = get_transactions_over(threshold, ID)

    # Basic assertions
    assert isinstance(result, list)

    transaction = result[0]
    expected_fields = ["amount", "category", "transaction_type", "bank_name"]
    for field in expected_fields:
        assert field in transaction

    # Verify amount is above threshold
    assert float(transaction["amount"]) > threshold

    # Verify data types
    assert isinstance(transaction["amount"], (int, float, decimal.Decimal))
    assert isinstance(transaction["category"], str)
    assert isinstance(transaction["transaction_type"], str)
    assert isinstance(transaction["bank_name"], str)


def test_get_transactions_below():
    # Test with a threshold amount
    threshold = 5000.00
    result = get_transactions_below(threshold, ID)

    # Basic assertions
    assert isinstance(result, list)

    transaction = result[0]
    expected_fields = ["amount", "category", "transaction_type", "bank_name"]
    for field in expected_fields:
        assert field in transaction

    # Verify amount is below threshold
    assert float(transaction["amount"]) < threshold

    # Verify data types
    assert isinstance(transaction["amount"], (int, float, decimal.Decimal))
    assert isinstance(transaction["category"], str)
    assert isinstance(transaction["transaction_type"], str)
    assert isinstance(transaction["bank_name"], str)


def test_get_deposits():
    # Execute function with test ID
    result = get_deposits(ID)

    # Basic assertions
    assert isinstance(result, list)

    deposit_summary = result[0]
    expected_fields = [
        "total_deposits",
        "highest_deposit_category",
        "highest_category_amount",
    ]
    for field in expected_fields:
        assert field in deposit_summary

    # Verify numeric fields have correct type
    numeric_fields = ["total_deposits", "highest_category_amount"]
    for field in numeric_fields:
        if deposit_summary[field] is not None:
            assert isinstance(deposit_summary[field], (int, float, decimal.Decimal))

    # Verify category field is string if present
    if deposit_summary["highest_deposit_category"]:
        assert isinstance(deposit_summary["highest_deposit_category"], str)


def test_get_withdrawals():
    # Execute function with test ID
    result = get_withdrawals(ID)

    # Basic assertions
    assert isinstance(result, list)

    withdrawal_summary = result[0]
    expected_fields = [
        "total_withdrawals",
        "highest_withdrawal_category",
        "highest_category_amount",
    ]
    for field in expected_fields:
        assert field in withdrawal_summary

    # Verify numeric fields have correct type
    numeric_fields = ["total_withdrawals", "highest_category_amount"]
    for field in numeric_fields:
        if withdrawal_summary[field] is not None:
            assert isinstance(withdrawal_summary[field], (int, float, decimal.Decimal))

    # Verify category field is string if present
    if withdrawal_summary["highest_withdrawal_category"]:
        assert isinstance(withdrawal_summary["highest_withdrawal_category"], str)


def test_get_transactions_by_category():
    # Test with a sample category
    category = "transfer"
    result = get_transactions_by_category(category, ID)

    # Basic assertions
    assert isinstance(result, list)

    transaction_summary = result[0]
    expected_fields = ["credit_amount", "debit_amount", "total_amount"]

    # Check all expected fields are present
    for field in expected_fields:
        assert field in transaction_summary

    # Verify numeric fields have correct type
    for field in expected_fields:
        if transaction_summary[field] is not None:
            assert isinstance(transaction_summary[field], (int, float, decimal.Decimal))

    # Verify total_amount equals credit_amount minus debit_amount
    if all(transaction_summary[field] is not None for field in expected_fields):
        expected_total = (
            transaction_summary["credit_amount"] + transaction_summary["debit_amount"]
        )
        assert (
            abs(transaction_summary["total_amount"] - expected_total) < 0.01
        )  # Allow for small rounding differences


def test_get_transactions_by_bank_name():
    # Test with a sample bank name
    bank_name = "GTBank"
    result = get_transactions_by_bank_name(bank_name, ID)

    # Basic assertions
    assert isinstance(result, list)

    transaction_summary = result[0]
    expected_fields = ["credit_amount", "debit_amount", "total_amount"]

    # Check all expected fields are present
    for field in expected_fields:
        assert field in transaction_summary

    # Verify numeric fields have correct type
    for field in expected_fields:
        if transaction_summary[field] is not None:
            assert isinstance(transaction_summary[field], (int, float, decimal.Decimal))

    # Verify total amount matches credit minus debit
    if all(transaction_summary[field] is not None for field in expected_fields):
        expected_total = (
            transaction_summary["credit_amount"] + transaction_summary["debit_amount"]
        )
        assert abs(transaction_summary["total_amount"] - expected_total) < 0.01


def test_get_transactions_created_last_week():
    # Execute function with test ID
    result = get_transactions_created_last_week(ID)

    # Basic assertions
    assert isinstance(result, list)

    if result:
        weekly_summary = result[0]
        expected_fields = [
            "total_sum",
            "total_spent",
            "total_received",
            "highest_spend_category",
            "highest_spend_amount",
        ]

        # Check all expected fields are present
        for field in expected_fields:
            assert field in weekly_summary

        # Verify numeric fields have correct type
        numeric_fields = [
            "total_sum",
            "total_spent",
            "total_received",
            "highest_spend_amount",
        ]
        for field in numeric_fields:
            if weekly_summary[field] is not None:
                assert isinstance(weekly_summary[field], (int, float, decimal.Decimal))

            # Verify category field is string if present
        if weekly_summary["highest_spend_category"]:
            assert isinstance(weekly_summary["highest_spend_category"], str)

        # Verify total sum equals received minus spent
        if all(
            field in weekly_summary
            for field in ["total_sum", "total_received", "total_spent"]
        ):
            expected_total = (
                weekly_summary["total_received"] + weekly_summary["total_spent"]
            )
            assert abs(weekly_summary["total_sum"] - expected_total) < 0.01


def test_get_withdrawals_over_last_days():
    # Test parameters
    min_amount = 100000.00
    days = 50

    # Execute function with test parameters
    result = get_withdrawals_over_last_days(min_amount, ID, days)

    # Basic assertions
    assert isinstance(result, list)

    withdrawal_summary = result[0]
    expected_fields = [
        "total_sum",
        "total_spent",
        "total_received",
        "highest_spend_category",
        "highest_category_amount",
    ]

    # Check all expected fields are present
    for field in expected_fields:
        assert field in withdrawal_summary

    # Verify numeric fields have correct type
    numeric_fields = [
        "total_sum",
        "total_spent",
        "total_received",
        "highest_category_amount",
    ]
    for field in numeric_fields:
        if withdrawal_summary[field] is not None:
            assert isinstance(withdrawal_summary[field], (int, float, decimal.Decimal))

    # Verify category field is string if present
    if withdrawal_summary["highest_spend_category"]:
        assert isinstance(withdrawal_summary["highest_spend_category"], str)

    # Verify total sum equals received minus spent
    if all(
        withdrawal_summary[field] is not None
        for field in ["total_sum", "total_received", "total_spent"]
    ):
        expected_total = (
            withdrawal_summary["total_received"] + withdrawal_summary["total_spent"]
        )
        assert abs(withdrawal_summary["total_sum"] - expected_total) < 0.01


def test_get_transactions_updated_since():
    # Test parameters
    specific_date = "2024-02-01 00:00:00"
    result = get_transactions_updated_since(specific_date, ID)

    # Basic assertions
    assert isinstance(result, list)

    transaction_summary = result[0]
    expected_fields = [
        "total_sum",
        "total_spent",
        "total_received",
        "highest_spend_category",
        "highest_spend_amount",
    ]

    # Check all expected fields are present
    for field in expected_fields:
        assert field in transaction_summary

    # Verify numeric fields
    numeric_fields = [
        "total_sum",
        "total_spent",
        "total_received",
        "highest_spend_amount",
    ]
    for field in numeric_fields:
        if transaction_summary[field] is not None:
            assert isinstance(transaction_summary[field], (int, float, decimal.Decimal))

    # Verify category field is string if present
    if transaction_summary["highest_spend_category"]:
        assert isinstance(transaction_summary["highest_spend_category"], str)


def test_get_transactions_between_amounts_and_category():
    # Test parameters
    min_amount = 100000.00
    max_amount = 1000000.00
    category = "transfer"

    result = get_transactions_between_amounts_and_category(
        min_amount, max_amount, category, ID
    )

    # Basic assertions
    assert isinstance(result, list)

    transaction_summary = result[0]
    expected_fields = [
        "total_sum",
        "total_spent",
        "total_received",
        "highest_spend_category",
        "highest_category_amount",
    ]

    # Check all expected fields are present
    for field in expected_fields:
        assert field in transaction_summary

    # Verify numeric fields
    numeric_fields = [
        "total_sum",
        "total_spent",
        "total_received",
        "highest_category_amount",
    ]
    for field in numeric_fields:
        if transaction_summary[field] is not None:
            assert isinstance(transaction_summary[field], (int, float, decimal.Decimal))

    # Verify category field is string if present
    if transaction_summary["highest_spend_category"]:
        assert isinstance(transaction_summary["highest_spend_category"], str)


def test_get_transactions_by_bank_and_category():
    # Test parameters
    bank_name = "GTBank"
    category = "transfer"

    result = get_transactions_by_bank_and_category(bank_name, category, ID)

    # Basic assertions
    assert isinstance(result, list)

    transaction_summary = result[0]
    expected_fields = ["total_sum", "total_spent", "total_received"]

    # Check all expected fields are present
    for field in expected_fields:
        assert field in transaction_summary

    # Verify all fields are numeric
    for field in expected_fields:
        if transaction_summary[field] is not None:
            assert isinstance(transaction_summary[field], (int, float, decimal.Decimal))
