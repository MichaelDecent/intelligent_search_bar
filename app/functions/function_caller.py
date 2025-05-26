import inspect
import json
import logging
from typing import Any, Callable, Dict

from openai import OpenAI
from pydantic import create_model

from app.config import OPENAI_API_KEY
from app.database import sql_queries

FUNCTION_MAP: Dict[str, Callable] = {
    "get_recent_transactions": sql_queries.get_recent_transactions,
    "get_current_balance": sql_queries.get_current_balance,
    "get_all_transactions": sql_queries.get_all_transactions,
    "get_transactions_by_date": sql_queries.get_transactions_by_date,
    "get_transactions_between_dates": sql_queries.get_transactions_between_dates,
    "get_transactions_last_month": sql_queries.get_transactions_last_month,
    "get_transactions_over": sql_queries.get_transactions_over,
    "get_transactions_below": sql_queries.get_transactions_below,
    "get_deposits": sql_queries.get_deposits,
    "get_withdrawals": sql_queries.get_withdrawals,
    "get_transactions_by_category": sql_queries.get_transactions_by_category,
    "get_transactions_by_account_number": sql_queries.get_transactions_by_account_number,
    "get_transactions_by_bank_name": sql_queries.get_transactions_by_bank_name,
    "get_transactions_by_account_id": sql_queries.get_transactions_by_account_id,
    "get_transactions_by_currency": sql_queries.get_transactions_by_currency,
    "get_withdrawals_over_last_days": sql_queries.get_withdrawals_over_last_days,
    "get_transactions_by_bank_and_category": sql_queries.get_transactions_by_bank_and_category,
    "get_transactions_between_amounts_and_category": sql_queries.get_transactions_between_amounts_and_category,
    "get_transactions_updated_since": sql_queries.get_transactions_updated_since,
    "get_transactions_created_last_week": sql_queries.get_transactions_created_last_week,
    "get_transactions_by_keyword": sql_queries.get_transactions_by_keyword,
}

client = OpenAI(api_key=OPENAI_API_KEY)
logger = logging.getLogger(__name__)


def generate_function_schema(func: Callable) -> Dict[str, Any]:
    """
    Automatically generate a JSON schema for the parameters of a function
    using its signature and type hints.
    """
    sig = inspect.signature(func)
    fields = {}
    required = []

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        annotation = (
            param.annotation if param.annotation is not inspect.Parameter.empty else str
        )

        if param.default is inspect.Parameter.empty:
            default = ...
            required.append(name)
        else:
            default = param.default

        fields[name] = (annotation, default)

    Model = create_model(func.__name__ + "Parameters", **fields)  # type: ignore
    schema = Model.model_json_schema()

    return {
        "type": "object",
        "properties": schema.get("properties", {}),
        "required": required,
    }


def generate_functions_list() -> list:
    """
    Automatically generate the list of function definitions for OpenAI
    based on the FUNCTION_MAP. The description is taken from the function's
    docstring (if provided), and the parameters are generated automatically.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": func_name,
                "description": func.__doc__
                or f"Automatically generated function for {func_name}.",
                "parameters": generate_function_schema(func),
            },
        }
        for func_name, func in FUNCTION_MAP.items()
    ]


def call_function_by_name(function_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Given a function name and its arguments, look up the corresponding function
    from FUNCTION_MAP and call it with the provided arguments.
    """
    if function_name not in FUNCTION_MAP:
        raise ValueError(f"Function {function_name} is not defined in the mapping.")

    func = FUNCTION_MAP[function_name]

    try:
        result = func(**arguments)
    except Exception as e:
        result = {"error": str(e)}

    return result


def generate_nl_response(function_result: dict) -> str:
    """
    Generate a natural language summary based on the raw function result.

    Args:
        function_result (dict): The result from a function call (e.g., SQL query result).

    Returns:
        str: A natural language summary of the data.
    """
    prompt = (
        "You are a Financial Insight Analyst. Given the following financial data,"
        "provide a concise 2-3 sentence summary, addressing the user as 'you'.\
        Focus on key insights and avoid overly technical language.\n\n"
        "Financial Data:\n"
        "--------------------------------------------------\n"
        f"{function_result}\n"
        "--------------------------------------------------\n\n"
        "Please provide your summary."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Financial Insight Analyst."},
            {"role": "user", "content": prompt},
        ],
    )

    nl_response = response.choices[0].message.content
    logger.info(nl_response)
    return nl_response


def openai_function_call(user_query: str, account_id: str) -> Dict[str, Any]:
    """
    Send the user query to OpenAI with function calling enabled, parse the function
    call response, and execute the corresponding Python function.

    Args:
        user_query (str): The natural language query from the user.
        account_id (str): The user's account ID to scope the query.

    Returns:
        Dict[str, Any]: Dictionary containing the function call results or direct response
    """
    tools = generate_functions_list()

    messages = [
        {"role": "user", "content": user_query},
        {
            "role": "system",
            "content": "You are a financial assistant. Given a keyword, call 'get_transactions_by_keyword'\
            to fetch relevant transactions. Automatically correct grammar in user queries.",
        },
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4", messages=messages, tools=tools, tool_choice="auto"
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]  # Get first tool call
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            arguments["account_id"] = account_id

            result = call_function_by_name(function_name, arguments)

            logger.debug(
                {
                    "called_function": function_name,
                    "arguments": arguments,
                    "result": result,
                }
            )

            nl_response = generate_nl_response(result)

            return {"nl_response": nl_response}
        else:
            return {"nl_response": message.content}

    except Exception as e:
        raise Exception(f"Error during OpenAI API call: {str(e)}")
