from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from database import run_query
import re

llm = init_chat_model(
    "llama-3.1-8b-instant",
    model_provider="groq",
    temperature=0,
)

# Global storage for last executed SQL
last_executed_query = None

# Define SQL Tool
@tool
def sql_runner(query: str):
    """Execute ONLY SELECT SQL queries against PostgreSQL database."""
    global last_executed_query

    print(f"Executing SQL Query: {query}")
    last_executed_query = query

    if not re.match(r"^\s*select\b", query.lower()):
        return {
            "sql_query": None,
            "response": "Only SELECT queries are allowed."
        }

    result = run_query(query)

    return {
        "sql_query": query,
        "response": result
    }


system_prompt = """
You are a PostgreSQL expert.

STRICT RULES:
- Convert the user question into ONE valid PostgreSQL SELECT query.
- Call the sql_runner tool exactly once.
- Do NOT explain anything.
- Do NOT describe the result.
- The final answer must be the tool output only.
"""

# Create agent
agent = create_react_agent(
    model=llm,
    tools=[sql_runner],
    prompt=system_prompt
)


def ask_agent(question: str):
    try:
        response = agent.invoke(
            {"messages": [("user", question)]},
            config={"recursion_limit": 8}
        )

        messages = response["messages"]

        # Find the tool response directly
        for msg in reversed(messages):
            if msg.type == "tool":
                return msg.content  # This is the REAL DB result

        return {
            "sql_query": None,
            "response": "No tool response found."
        }

    except Exception as e:
        return {
            "sql_query": None,
            "response": f"Error: {str(e)}"
        }