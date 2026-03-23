from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from app.core.ai_agent import get_response_from_ai_agent
from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="MULTI AI AGENT")


class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]
    allow_search: bool


@app.post("/chat")
def chat_endpoint(request: RequestState):
    logger.info(f"Received request for model : {request.model_name}")

    if request.model_name not in settings.ALLOWED_MODELS_NAME:
        logger.warning("Invalid model name")
        raise HTTPException(status_code=400, detail=f"Invalid model name '{request.model_name}'. Allowed: {settings.ALLOWED_MODELS_NAME}")

    try:
        # FIX 3: Arguments were passed in the WRONG ORDER — this was the
        # primary cause of the 400 Bad Request error.
        #
        # Function signature:
        #   get_response_from_ai_agent(llm_id, query, allow_search, system_prompt)
        #
        # OLD (wrong) ❌:
        #   get_response_from_ai_agent(
        #       request.model_name,   → llm_id       ✅
        #       request.system_prompt → query         ❌ system prompt sent as query
        #       request.messages,     → allow_search  ❌ List[str] passed as bool
        #       request.allow_search  → system_prompt ❌ bool passed as system prompt
        #   )
        #
        # NEW (correct) ✅: match the order defined in ai_agent.py
        response = get_response_from_ai_agent(
            llm_id=request.model_name,
            query=request.messages,
            allow_search=request.allow_search,
            system_prompt=request.system_prompt,
        )

        logger.info(f"Successfully got response from AI Agent {request.model_name}")
        return {"response": response}

    except Exception as e:
        # FIX 4: Original except block swallowed the real error — logged only
        # "Error occurred during response generation" with no detail, making
        # debugging impossible. Now logs the actual exception message.
        logger.error(f"Error occurred during response generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")