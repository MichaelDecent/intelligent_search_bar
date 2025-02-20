import pytest
from os import getenv

from app.functions.function_caller import (
    call_function_by_name,
    generate_function_schema,
    generate_functions_list,
)

ID = getenv("TEST_ID")


def test_generate_function_schema():
    # Test with a simple function
    def sample_function(param1: str, param2: int = 10):
        pass

    schema = generate_function_schema(sample_function)

    # Basic assertions
    assert isinstance(schema, dict)
    assert "type" in schema
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema

    # Check properties
    properties = schema["properties"]
    assert "param1" in properties
    assert "param2" in properties

    # Check required fields
    assert "param1" in schema["required"]
    assert "param2" not in schema["required"]  # Because it has a default value


def test_generate_functions_list():
    functions_list = generate_functions_list()

    # Basic assertions
    assert isinstance(functions_list, list)
    assert len(functions_list) > 0

    # Check structure of first function
    first_function = functions_list[0]
    assert "type" in first_function
    assert first_function["type"] == "function"
    assert "function" in first_function

    # Check function properties
    function_props = first_function["function"]
    assert "name" in function_props
    assert "description" in function_props
    assert "parameters" in function_props


def test_call_function_by_name():
    # Test with a valid function
    function_name = "get_current_balance"
    arguments = {"account_id": ID}

    result = call_function_by_name(function_name, arguments)

    # Basic assertions
    assert isinstance(result, list)

    # Test with invalid function name
    with pytest.raises(ValueError):
        call_function_by_name("non_existent_function", {})
