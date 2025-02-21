from app.database.execute_sql import execute_sql


def get_recent_transactions(account_id: str):
    """
    Get the 3 most recent transactions for a specific account, retrieving the amount,
    transaction type, category, bank name, balance after the transaction, currency and
    the sum of these 3 transactions.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of the 3 most recent transaction records with the required columns.
    """
    query = f"""
        WITH recent_transactions AS (
            SELECT 
                amount,
                transaction_type,
                category,
                bank_name,
                balance_after,
                currency
            FROM new_table
            WHERE account_id = '{account_id}'
            ORDER BY "date" DESC
            LIMIT 3
        )
        SELECT 
            rt.*,
            (SELECT SUM(amount) FROM recent_transactions) as total_amount_of_3_transactions
        FROM recent_transactions rt;
    """
    return execute_sql(query)


def get_current_balance(account_id: str):
    """
    Get the current balance and currency for a specific account.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: The current balance and currency from the most recent transaction.
    """
    query = f"""
        SELECT 
            balance_after,
            currency
        FROM new_table
        WHERE account_id = '{account_id}'
        ORDER BY "date" DESC
        LIMIT 1;
    """
    return execute_sql(query)


def get_all_transactions(account_id: str):
    """
    Get aggregate sums for all transactions for an account, including the total sum,
    the sum for debit transactions, the sum for credit transactions, and the categories
    with the highest debit and credit amounts (along with their sums and currencies).

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing total_amount, total_credit, total_debit,
              highest_credit_category, highest_credit_amount, highest_debit_category,
              highest_debit_amount, and their respective currencies.
    """
    query = f"""
        WITH highest_credit AS (
            SELECT category, SUM(amount) AS credit_sum, currency
            FROM new_table
            WHERE transaction_type ILIKE '%credit%'
              AND account_id = '{account_id}'
            GROUP BY category, currency
            ORDER BY credit_sum DESC
            LIMIT 1
        ),
        highest_debit AS (
            SELECT category, SUM(amount) AS debit_sum, currency
            FROM new_table
            WHERE transaction_type ILIKE '%debit%'
              AND account_id = '{account_id}'
            GROUP BY category, currency
            ORDER BY debit_sum DESC
            LIMIT 1
        ),
        total_amounts AS (
            SELECT 
                SUM(amount) AS total_amount,
                currency,
                SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS total_credit,
                SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS total_debit
            FROM new_table
            WHERE account_id = '{account_id}'
            GROUP BY currency
            ORDER BY total_amount DESC
            LIMIT 1
        )
        SELECT 
            total_amount,
            total_credit,
            total_debit,
            (SELECT currency FROM total_amounts) AS currency,
            (SELECT category FROM highest_credit) AS highest_credit_category,
            (SELECT credit_sum FROM highest_credit) AS highest_credit_amount,
            (SELECT currency FROM highest_credit) AS highest_credit_currency,
            (SELECT category FROM highest_debit) AS highest_debit_category,
            (SELECT debit_sum FROM highest_debit) AS highest_debit_amount,
            (SELECT currency FROM highest_debit) AS highest_debit_currency
        FROM total_amounts;
    """
    return execute_sql(query)


def get_transactions_by_date(date_str: str, account_id: str):
    """
    Get all transactions for a specific date and account, retrieving individual amounts, currency,
    category, transaction type and bank name used to make the transaction.

    Args:
        date_str (str): Date in YYYY-MM-DD format.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records with the individual amount, currency, category,
                    transaction type and bank name.
    """
    query = f"""
        SELECT 
            amount,
            currency,
            category, 
            transaction_type,
            bank_name
        FROM new_table
        WHERE DATE("date") = '{date_str}'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_between_dates(start_date: str, end_date: str, account_id: str):
    """
    Get individual amounts, currency, category, transaction type, and bank name
    for transactions between two dates for a specific account.

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records with the amount, currency, category,
                    transaction_type and bank_name between the specified dates.
    """
    query = f"""
        SELECT 
            amount,
            currency,
            category,
            transaction_type,
            bank_name
        FROM new_table
        WHERE "date" BETWEEN '{start_date}' AND '{end_date} 23:59:59'
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_last_month(account_id: str):
    """
    Get summary of transactions from the previous calendar month including:
      - Total transaction amount with currency
      - Total received (credits) with currency
      - Total spent (debits) with currency
      - Category with the highest spending and its amount with currency

    Uses PostgreSQL date functions to filter transactions between
    the first and last day of the previous month.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing the aggregated values for transactions with currencies.
    """
    query = f"""
        WITH last_month AS (
            SELECT *
            FROM new_table
            WHERE "date" >= date_trunc('month', current_date - interval '1 month')
              AND "date" < date_trunc('month', current_date)
              AND account_id = '{account_id}'
        ),
        highest_spent_category AS (
            SELECT category, SUM(amount) AS total_spent, currency
            FROM last_month
            WHERE transaction_type ILIKE '%debit%'
            GROUP BY category, currency
            ORDER BY total_spent DESC
            LIMIT 1
        ),
        totals AS (
            SELECT 
                SUM(amount) as total_amount,
                currency,
                SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS total_received,
                SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS total_spent
            FROM last_month
            GROUP BY currency
            ORDER BY total_amount DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(total_amount, 0) AS total_transactions_last_month,
            (SELECT currency FROM totals) AS total_currency,
            COALESCE(total_received, 0) AS total_received,
            (SELECT currency FROM totals) AS received_currency,
            COALESCE(total_spent, 0) AS total_spent,
            (SELECT currency FROM totals) AS spent_currency,
            (SELECT category FROM highest_spent_category) AS highest_spent_category,
            (SELECT total_spent FROM highest_spent_category) AS highest_spent_amount,
            (SELECT currency FROM highest_spent_category) AS highest_spent_currency
        FROM totals;
    """
    return execute_sql(query)


