# python -m src.search_in_receipts.talk_to_sql
import sqlite3
import json
from typing import Dict
from db.database import ReceiptDatabase
import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"src\.env")
api_key = os.getenv("GROQ_API_KEY")


class ReceiptQuerySystem:
    """
    system to ask about receipt using NLP
    """

    def __init__(self, db_name: str = "receipts.db"):
        self.db = ReceiptDatabase(db_name)
        self.db_name = db_name

    def get_database_schema(self) -> str:
        """
        Returns the database schema description for the LLM.
        """
        return """
        DATABASE SCHEMA
        Table: receipts
        id INTEGER PK | user_id INTEGER | store_name TEXT | receipt_number TEXT | date TEXT (free text, no STRFTIME) | currency TEXT | taxes TEXT | total_amount TEXT (CAST AS REAL for math)  | created_at TIMESTAMP

        Table: items
        id INTEGER PK | receipt_id INTEGER FK → receipts.id | item_name TEXT | quantity TEXT (CAST AS REAL for math)

        receipts 1──* items (items.receipt_id = receipts.id)

        RULES:

        total_amount, quantity, taxes: always CAST(... AS REAL) before math

        date: use LIKE patterns only, never date functions

        item_name, store_name: use LOWER() for case‑insensitive search

        NULLs: guard numeric columns with COALESCE(CAST(col AS REAL), 0)

        items.receipt_id always valid FK
        user_id scopes receipt ownership

        """

    # write it in config them call it in the prompt, and make sure to include it in the prompt.
    arabic_ambiguity_rules = {"""
        "كم فاتورتي في [place]?" means "how much is my total bill at [place]?" → USE SUM
        "كم عدد فواتيري في [place]?" means "how many receipts do I have at [place]?" → USE COUNT
        "كم فاتورة عندي في [place]?" → USE COUNT
        KEY: "فاتورتي" (my bill) = SUM. "عدد فواتير" or "كم فاتورة" (number of invoices) = COUNT."""}

    def text_to_sql(self, user_question: str, user_id: int | None = None) -> str:
        """
        Convert Arabic question to SQL query
        """
        user_scope_rule = ""
        if user_id is not None:
            user_scope_rule = f"7. The query MUST be scoped to this user only: receipts.user_id = {int(user_id)}"

        prompt = f""" You are an SQL expert for a receipts database.
        {self.get_database_schema()}

        RULES:
        1. SQLite syntax only.
        2. total_amount and quantity are TEXT → CAST(column AS REAL).
        3. Text search: LIKE with %.
        4. Check NULL before numeric ops.
        5. Return ONE SQL query only — no explanation, no markdown.
        6. JOIN only when needed.
        {user_scope_rule}

        MONTH COMPARISON RULE:
        - Never use WHERE LIKE for month comparison.
        - Always use LEFT JOIN with a months subquery.
        - Template:
        SELECT months.month_name, COALESCE(SUM(CAST(r.total_amount AS REAL)),0) AS total, r.currency
        FROM (SELECT 'January' AS month_name UNION ALL SELECT 'February' AS month_name) months
        LEFT JOIN receipts r ON (
        (months.month_name='January' AND r.date LIKE '%/01/%') OR
        (months.month_name='February' AND r.date LIKE '%/02/%')
        )
        GROUP BY months.month_name, r.currency
        - Month patterns: January='%/01/%', February='%/02/%', ..., November='%/11/%', December='%/12/%'
        - Always include slashes before and after month number.
        - Always include currency in SELECT and GROUP BY.
        ARABIC AMBIGUITY RULE: {self.arabic_ambiguity_rules}
        - store_name search: use CASE WHEN user asks Arabic category, match common patterns or check actual data first
       

        {user_question}
        SQL:"""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }
            )

            response.raise_for_status()
            data = response.json()

            sql_query = data["choices"][0]["message"]["content"].strip()
            sql_query = sql_query.replace("```sql", "").replace("```", "")
            sql_query = sql_query.replace("SQL:", "").strip()

            return sql_query

        except Exception as e:
            raise Exception(f"error on generate SQL: {str(e)}")

    def execute_sql(self, sql_query: str, user_id: int | None = None) -> Dict:
        try:
            # Clean up the query
            sql_query = sql_query.strip()
            if sql_query.endswith(";"):
                sql_query = sql_query[:-1].strip()

            if not sql_query.upper().startswith("SELECT"):
                return {
                    "success": False,
                    "error": "Only SELECT queries are allowed",
                    "query": sql_query
                }

            # Check for multiple statements (actual safety check)
            statement_count = sql_query.count(";")
            if statement_count > 0:
                return {
                    "success": False,
                    "error": "Only one SELECT query is allowed",
                    "query": sql_query
                }

            lowered_query = sql_query.lower()
            blocked_tokens = ["pragma", "attach", "detach",
                              "insert", "update", "delete", "drop", "alter"]
            if any(token in lowered_query for token in blocked_tokens):
                return {
                    "success": False,
                    "error": "Unsafe SQL detected",
                    "query": sql_query
                }

            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if user_id is not None:
                safe_user_id = int(user_id)
                cursor.execute("DROP VIEW IF EXISTS temp.receipts")
                cursor.execute("DROP VIEW IF EXISTS temp.items")
                cursor.execute(
                    f"CREATE TEMP VIEW receipts AS SELECT * FROM main.receipts WHERE user_id = {safe_user_id}"
                )
                cursor.execute(
                    f"""
                    CREATE TEMP VIEW items AS
                    SELECT i.*
                    FROM main.items i
                    JOIN main.receipts r ON i.receipt_id = r.id
                    WHERE r.user_id = {safe_user_id}
                    """
                )

            cursor.execute(sql_query)
            rows = cursor.fetchall()

            conn.close()

            return {
                "success": True,
                "data": [dict(row) for row in rows],
                "count": len(rows),
                "query": sql_query
            }

        except sqlite3.Error as e:
            return {
                "success": False,
                "error": str(e),
                "query": sql_query
            }

    def format_answer(self, user_question: str, sql_results: Dict) -> str:
        if not sql_results.get("success"):
            return sql_results.get("error", "Unknown error")

        rows = sql_results.get("data", [])

        if not rows:
            return json.dumps(
                {
                    "result_type": "empty",
                    "data": [],
                },
                ensure_ascii=False,
                indent=2,
            )

        if len(rows) == 1 and len(rows[0]) == 1:
            value = list(rows[0].values())[0]
            return json.dumps(
                {
                    "result_type": "scalar",
                    "data": rows[0],
                    "value": value,
                },
                ensure_ascii=False,
                indent=2,
            )

        return json.dumps(
            {
                "result_type": "table",
                "data": rows,
            },
            ensure_ascii=False,
            indent=2,
        )

    def format_sql_answer(self, question: str, sql_results: Dict) -> str:

        # Multiple rows -> use LLM
        prompt = f"""keep the answer concise and your role is to be a helpful assistant that formats SQL query results in a user-friendly way.
            {self.format_answer(question, sql_results)}
            i want to be the explanation of the results in a concise way, and if there are multiple rows, summarize them in a way that highlights key insights relevant to the user's question.
            i dont want to return the raw data, i want to return the insights from the data in a concise way, and if there are multiple rows, summarize them in a way that highlights key insights relevant to the user's question.
            i mean add a natural language explanation of the results.
            
            start directly with the answer, no need to repeat the question or add any extra text. just give me the answer directly.
           **ZERO RESULTS RULE:**
            If no data found for requested period, check the latest year in data:
            - Look at the dates in your results to find the newest year
            - Say: "لا توجد بيانات لـ [الفترة المطلوبة]. أحدث الإيصالات في قاعدة البيانات تعود لسنة [أحدث سنة].
            -your answer must be in Arabic.
            """

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            raise Exception(
                f"error on generate format_sql_answer: {str(e)}")

    def combined_answer(self, question: str, sql_results: Dict) -> dict:
        if not sql_results["success"]:
            return {
                "raw_data": [],
                "insight_ar": sql_results.get("error", "Unknown error"),
            }

        raw_data = sql_results.get("data", [])
        insight = self.format_sql_answer(question, sql_results)

        return {
            "raw_data": raw_data,
            "insight_ar": insight
        }
