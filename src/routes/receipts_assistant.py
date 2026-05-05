import sys

from fastapi import APIRouter, Depends, HTTPException
from src.search_in_receipts.talk_to_sql import ReceiptQuerySystem
from src.utils.schema import QuestionRequest
from src.routes.auth_router import get_current_user, check_user_has_data
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="DEBUG")
system = ReceiptQuerySystem()
receipts_assistant_router = APIRouter(
    prefix="/api/v1/receipts_assistant", 
    tags=["receipts_assistant"]
)

@receipts_assistant_router.post("/ask_question", summary="ask about your receipts")
async def receipt_assistant(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user),
):
    logger.bind(user_id=current_user["user_id"], route="/api/v1/receipts_assistant/ask_question").info(
        "Received question"
    )

    # check if question is a valid string
    if not isinstance(request.question, str) or not request.question.strip():
        logger.bind(user_id=current_user["user_id"]).warning("Invalid question input")
        raise HTTPException(status_code=400, detail="Invalid input: question must be a non-empty string.")

    user_id = current_user["user_id"]
    receipt_count = check_user_has_data(user_id)
    if receipt_count == 0:
        return {
            "status": "no_data",
            "code": "NO_RECEIPTS",
            "message": "No receipts found for this account.",
            "actions": {
                "upload_receipt": "/api/v1/receipt_parser/upload",
                "retry": "/api/v1/receipts_assistant/ask_question",
            },
        }

    try:
            
        sql_query = system.text_to_sql(request.question, user_id=user_id)
        logger.bind(user_id=user_id).debug("Generated SQL query")
        sql_results = system.execute_sql(sql_query, user_id=user_id)
        logger.bind(user_id=user_id, success=sql_results.get("success", False)).info("SQL query executed")
                
        return {
            "status": "success",
            "code": "ANSWER_GENERATED",
            "answer": system.combined_answer(request.question, sql_results),
        }
    except Exception as e:
        logger.bind(user_id=current_user["user_id"]).exception("Error processing question")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

