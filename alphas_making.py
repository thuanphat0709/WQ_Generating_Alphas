from langchain.prompts import PromptTemplate
import json
import constants
from constants import USER_PROMPT, SYSTEM_PROMPT
from decompose import decompose
from datafield_database_query import database_query
from similarity_query import query_datafield
from transform_input import transform
from Output_transform import output_transform
import json
import streamlit as st
import openai
import ast
import backoff
import openai

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def make_openai_call(model, messages):
    return openai.chat.completions.create(model=model, messages=messages)

def make_chain(query):

    # Step 1: Decompose the query into factors and retrieve related datafields
    trans_trading_str =  transform(query)
    if trans_trading_str == "NONE":
        return 0, 0, 0
    else:
        factors = decompose(query)
        database_dict = database_query(factors)
        datafield_dict = query_datafield(json.loads(database_dict))

        # Step 2: Create a PromptTemplate for the user prompt
        answer_prompt = PromptTemplate(
            input_variables=["trading_strategy", "datafields"],
            template=USER_PROMPT
        )

        # Step 3: Generate the user prompt dynamically using the template
        user_prompt = answer_prompt.format(
            trading_strategy=query,
            datafields=datafield_dict
        )

        result = make_openai_call(
        model="ft:gpt-4o-mini-2024-07-18:personal:alphas-making:A6wfiORm",
        messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
        )

        response = result.choices[0].message.content
        result_1, result_2 = output_transform(response)

        return result_1, result_2, datafield_dict

# Streamlit app structure
def main():
    st.title('Alpha Generator from Trading Strategies')

    # Text input for trading strategy
    trading_strategy = st.text_area('Enter your trading strategy:', height=200)

    # Submit button
    if st.button('Generate Alphas'):
        if trading_strategy:
            with st.spinner('Processing...'):
                try:
                    # Pass the input strategy to the make_chain function
                    response, datafield_dict = make_chain(trading_strategy)
                    st.success('Alphas and Datafields generated successfully!')
                    st.write("### Generated Alphas:")
                    st.write(response)

                    # Display the datafield_dict (JSON format)
                    st.write("### Relevant Datafields:")
                    st.json(datafield_dict)  # Display the JSON response in structured format
                except: 
                    st.write("The system is overload, please try again")           
        else:
            st.error('Please enter a trading strategy before generating alphas.')

if __name__ == "__main__":
    main()
    # query = "Long stocks with high depreciation expense, short vice versa, when the volume are high"
    # a, b = make_chain(query)
    # print(a)
