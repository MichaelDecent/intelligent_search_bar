from datetime import datetime, timezone
from unittest.mock import patch

import pytest

# Mock Data Setup
TEST_ACCOUNT_ID = "550e8400-e29b-41d4-a716-446655440000"

MOCK_TRANSACTIONS = [
    {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "transaction_id": "a23e4567-e89b-12d3-a456-426614174001",
        "amount": 50000.00,
        "date": datetime(2024, 2, 19, 10, 30, tzinfo=timezone.utc),
        "narration": "SALARY PAYMENT - FEB 2024",
        "transaction_type": "credit",
        "balance_after": 150000.00,
        "category": "salary",
        "created_at": datetime(2024, 2, 19, 10, 30, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 2, 19, 10, 30, tzinfo=timezone.utc),
        "account_id": TEST_ACCOUNT_ID,
        "mono_connection_id": "m23e4567-e89b-12d3-a456-426614174001",
        "currency": "NGN",
        "first_name": "John",
        "last_name": "Doe",
        "account_number": "0123456789",
        "bank_name": "First Bank",
    },
    {
        "id": "123e4567-e89b-12d3-a456-426614174002",
        "transaction_id": "b23e4567-e89b-12d3-a456-426614174002",
        "amount": -15000.00,
        "date": datetime(2024, 2, 18, 15, 45, tzinfo=timezone.utc),
        "narration": "SHOPPING - MALL PURCHASE",
        "transaction_type": "debit",
        "balance_after": 100000.00,
        "category": "shopping",
        "created_at": datetime(2024, 2, 18, 15, 45, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 2, 18, 15, 45, tzinfo=timezone.utc),
        "account_id": TEST_ACCOUNT_ID,
        "mono_connection_id": "m23e4567-e89b-12d3-a456-426614174002",
        "currency": "NGN",
        "first_name": "John",
        "last_name": "Doe",
        "account_number": "0123456789",
        "bank_name": "First Bank",
    },
    {
        "id": "123e4567-e89b-12d3-a456-426614174003",
        "transaction_id": "c23e4567-e89b-12d3-a456-426614174003",
        "amount": -5000.00,
        "date": datetime(2024, 2, 17, 9, 20, tzinfo=timezone.utc),
        "narration": "UTILITY BILL PAYMENT",
        "transaction_type": "debit",
        "balance_after": 115000.00,
        "category": "utilities",
        "created_at": datetime(2024, 2, 17, 9, 20, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 2, 17, 9, 20, tzinfo=timezone.utc),
        "account_id": TEST_ACCOUNT_ID,
        "mono_connection_id": "m23e4567-e89b-12d3-a456-426614174003",
        "currency": "NGN",
        "first_name": "John",
        "last_name": "Doe",
        "account_number": "0123456789",
        "bank_name": "UBA",
    },
    {
        "id": "123e4567-e89b-12d3-a456-426614174004",
        "transaction_id": "d23e4567-e89b-12d3-a456-426614174004",
        "amount": 25000.00,
        "date": datetime(2024, 2, 16, 14, 15, tzinfo=timezone.utc),
        "narration": "TRANSFER FROM JAMES",
        "transaction_type": "credit",
        "balance_after": 120000.00,
        "category": "transfer",
        "created_at": datetime(2024, 2, 16, 14, 15, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 2, 16, 14, 15, tzinfo=timezone.utc),
        "account_id": TEST_ACCOUNT_ID,
        "mono_connection_id": "m23e4567-e89b-12d3-a456-426614174004",
        "currency": "NGN",
        "first_name": "John",
        "last_name": "Doe",
        "account_number": "0123456789",
        "bank_name": "GTBank",
    },
    {
        "id": "123e4567-e89b-12d3-a456-426614174005",
        "transaction_id": "e23e4567-e89b-12d3-a456-426614174005",
        "amount": -10000.00,
        "date": datetime(2024, 2, 15, 20, 30, tzinfo=timezone.utc),
        "narration": "RESTAURANT PAYMENT",
        "transaction_type": "debit",
        "balance_after": 95000.00,
        "category": "entertainment",
        "created_at": datetime(2024, 2, 15, 20, 30, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 2, 15, 20, 30, tzinfo=timezone.utc),
        "account_id": TEST_ACCOUNT_ID,
        "mono_connection_id": "m23e4567-e89b-12d3-a456-426614174005",
        "currency": "NGN",
        "first_name": "John",
        "last_name": "Doe",
        "account_number": "0123456789",
        "bank_name": "UBA",
    },
]


@pytest.fixture
def mock_db():
    """Fixture to mock the database execution"""
    with patch("app.database.sql_queries.execute_sql") as mock:
        mock.return_value = MOCK_TRANSACTIONS
        yield mock


def test_get_recent_transactions(mock_db):
    """Test getting 3 most recent transactions"""
    from app.database.sql_queries import get_recent_transactions

    # Call the function with test account ID
    result = get_recent_transactions(TEST_ACCOUNT_ID)

    # Verify mock_db was called with correct query
    mock_db.assert_called_once()
    query_call = mock_db.call_args[0][0]
    assert "SELECT" in query_call
    assert 'ORDER BY "date" DESC' in query_call
    assert "LIMIT 3" in query_call
    assert TEST_ACCOUNT_ID in query_call

    # Verify the returned data matches expectations
    assert len(result) == len(MOCK_TRANSACTIONS)  # Will be 5 due to mock setup

    # Verify the structure of returned data
    first_transaction = result[0]
    assert "amount" in first_transaction
    assert "transaction_type" in first_transaction
    assert "category" in first_transaction
    assert "bank_name" in first_transaction
    assert "balance_after" in first_transaction
