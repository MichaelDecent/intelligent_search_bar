# app/ai_function_caller.py

import inspect
import json
from pprint import pprint
from typing import Any, Callable, Dict

from openai import OpenAI
from pydantic import create_model

from app.config import OPENAI_API_KEY
from app.database import sql_queries

# Mapping from function names to actual functions
FUNCTION_MAP: Dict[str, Callable] = {
    "get_last_5_transactions": sql_queries.get_last_5_transactions,
    "get_current_balance": sql_queries.get_current_balance,
    "get_all_transactions": sql_queries.get_all_transactions,
    "get_transactions_by_date": sql_queries.get_transactions_by_date,
    "get_transactions_between_dates": sql_queries.get_transactions_between_dates,
    "get_transactions_last_month": sql_queries.get_transactions_last_month,
    "get_transactions_over": sql_queries.get_transactions_over,
    "get_transactions_below": sql_queries.get_transactions_below,
    "get_transactions_by_exact_amount": sql_queries.get_transactions_by_exact_amount,
    "get_deposits": sql_queries.get_deposits,
    "get_withdrawals": sql_queries.get_withdrawals,
    "get_transactions_by_category": sql_queries.get_transactions_by_category,
    "get_transactions_by_narration_keyword": sql_queries.get_transactions_by_narration_keyword,
    "get_transactions_by_account_number": sql_queries.get_transactions_by_account_number,
    "get_transactions_by_bank_name": sql_queries.get_transactions_by_bank_name,
    "get_transactions_by_account_id": sql_queries.get_transactions_by_account_id,
    "get_transactions_by_mono_connection_id": sql_queries.get_transactions_by_mono_connection_id,
    "get_transactions_by_currency": sql_queries.get_transactions_by_currency,
    "get_transaction_by_transaction_id": sql_queries.get_transaction_by_transaction_id,
    "get_last_transaction_narration_and_amount": sql_queries.get_last_transaction_narration_and_amount,
    "get_withdrawals_over_last_days": sql_queries.get_withdrawals_over_last_days,
    "get_transactions_by_bank_and_category": sql_queries.get_transactions_by_bank_and_category,
    "get_transactions_between_amounts_and_category": sql_queries.get_transactions_between_amounts_and_category,
    "get_transactions_updated_since": sql_queries.get_transactions_updated_since,
    "get_transactions_created_last_week": sql_queries.get_transactions_created_last_week,
}

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_function_schema(func: Callable) -> Dict[str, Any]:
    """
    Automatically generate a JSON schema for the parameters of a function
    using its signature and type hints.
    """
    sig = inspect.signature(func)
    fields = {}
    required = []

    # Iterate over function parameters.
    for name, param in sig.parameters.items():
        # Only include parameters that are not 'self' (if any) or context-specific.
        if name == "self":
            continue

        # Determine type annotation; default to string if not provided.
        annotation = (
            param.annotation if param.annotation is not inspect.Parameter.empty else str
        )

        # Mark the field as required if there is no default.
        if param.default is inspect.Parameter.empty:
            default = ...
            required.append(name)
        else:
            default = param.default

        fields[name] = (annotation, default)

    # Create a temporary Pydantic model to generate a JSON schema.
    Model = create_model(func.__name__ + "Parameters", **fields)  # type: ignore
    schema = Model.model_json_schema()

    # The JSON Schema for function parameters should be under the 'properties' key.
    # OpenAI expects the schema to be an object type.
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
    functions = []
    for func_name, func in FUNCTION_MAP.items():
        function_definition = {
            "name": func_name,
            "description": func.__doc__
            or f"Automatically generated function for {func_name}.",
            "parameters": generate_function_schema(func),
        }
        functions.append(function_definition)
    return functions


def call_function_by_name(function_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Given a function name and its arguments, look up the corresponding function
    from FUNCTION_MAP and call it with the provided arguments.
    """
    if function_name not in FUNCTION_MAP:
        raise ValueError(f"Function {function_name} is not defined in the mapping.")

    # Retrieve the function
    func = FUNCTION_MAP[function_name]

    # Call the function using unpacked arguments
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
    # Create a prompt that includes the raw result.
    prompt = (
        "You are a helpful financial assistant. Based on the following financial data, "
        "provide a concise 2-3 sentence summary addressing the user as 'you'. Focus on key insights and avoid overly technical language.\n\n"
        "The default currency is in Naira.\n"
        "Financial Data:\n"
        "--------------------------------------------------\n"
        f"{function_result}\n"
        "--------------------------------------------------\n\n"
        "Please provide your summary."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful financial assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    nl_response = response.choices[0].message.content
    print(nl_response)
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
    # Convert our functions list to OpenAI's new tools format
    tools = [
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

    # Create messages list
    messages = [{"role": "user", "content": user_query}]

    # Make API call with new format
    try:
        response = client.chat.completions.create(
            model="gpt-4", messages=messages, tools=tools, tool_choice="auto"
        )

        # Get the message from the response
        message = response.choices[0].message

        # Check if the model wanted to call a function
        if message.tool_calls:
            tool_call = message.tool_calls[0]  # Get first tool call
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Attach the user's account_id automatically.
            arguments["account_id"] = account_id

            # Call the function with the provided arguments
            result = call_function_by_name(function_name, arguments)

            pprint(
                {
                    "called_function": function_name,
                    "arguments": arguments,
                    "result": result,
                }
            )

            # Generate a natural language response based on the function result
            nl_response = generate_nl_response(result)

            return {"nl_response": nl_response}
        else:
            # If no function call was suggested, return the natural language response
            return {"nl_response": message.content}

    except Exception as e:
        raise Exception(f"Error during OpenAI API call: {str(e)}")


# if __name__ == "__main__":
#     # Example usage
#     user_query = "Hello, show me the last 5 transactions."
#     response = openai_function_call(user_query, "7807b493-fe43-4d97-b117-4298a3c24dbe")
#     print(response)

# Example usage with generate_function_schema
# print(generate_function_schema(sql_queries.get_transactions_by_date))

# Example usage with call_function_by_name
# result = print(call_function_by_name("get_last_5_transactions", {}))
