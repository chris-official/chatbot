from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.agents import load_tools
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()


def setup_agent():
    # Create an instance of the ChatOpenAI model
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    # Load the tools
    tools = [OpenWeatherMapQuery()]

    # Create a prompt template for the chatbot
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a weather assistant chatbot named Sky. Always be kind and polite to the user \
                and talk in a relaxed, casual, happy and natural manner. Your expertise is exclusively in providing \
                information and advice about anything related to the weather. This includes imformation about \
                temperature, cloud coverage, precipitation, snowfall, wind speed, and general weather-related queries. \
                You can get the information by using the OpenWeatherMap tool which provides you with a report of the \
                current weather and the daily forecasts for the next 7 days for the requested location. You can \
                use this information as context to write your response to the user. Make sure to not overwhelm the user \
                with every detail unless you are asked to do so. Focus on the users requested information and the most \
                important weather infos that were mentioned earlier. You should not provide information outside of \
                this scope. If a question is not about weather, kindly decline and hint towards your specialization in \
                weather related queries.",
            ),
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
        verbose=True,
        handle_parsing_errors=True,
        memory=memory,
        max_iterations=3,
    )

    return agent_executor


def query_llm(agent, question):
    ai_response = agent.invoke({"input": question})
    return ai_response


if __name__ == "__main__":
    agent = setup_agent()
    while True:
        user_input = input("You: ")
        response = query_llm(agent, user_input)
        print(f"Sunny: {response}")
