from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from api.tools import OpenWeatherMapQuery
from templates import SYSTEM_PROMPT

load_dotenv()


def setup_agent(model: str = "gpt-3.5-turbo", temperature: float = 0.8, verbose: bool = False) -> tuple:
    # Create an instance of the ChatOpenAI model
    llm = ChatOpenAI(model=model, temperature=temperature, max_retries=2, max_tokens=None, n=1, streaming=False)

    # Load the tools
    tools = [OpenWeatherMapQuery()]

    # Create a prompt template for the chatbot
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # Create a memory object to store the chat history
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Construct the Tools agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=True,
        memory=memory,
        max_iterations=3,
    )

    return agent_executor, tools


def query_llm(agent, question: str, return_history: bool = False) -> dict | str:
    ai_response = agent.invoke({"input": question})
    if return_history:
        return ai_response
    return ai_response["output"]
