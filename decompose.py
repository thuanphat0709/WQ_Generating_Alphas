from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import constants
from constants import factors_decompose
import backoff
import openai

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def decompose(trading_strategy):    

    model = ChatOpenAI(
        temperature=0.3,  # increase temperature to get more creative answers
        model_name='gpt-4o-mini'  # change this to 'gpt-4' if you have access
    )

    # Create a PromptTemplate
    answer_prompt = PromptTemplate(
        input_variables=["trading_str"],
        template= factors_decompose
    )
    # Create the LLMChain with the model and prompt
    llm_chain = answer_prompt | model

    # Define the input values
    input_values = {
        "trading_str": trading_strategy
    }

    # Run the LLMChain with the inputs
    response = llm_chain.invoke(input_values).content

    return response

if __name__ == "__main__":

    # Input your trading strategies here
    QUERY = "Long stocks with high leverage, short vice versa, when the stocks are blue chips"

    response = decompose(QUERY)
    # result = list(response)
    print(response)
