from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import constants
from constants import OUTPUT_PARSING
import streamlit as st
import ast
import backoff
import openai

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def output_transform(output):    

    model = ChatOpenAI(
        temperature=0.1,  # increase temperature to get more creative answers
        model_name='gpt-4o-mini'  # change this to 'gpt-4' if you have access
    )

    # Create a PromptTemplate
    answer_prompt = PromptTemplate(
        input_variables=["LLM_OUTPUT"],
        template= OUTPUT_PARSING
    )
    # Create the LLMChain with the model and prompt
    llm_chain = answer_prompt | model

    # Define the input values
    input_values = {
        "LLM_OUTPUT": output
    }

    # Run the LLMChain with the inputs
    response = llm_chain.invoke(input_values).content

    result = ast.literal_eval(response)
    return result[0], result[1]

if __name__ == "__main__":

    st.title('Alpha Generator from Trading Strategies')

    # Text input for trading strategy
    trading_strategy = st.text_area('Enter your trading strategy:', height=200)

    # Submit button
    if st.button('Generate Alphas'):
        if trading_strategy:
            with st.spinner('Processing...'):
                try:
                    # Pass the input strategy to the make_chain function
                    result = output_transform(trading_strategy)
                    st.write(result)
                    st.write(f"Type of result: {type(result)}")
                    st.write(f"Raw result: {result}")

                    st.write("### Relevant Datafields:")
                    try:
                        response = ast.literal_eval(result)
                    except Exception as e: 
                        st.write(f"Error details: {e}")

                    # Display the datafield_dict (JSON format)
                    st.write("### Relevant Datafields:")
                    st.write(response[1])  # Display the JSON response in structured format
                except: 
                    st.write("The system is overload, please try again")           
        else:
            st.error('Please enter a trading strategy before generating alphas.')

