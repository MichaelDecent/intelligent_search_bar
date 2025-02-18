from app.database.execute_sql import execute_sql

# 1. Recent Activity & Balance


def get_last_5_transactions(account_id: str):
    """
    Get the 5 most recent transactions for a specific account.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of the 5 most recent transaction records.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE account_id = '{account_id}'
        ORDER BY "date" DESC
        LIMIT 5;
    """
    return execute_sql(query)


def get_current_balance(account_id: str):
    """
    Get the current balance for a specific account.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: The current balance from the most recent transaction.
    """
    query = f"""
        SELECT balance_after
        FROM new_table
        WHERE account_id = '{account_id}'
        ORDER BY "date" DESC
        LIMIT 1;
    """
    return execute_sql(query)


def get_all_transactions(account_id: str):
    """
    Get all transactions for an account ordered by most recent first.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of all transaction records ordered by date descending.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE account_id = '{account_id}'
        ORDER BY "date" DESC;
    """
    return execute_sql(query)


# 2. Date-Specific Queries


def get_transactions_by_date(date_str: str, account_id: str):
    """
    Get all transactions for a specific date and account.

    Args:
        date_str (str): Date in YYYY-MM-DD format.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records for the given date.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE DATE("date") = '{date_str}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_between_dates(start_date: str, end_date: str, account_id: str):
    """
    Get all transactions between two dates for a specific account.

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records between the specified dates.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE "date" BETWEEN '{start_date}' AND '{end_date} 23:59:59'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_last_month(account_id: str):
    """
    Get the sum of all transactions from the previous calendar month.

    Uses PostgreSQL date functions to filter transactions between
    the first and last day of the previous month.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing the sum of transactions from the previous month.
    """
    query = f"""
        SELECT COALESCE(SUM(amount), 0) as total_transactions_last_month
        FROM new_table
        WHERE "date" >= date_trunc('month', current_date - interval '1 month')
          AND "date" < date_trunc('month', current_date)
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


# 3. Amount-Based Filters


def get_transactions_over(amount: float, account_id: str):
    """
    Get all transactions with amount greater than specified value.

    Args:
        amount (float): The minimum amount threshold.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records exceeding the specified amount.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE amount > {amount}
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_below(amount: float, account_id: str):
    """List all transactions below a specified amount for the given account."""
    query = f"""
        SELECT *
        FROM new_table
        WHERE amount < {amount}
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_by_exact_amount(amount: float, account_id: str):
    """
    Get all transactions matching an exact amount value.

    Args:
        amount (float): The exact amount to match (precise to 2 decimal places).
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records matching the exact amount.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE amount = {amount:.2f}
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


# 4. Transaction Type & Category


