import streamlit as st
import random
from alphas_making import make_chain

def main():
    st.title('Alpha Generator from Trading Strategies')

    # Inject custom CSS for styling the "Examples" button
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: green;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # List of example trading strategies
    example_strategies = [
        "Example Trading Strategy: \nLong stocks with abnormally high expected future volatility, short vice versa, if trading turnover is low relative to market cap.",
        "Example Trading Strategy: \nLong stocks with high price declines over the previous 5 days, short vice versa, if trading more on high leverage companies.",
        "Example Trading Strategy: \nShort stocks with relatively high social media discussion, long vice versa, if trading volume is unexpectedly high.",
        "Example Trading Strategy: \nLong stocks with large fund spent for employee pension, short vice versa"
        "Example Trading Strategy: \nLong stocks with high potential for dividend payment, short vice versa, when the company is growing fast"
        "Example Trading Strategy: \nLong stocks with high put open interest relative to call open interest, short vice versa.",
        "Example Trading Strategy: \nLong stocks with high invested capital, short vice versa, when the volume is high"
        "Example Trading Strategy: \nLong stocks with high cash flow relative to liabilities, short vice versa, when the company is growing fast."
    ]

    # Initialize session state to store the trading strategy
    if "example_strategy" not in st.session_state:
        st.session_state.example_strategy = ""

    # Button to fill example strategy
    if st.button('Examples'):
        st.session_state.example_strategy = random.choice(example_strategies)

    # Text input for trading strategy with pre-filled example if the 'Example' button is clicked
    trading_strategy = st.text_area('Enter your trading strategy:', 
                                    height=200, 
                                    value=st.session_state.example_strategy)

    # Submit button
    if st.button('Generate Alphas'):
        if trading_strategy:
            with st.spinner('Processing... about 20 second'):
                try:
                    # Example response placeholder
                    response_1, response_2, datafield_dict = make_chain(trading_strategy)  # Replace with actual alpha generation logic
                    if response_1 == 0: 
                        st.error('Please enter a correct trading strategy before generating alphas.')
                    else:
                        st.success('Alphas generated successfully!')
                        st.balloons()
                        
                        # Display the Chain of Thought
                        st.write("### Chain of Thought for creating Alpha formula")
                        st.write(response_1)  

                        # Display the Innovative Alphas
                        st.write("### Innovative Alphas from original idea")
                        st.write(response_2)
                        
                        # Display the datafield_dict (JSON format)
                        st.write("### Relevant Datafields:")
                        st.json(datafield_dict)  # Display the JSON response in structured format
                except: 
                    st.write("The system is overloaded, please try again.")           
        else:
            st.error('Please enter a trading strategy before generating alphas.')

if __name__ == "__main__":
    main()