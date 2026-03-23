from langchain_groq import ChatGroq

# FIX 1: TavilySearchResults deprecated in LangChain 0.3.25.
# OLD ❌: from langchain_community.tools.tavily_search import TavilySearchResults
# NEW ✅: from langchain_tavily import TavilySearch
from langchain_tavily import TavilySearch

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage

from app.config.settings import settings


def get_response_from_ai_agent(llm_id, query, allow_search, system_prompt):
    llm = ChatGroq(model=llm_id)

    # FIX 1 (continued): TavilySearch replaces TavilySearchResults
    tools = [TavilySearch(max_results=2)] if allow_search else []

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )

    # FIX 2: query arriving here was a List[str] from the API (request.messages),
    # but HumanMessage expects a single string.
    # Convert list to a single string by joining with newlines.
    if isinstance(query, list):
        query = "\n".join(query)

    state = {"messages": [HumanMessage(content=query)]}

    response = agent.invoke(state)

    messages = response.get("messages", [])
    ai_messages = [msg.content for msg in messages if isinstance(msg, AIMessage)]

    return ai_messages[-1]