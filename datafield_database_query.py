from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from constants import input_query_datafield
import backoff
import openai

QA_TEMPLATE = input_query_datafield

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def database_query(factors):    

    model = ChatOpenAI(
        temperature=0.1,  # increase temperature to get more creative answers
        model_name='gpt-4o-mini'  # change this to 'gpt-4' if you have access
    )

    # Create a PromptTemplate
    answer_prompt = PromptTemplate(
        input_variables=["factors"],
        template=QA_TEMPLATE
    )
    # Create the LLMChain with the model and prompt
    llm_chain = answer_prompt | model

    # Define the input values
    input_values = {
        "factors": factors
    }

    # Run the LLMChain with the inputs
    response = llm_chain.invoke(input_values).content

    return response


if __name__ == "__main__":

    trading_str = '''
                    ["Quality"]
                '''
    response = database_query(trading_str)
    print(response)