def get_transactions_over(amount: float, account_id: str):
    """
    Get the individual amounts, currency, category, transaction type, and bank name for transactions
    with an amount greater than the specified value.

    Args:
        amount (float): The minimum amount threshold.
        account_id (str): The unique identifier of the account.

    Returns:
        List[Dict]: A list of transaction records with the specified columns.
    """
    query = f"""
        SELECT 
            amount,
            currency,
            category,
            transaction_type,
            bank_name
        FROM new_table
        WHERE amount > {amount}
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_transactions_below(amount: float, account_id: str):
    """
    List individual transaction amounts, currency, category, transaction type, and bank name for transactions \
    below a specified amount for the given account.
    """
    query = f"""
        SELECT 
            amount,
            currency,
            category, 
            transaction_type,
            bank_name
        FROM new_table
        WHERE amount < {amount}
          AND account_id = '{account_id}';
    """
    return execute_sql(query)


def get_deposits(account_id: str):
    """
    Get total deposit amount and category with highest deposit amount for an account.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: Contains total_deposits, currency and category with highest deposit amount
    """
    query = f"""
        WITH deposit_totals AS (
            SELECT 
                category,
                SUM(amount) as category_total,
                currency
            FROM new_table 
            WHERE transaction_type ILIKE '%credit%'
                AND account_id = '{account_id}'
            GROUP BY category, currency
            ORDER BY category_total DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(SUM(amount), 0) as total_deposits,
            (SELECT currency FROM deposit_totals) as total_deposits_currency,
            (SELECT category FROM deposit_totals) as highest_deposit_category,
            (SELECT category_total FROM deposit_totals) as highest_category_amount,
            (SELECT currency FROM deposit_totals) as highest_category_currency
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
        Dict: Contains total_withdrawals, currency and category with highest withdrawal amount
    """
    query = f"""
        WITH withdrawal_totals AS (
            SELECT 
                category,
                SUM(amount) as category_total,
                currency
            FROM new_table 
            WHERE transaction_type ILIKE '%debit%'
                AND account_id = '{account_id}'
            GROUP BY category, currency
            ORDER BY category_total DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(SUM(amount), 0) as total_withdrawals,
            (SELECT currency FROM withdrawal_totals) as total_withdrawals_currency,
            (SELECT category FROM withdrawal_totals) as highest_withdrawal_category,
            (SELECT category_total FROM withdrawal_totals) as highest_category_amount,
            (SELECT currency FROM withdrawal_totals) as highest_category_currency
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
        Dict: A dictionary containing 'credit_amount', 'debit_amount', 'total_amount'
              and their respective currencies.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount,
            MAX(currency) AS currency
        FROM new_table
        WHERE category ILIKE '{category}'
          AND account_id = '{account_id}'
        GROUP BY currency
        ORDER BY total_amount DESC
        LIMIT 1;
    """
    return execute_sql(query)


def get_transactions_by_account_number(account_number: str, account_id: str):
    """
    Get credit amount, debit amount and total sum for transactions from a specific account number.

    Args:
        account_number (str): The account number to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount, total_amount and their currencies.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount,
            MAX(currency) AS currency
        FROM new_table
        WHERE account_number = '{account_number}'
          AND account_id = '{account_id}'
        GROUP BY currency
        ORDER BY total_amount DESC
        LIMIT 1;
    """
    return execute_sql(query)


def get_transactions_by_bank_name(bank_name: str, account_id: str):
    """
    Get credit amount, debit amount and total sum for transactions from a specific bank.

    Args:
        bank_name (str): The name of the bank to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount, total_amount and their currencies.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount,
            MAX(currency) AS currency
        FROM new_table
        WHERE bank_name ILIKE '{bank_name}'
          AND account_id = '{account_id}'
        GROUP BY currency
        ORDER BY total_amount DESC
        LIMIT 1;
    """
    return execute_sql(query)


def get_transactions_by_account_id(account_id: str):
    """
    Get credit amount, debit amount and total sum for a specific account ID.

    Args:
        account_id (str): The unique identifier of the account (UUID format).

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount, total_amount and their currencies for the account.
    """
    query = f"""
        SELECT 
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount,
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount,
            SUM(amount) AS total_amount,
            MAX(currency) AS currency
        FROM new_table
        WHERE account_id = '{account_id}'
        GROUP BY currency
        ORDER BY total_amount DESC
        LIMIT 1;
    """
    return execute_sql(query)


def get_transactions_by_currency(currency: str, account_id: str):
    """
    Get credit amount, debit amount and total sum for transactions in a specified currency.

    Args:
        currency (str): The currency code to filter by (e.g., 'USD', 'NGN').
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount, total_amount and their currencies.
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
    Get summary of withdrawals over a specified amount within a time period.

    Args:
        amount (float): The minimum withdrawal amount.
        account_id (str): The unique identifier of the account.
        days (int, optional): Number of past days to look back. Defaults to 30.

    Returns:
        Dict: Contains total sum, amount spent, amount received,\ 
        and highest spending category with amount and currencies.
    """
    query = f"""
        WITH filtered_transactions AS (
            SELECT *
            FROM new_table 
            WHERE amount > {amount}
              AND "date" >= current_date - interval '{days} days'
              AND account_id = '{account_id}'
        ),
        top_category AS (
            SELECT category, SUM(amount) as category_total, currency
            FROM filtered_transactions
            WHERE transaction_type ILIKE '%debit%'
            GROUP BY category, currency
            ORDER BY category_total DESC
            LIMIT 1
        ),
        totals AS (
            SELECT 
                SUM(amount) as total_sum,
                SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) as total_spent,
                SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) as total_received,
                currency
            FROM filtered_transactions
            GROUP BY currency
            ORDER BY total_sum DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(total_sum, 0) as total_sum,
            (SELECT currency FROM totals) as total_currency,
            COALESCE(total_spent, 0) as total_spent,
            (SELECT currency FROM totals) as spent_currency,
            COALESCE(total_received, 0) as total_received,
            (SELECT currency FROM totals) as received_currency,
            (SELECT category FROM top_category) as highest_spend_category,
            (SELECT category_total FROM top_category) as highest_category_amount,
            (SELECT currency FROM top_category) as highest_category_currency
        FROM totals;
    """
    return execute_sql(query)


def get_transactions_by_bank_and_category(
    bank_name: str, category: str, account_id: str
):
    """
    Get transaction summaries from a specific bank in a given category.

    Args:
        bank_name (str): The name of the bank to filter by.
        category (str): The transaction category to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: Contains total sum, amount spent (debits), and amount received (credits) with their currencies.
    """
    query = f"""
        WITH totals AS (
            SELECT 
                SUM(amount) as total_sum,
                SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) as total_spent,
                SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) as total_received,
                currency
            FROM new_table
            WHERE bank_name ILIKE '{bank_name}'
              AND category ILIKE '{category}'
              AND account_id = '{account_id}'
            GROUP BY currency
            ORDER BY total_sum DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(total_sum, 0) as total_sum,
            currency as total_currency,
            COALESCE(total_spent, 0) as total_spent,
            currency as spent_currency,
            COALESCE(total_received, 0) as total_received,
            currency as received_currency
        FROM totals;
    """
    return execute_sql(query)


def get_transactions_between_amounts_and_category(
    min_amount: float, max_amount: float, category: str, account_id: str
):
    """
    Get transaction summary between a specified amount range for a given category.

    Args:
        min_amount (float): The minimum amount threshold.
        max_amount (float): The maximum amount threshold.
        category (str): The transaction category to filter by.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: Contains total sum, amount spent, amount received, and highest spending category details with currencies
    """
    query = f"""
        WITH filtered_transactions AS (
            SELECT *
            FROM new_table
            WHERE amount BETWEEN {min_amount} AND {max_amount}
              AND category ILIKE '{category}'
              AND account_id = '{account_id}'
        ),
        top_category AS (
            SELECT category, SUM(amount) as category_total, currency
            FROM filtered_transactions 
            WHERE transaction_type ILIKE '%debit%'
            GROUP BY category, currency
            ORDER BY category_total DESC
            LIMIT 1
        ),
        totals AS (
            SELECT 
                SUM(amount) as total_sum,
                SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) as total_spent,
                SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) as total_received,
                currency
            FROM filtered_transactions
            GROUP BY currency
            ORDER BY total_sum DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(total_sum, 0) as total_sum,
            (SELECT currency FROM totals) as total_currency,
            COALESCE(total_spent, 0) as total_spent,
            (SELECT currency FROM totals) as spent_currency,
            COALESCE(total_received, 0) as total_received,
            (SELECT currency FROM totals) as received_currency,
            (SELECT category FROM top_category) as highest_spend_category,
            (SELECT category_total FROM top_category) as highest_category_amount,
            (SELECT currency FROM top_category) as highest_category_currency
        FROM totals;
    """
    return execute_sql(query)


def get_transactions_updated_since(specific_date: str, account_id: str):
    """
    Get transaction totals and highest spending category for transactions updated since a specific date.

    Args:
        specific_date (str): Timestamp string in YYYY-MM-DD HH:MM:SS format.
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: Contains total sum, amount spent, amount received, and highest spending category with amount.
    """
    query = f"""
        WITH filtered_transactions AS (
            SELECT *
            FROM new_table
            WHERE updated_at >= '{specific_date}'
              AND account_id = '{account_id}'
        ),
        highest_spend_category AS (
            SELECT category, SUM(amount) as category_total
            FROM filtered_transactions
            WHERE transaction_type ILIKE '%debit%'
            GROUP BY category
            ORDER BY category_total DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(SUM(amount), 0) as total_sum,
            COALESCE(SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END), 0) as total_spent,
            COALESCE(SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END), 0) as total_received,
            (SELECT category FROM highest_spend_category) as highest_spend_category,
            (SELECT category_total FROM highest_spend_category) as highest_spend_amount
        FROM filtered_transactions;
    """
    return execute_sql(query)


def get_transactions_created_last_week(account_id: str):
    """
    Get total transaction amounts and top spending categories for the last 7 days.

    Args:
        account_id (str): The unique identifier of the account.

    Returns:
        Dict: Contains total sum, amount spent, amount received, and top spending category with amount and currencies.
    """
    query = f"""
        WITH last_week_transactions AS (
            SELECT *
            FROM new_table
            WHERE created_at >= current_date - interval '7 days'
              AND account_id = '{account_id}'
        ),
        top_spending_category AS (
            SELECT 
                category,
                SUM(amount) as spent_amount,
                currency
            FROM last_week_transactions
            WHERE transaction_type ILIKE '%debit%'
            GROUP BY category, currency
            ORDER BY spent_amount DESC
            LIMIT 1
        ),
        totals AS (
            SELECT 
                SUM(amount) as total_sum,
                SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) as total_spent,
                SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) as total_received,
                currency
            FROM last_week_transactions
            GROUP BY currency
            ORDER BY total_sum DESC
            LIMIT 1
        )
        SELECT 
            COALESCE(total_sum, 0) as total_sum,
            (SELECT currency FROM totals) as total_currency,
            COALESCE(total_spent, 0) as total_spent,
            (SELECT currency FROM totals) as spent_currency,
            COALESCE(total_received, 0) as total_received,
            (SELECT currency FROM totals) as received_currency,
            (SELECT category FROM top_spending_category) as highest_spend_category,
            (SELECT spent_amount FROM top_spending_category) as highest_spend_amount,
            (SELECT currency FROM top_spending_category) as highest_spend_currency
        FROM totals;
    """
    return execute_sql(query)


def get_transactions_by_keyword(keyword: str, account_id: str):
    """
    Get credit amount, debit amount and total sum with their currencies for transactions matching a keyword
    in bank_name, category, or transaction_type (in that order).

    Args:
        keyword (str): Keyword to search across bank_name, category and transaction_type columns
        account_id (str): The user's account ID to scope the query

    Returns:
        Dict: A dictionary containing credit_amount, debit_amount and total_amount with currencies for matches
    """
    query = f"""
        SELECT
            SUM(CASE WHEN transaction_type ILIKE '%credit%' THEN amount ELSE 0 END) AS credit_amount_{keyword},
            SUM(CASE WHEN transaction_type ILIKE '%debit%' THEN amount ELSE 0 END) AS debit_amount_{keyword}, 
            SUM(amount) AS total_amount_{keyword},
            MAX(currency) as currency
        FROM new_table
        WHERE account_id = '{account_id}'
          AND (
              bank_name ILIKE '%{keyword}%' OR
              category ILIKE '%{keyword}%' OR
              transaction_type ILIKE '%{keyword}%'
          )
        GROUP BY currency
        ORDER BY total_amount_{keyword} DESC
        LIMIT 1;
    """
    return execute_sql(query)
