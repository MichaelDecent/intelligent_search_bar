# app/routes.py

import re
from fastapi import APIRouter, HTTPException

from app.functions.function_caller import openai_function_call
from app.schema.user import UserQuery, UserResponse

router = APIRouter()


@router.post("/ai-search", response_model=UserResponse)
async def ai_search(user_query: UserQuery):
    try:
        result = openai_function_call(user_query.query, user_query.account_id)
        return UserResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