def get_deposits(account_id: str):
    """
    Get total deposit amount and category with highest deposit amount for an account.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: Contains total_deposits and category with highest deposit amount
    """
    query = f"""
        WITH deposit_totals AS (
            SELECT 
                category,
                SUM(amount) as category_total
            FROM new_table 
            WHERE transaction_type ILIKE '%credit%'
                AND account_id = '{account_id}'
            GROUP BY category
            ORDER BY category_total DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(SUM(amount), 0) as total_deposits,
            (SELECT category FROM deposit_totals) as highest_deposit_category,
            (SELECT category_total FROM deposit_totals) as highest_category_amount
        FROM new_table
        WHERE transaction_type ILIKE '%credit%'
            AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_withdrawals(account_id: str):
    """
    Get total withdrawal amount and category with highest withdrawal amount for an account.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: Contains total_withdrawals and category with highest withdrawal amount
    """
    query = f"""
        WITH withdrawal_totals AS (
            SELECT 
                category,
                SUM(amount) as category_total
            FROM new_table 
            WHERE transaction_type ILIKE '%debit%'
                AND account_id = '{account_id}'
            GROUP BY category
            ORDER BY category_total DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(SUM(amount), 0) as total_withdrawals,
            (SELECT category FROM withdrawal_totals) as highest_withdrawal_category,
            (SELECT category_total FROM withdrawal_totals) as highest_category_amount
        FROM new_table
        WHERE transaction_type ILIKE '%debit%'
            AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_by_category(category: str, account_id: str):
    """
    Get the total amounts for credit and debit transactions, as well as the overall sum,
    for a specific category and account.

    Args:
        category (str): The transaction category to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing 'credit_amount', 'debit_amount', and 'total_amount'.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount
        FROM new_table
        WHERE category ILIKE '{category}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


# 5. Narration & Description Searches


def get_transactions_by_narration_keyword(keyword: str, account_id: str):
    """
    Get transactions containing a specific keyword in their narration.

    Args:
        keyword (str): The keyword to search for in transaction narrations.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records containing the keyword.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE narration ILIKE '%{keyword}%'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


# 6. Account & Bank Specific Queries


def get_transactions_by_account_number(account_number: str, account_id: str):
    """
    Get credit amount, debit amount and total sum for transactions from a specific account number.

    Args:
        account_number (str): The account number to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount and total_amount for the account.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount
        FROM new_table
        WHERE account_number = '{account_number}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_by_bank_name(bank_name: str, account_id: str):
    """
    Get credit amount, debit amount and total sum for transactions from a specific bank.

    Args:
        bank_name (str): The name of the bank to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount and total_amount for the bank.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount
        FROM new_table
        WHERE bank_name ILIKE '{bank_name}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_by_account_id(account_id: str):
    """
    Get credit amount, debit amount and total sum for a specific account ID.

    Args:
        account_id (str): The unique identifier of the account (UUID format).

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount and total_amount for the account.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount
        FROM new_table
        WHERE account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_by_mono_connection_id(mono_connection_id: str, account_id: str):
    """
    Get credit amount, debit amount and total sum for a specific Mono connection ID.

    Args:
        mono_connection_id (str): The Mono connection ID to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount and total_amount for the connection.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount
        FROM new_table
        WHERE mono_connection_id = '{mono_connection_id}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


# 7. Currency-Based Queries


def get_transactions_by_currency(currency: str, account_id: str):
    """
    Get credit amount, debit amount and total sum for transactions in a specified currency.

    Args:
        currency (str): The currency code to filter by (e.g., 'USD', 'NGN').
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount and total_amount for the currency.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount
        FROM new_table
        WHERE currency = '{currency}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


# 9. Composite Filters


def get_withdrawals_over_last_days(amount: float, account_id: str, days: int = 30):
    """
    Get all withdrawals over a specified amount within a time period.

    Args:
        amount (float): The minimum withdrawal amount.
        account_id (str): The unique identifier of the account.
        days (int, optional): Number of past days to look back. Defaults to 30.

    Returns:
        List[Dict]: A list of withdrawal transactions meeting the criteria.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE transaction_type ILIKE '%withdrawal%'
          AND amount > {amount}
          AND "date" >= current_date - interval '{days} days'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_by_bank_and_category(
    bank_name: str, category: str, account_id: str
):
    """
    Get all transactions from a specific bank in a given category.

    Args:
        bank_name (str): The name of the bank to filter by.
        category (str): The transaction category to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records matching both bank name and category.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE bank_name ILIKE '{bank_name}'
          AND category ILIKE '{category}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_between_amounts_and_category(
    min_amount: float, max_amount: float, category: str, account_id: str
):
    """
    Get transactions between a specified amount range for a given category.

    Args:
        min_amount (float): The minimum amount threshold.
        max_amount (float): The maximum amount threshold.
        category (str): The transaction category to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records within the amount range and category.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE amount BETWEEN {min_amount} AND {max_amount}
          AND category ILIKE '{category}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


# 10. Historical & Audit Queries


def get_transactions_updated_since(specific_date: str, account_id: str):
    """
    Get all transactions updated on or after a specific date.

    Args:
        specific_date (str): Timestamp string in YYYY-MM-DD HH:MM:SS format.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records updated since the specified date.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE updated_at >= '{specific_date}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_created_last_week(account_id: str):
    """
    Get transactions created within the last 7 days.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records from the past week.
    """
    query = f"""
        SELECT *
        FROM new_table
        WHERE created_at >= current_date - interval '7 days'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_by_keyword(keyword: str, account_id: str):
    """
    Get credit amount, debit amount and total sum for transactions matching a keyword
    in bank_name, category, or transaction_type (in that order).

    Args:
        keyword (str): Keyword to search across bank_name, category and transaction_type columns
        account_id (str): The user's account ID to scope the query

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount and total_amount for matches
    """
    query = f"""
        SELECT
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount_{keyword},
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount_{keyword},
            SUM(amount) AS total_amount_{keyword}
        FROM new_table
        WHERE account_id = '{account_id}'
          AND (
              bank_name ILIKE '%{keyword}%' OR
              category ILIKE '%{keyword}%' OR
              transaction_type ILIKE '%{keyword}%'
          );
    """
    return execute_sql(query)
