from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import constants
from constants import transform_input
import streamlit as st
import backoff
import openai

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def transform(trading_strategy):    

    model = ChatOpenAI(
        temperature=0.3,  # increase temperature to get more creative answers
        model_name='gpt-4o-mini'  # change this to 'gpt-4' if you have access
    )

    # Create a PromptTemplate
    answer_prompt = PromptTemplate(
        input_variables=["trading_strategy"],
        template= transform_input
    )
    # Create the LLMChain with the model and prompt
    llm_chain = answer_prompt | model

    # Define the input values
    input_values = {
        "trading_strategy": trading_strategy
    }

    # Run the LLMChain with the inputs
    response = llm_chain.invoke(input_values).content

    return response

if __name__ == "__main__":

    # # Input your trading strategies here
    # QUERY = "Long stock with the most solid increase of defer revenue, short vice versa, when the leverage ratio is low"

    # response = transform(QUERY)
    st.title('Alpha Generator from Trading Strategies')

    # Text input for trading strategy
    trading_strategy = st.text_area('Enter your trading strategy:', height=200)

    # Submit button
    if st.button('Generate Alphas'):
        if trading_strategy:
            with st.spinner('Processing...'):
                try:
                    # Pass the input strategy to the make_chain function
                    datafield_dict = transform(trading_strategy)

                    # Display the datafield_dict (JSON format)
                    st.write("### Relevant Datafields:")
                    st.write(datafield_dict)  # Display the JSON response in structured format
                except: 
                    st.write("The system is overload, please try again")           
        else:
            st.error('Please enter a trading strategy before generating alphas.')
