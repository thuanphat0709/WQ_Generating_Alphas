import os
from langchain_community.document_loaders import CSVLoader, TextLoader, UnstructuredExcelLoader, Docx2txtLoader
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredMarkdownLoader

os.environ["OPENAI_API_KEY"] = 'MY_API_KEY'

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
directory = "docs"
a = os.listdir(directory)
# Define the folder for storing database
SOURCE_DIRECTORY = f"{ROOT_DIRECTORY}/SOURCE_DOCUMENTS"

PERSIST_DIRECTORY = f"{ROOT_DIRECTORY}/DB"

MODELS_PATH = "./models"

# Can be changed to a specific number
INGEST_THREADS = min(os.cpu_count(),8)

DOCUMENT_MAP = {
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
    ".py": TextLoader,
    # ".pdf": PDFMinerLoader,
    ".pdf": PyMuPDFLoader,
    ".csv": CSVLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
}

query = """
    Shorts stocks with high liabilities-to-equity ratio and long stocks with low leverages 
"""
query_test  = '''
buying a stock when its price falls 2 standard deviations below its 50-day moving average and selling it when the price reverts back to the moving average
'''

transform_input = '''
You are an expert in quantitative investment, specializing in arbitrage-based trading strategies. 
Transform the following input into a trading strategy format by understanding the user's input, understanding the indicators (factors used to deliver signal of alpha) and classifying it based on the rules below. 

Important:
If the input suggests a moderate extremity of a condition, use "when".
If the input suggests a high degree of extremity, use "if".
User can mention the condition as: when/if [condition] --> implement alpha, or when/if [condition] of stocks --> set higher alpha signal,.... You can detect the [condition] from that

1. If the input suggests that indicators are higher or lower relative to other stocks, format the output as:
"Long/short stocks with [adj_1] [indicator_1] (and [adj_2] [indicator_1], etc.), short/long vice versa, (when/if [condition] --> optional)."
Example: "Long stocks with high P/E ratios and low debt-to-equity, short vice versa, when growth rates are stable."

2. If the input suggests that an indicator is on an accelerating or declining trend, format the output as:
"Long/short stocks with increasingly/decreasingly [adj] [indicator_1],short/long vice versa,  (when/if [condition] --> optional)."
Example: "Short stocks with increasingly high earnings growth, long vice versa, if market sentiment improves."

3. If the input suggests abnormal values of an indicator (relative to historical data), format the output as:
"Long/short stocks with abnormally [adj] [indicator_1], short/long vice versa, (when/if [condition] --> optional)."
Example: "Short stocks with abnormally high volume, long vice versa, when volatility spikes."

4. If the user's input does not align clearly with the above rules or is difficult to categorize, transform it into the following general format:
"Long/short stocks with [signal_1], short/long vice versa, (when/if [condition] --> optional)."
Ensure that all indicators mentioned by the user are included, even if they seem to be related or overlapping

5. If the condtion of input suggests moderate extremity of a condition, format the output as:
"Long/short [signal], short/long vice versa, when [condition]."
Example: "Long stocks with high capitalization, short vice versa, when interest rates are moderately low."

6. If the condition of input suggests a high degree of extremity, or use what to trade more with signal, format the output as:
"Long/short [signal], short/long vice versa, if [condition]."
Example: "Short stocks with high risk to compensate for higher return, if bond yields drop sharply."

Please note that the "when/if" condition is optional and should only be included if the user input provides it (usually go with when, if, trade more, stop trade, etc). Do not make up conditions if they are not explicitly mentioned by the user.
A condition should not too similar to the indicators
Keep all the indicators in user input, even though they can be reasons to each others, try to wisely collaborate them, do not drop
If the input is not about trading, or investment, please return [NONE] only
For example: 
Input: "I like ice-cream" or "The president of the USA is Donald Trumpt"
Output: "NONE"
Here is the user input: {trading_strategy}
You must only output your transformed version, not thing more
'''

factors_decompose = '''
You are expert in decomposing a text of trading strategy into a list of basic factors. 
Factors are the basic quantitative datafields used to formulate the trading strategies.  
To decompose, you can use your domain knowledge of finance and investment to understand the trading strategy, quantitative factors needed to calculate it, 
You must breakdown of factors to the most basic, and use your domain knowledge of finance and investment to find more relative factors that can be quantify, and to diversify your understanding of the strategy to find even more factors. 
Do not include too general factors that can not be quantify like: ["fundamental analysis", "good stocks", "blue chips stock"] but rather try to find relevant quantitative factors represent those. 

Here are examples:

Input: "Long stock with high earning yield, short vice versa"
Output: ["Earning Yield", "Earning per Share", "EBITDA", "Price per Share", "P/E ratio", "Cash Flow Yield", "Free Cash Flow (FCF)", "P/CF (Price to Cash Flow Ratio)", "Enterprise Value (EV)"]

Input: "Long stock with low debt to equity ratio, short vice versa, when the volume is high"
Output: ["debt to equity ratio", "debt to asset ratio", "debt", "liabilities", "net debt", "equity", "Return on Equity (ROE)", "volume"]

Input: "Long on a stocks with high systematic risk, short vice versa, when the company's fundamentals are strong with low debt and high free cash flow"
Output: ["systematic risk", "beta", "market risk premium", "debt to equity ratio", "debt to asset ratio", "net debt", "liabilities", "equity", "free cash flow (FCF)", "operating cash flow", "return on equity (ROE)", "return on assets (ROA)", "current ratio"]

Here is our input, your output must only be the list: 
Input: {trading_str}
Output: 

'''


input_query_datafield = '''
You are expert in finding dataset names including the given factors about trading strategies. You are now given a list of factors of trading strategies, task is to identify the list of dataset names from the following list that are best relates to the strategy factors: 

- FUNDAMENTAL: includes quarterly/semiannual/yearly companies financial statements (Balance sheet, PnL, CashFlow statement) items, industry specific data, corporate governance data, and updates on quarterly basis.
- PRICE_VOLUME: containing price, volume, close, open, high price, low price, number of shares,market capitaliztion and related information related to market of each stock.
- MODEL: factors in 6 categories: Valuation, Growth, Profitability, Momentum, Quality, Risk. For example looking at valuation → metrics such as price to earnings, price to book value, discount rates…. 
- OPTION: This dataset has various estimates of Options Volatility data and other metrics like Volatility, Slope of strike skew and derivative of the strike skew., put/call ratios, forward prices, and options breakevens at different horizon. It also has relationships with SPY and other ETFs that can be used to forecast volatility.
- ANALYST: This dataset provides opinions from analysts about the futures, information about company financial updates before and after earning announcements.
- SOCIAL_MEDIA:  sentiment data with different sentiment and volume on social media, news and opinions for financial markets such as tweets or twitter messages.


Instructions:
From the given list of factors, you will identify which datasets will include these factors. Then, you put the chosen dataset name to a list and output that list. If you confuse between 2 datasets when categorize a factor, please include both. 

Example:

Input: ["liabilities-to-equity ratio",  "cash", "assets"]
Output: "liabilities-to-equity ratio": ["FUNDAMENTAL"], "cash": ["FUNDAMENTAL"], ""assets": ["FUNDAMENTAL"]

Input: ["open prices", "returns"]
Output: "open prices": ["PRICE_VOLUME"] , "returns": ["PRICE_VOLUME"]

Input: ["open_prices", "profit after tax"]
Output: "open_prices": ["PRICE_VOLUME"], "profit after tax": ["FUNDAMENTAL"]

Input: ["estimated/forecasted/projected profit", "implied volatility"]
Output: "estimated/forecasted/projected profit": ["ANALYST", "MODEL"], "implied volatility": ["OPTION"]

Input: ["sentiment volume", "Market Capitalization"]
Output: "sentiment volume":  ["SOCIAL_MEDIA"], "Market Capitalization": ["PRICE_VOLUME", "FUNDAMENTAL"]

Input: ["liabilities", "Beta to SPY", "Unsystematic Risk"]
Output: "liabilities": ["FUNDAMENTAL"], "Beta to SPY":  ["MODEL"], "Unsystematic Risk": ["MODEL"]

Input: ["Dividend per share projection for FY10", "SG&A expense", "Adjusted Earnings projection"]
Output: "Dividend per share projection for FY10": ["MODEL", "ANALYST"], "SG&A expense": ["FUNDAMENTAL"], "Adjusted Earnings projection": ["MODEL", "ANALYST"]

The output must only be the dictionary with keys are factors and values are dataset names
Please drop the ```json and ``` or any strange thing to make it a real json
Input query: {factors}
Output: 
'''

SYSTEM_PROMPT = '''
    You are an expert quantitative finance investment researcher, excelling in generating alphas with Fast Expression Language. 
    Alpha is a mathematical model used to assign different weights to various stocks, create a market neutral portfolio on US stocks. When alpha, composed of datafields, operators, and constants, is given, it is evaluated for each stock to create a portfolio (a vector of weights), repeating this process daily.	
    Here is the overview of Fast Expression Language: “Fast expression” is a proprietary programming language, designed to write and test financial models. The language can be thought as a form of pseudo code using natural language and simple programming constructs to convey clearly and concisely logic of the algorithm. Just like how an English sentence consists of a subject, verb and object; Fast expression can include datafields, operators and numerical values.	
    A datafield is a named element within a dataset that represents specific information or metrics, such as stock prices or trading volumes, accompanied by a description of its content .	
    Operators are mathematical techniques used to manipulate datafields for implementing alpha. They include such categories:
    
    Arithmetic: used for performing simple calculations:
    ['+': 'plus', '-': 'minus', '*' : 'multiply', '/': 'divide', '^': 'power', 'abs(x)': 'Absolute value of x', 'sqrt(x)': 'Square root of x']

    Logical: used to compare values to create condition or logically combine conditions: 
    ['<': 'Less than', '<=': 'Less Than or Equal', '>': 'Greater Than', '>=': 'Greater Than or Equal', '==': 'Equal', '!=': 'Not Equal', 'and(input1, input2)': 'Logical AND operator, returns true if both operands are true and returns false otherwise', 'or(input1, input2)': 'Logical OR operator returns true if either or both inputs are true and returns false otherwise']

    Conditional: modify or return values based on specified conditions: 
    [
    'trade_when (condition, signal, -1)': ' Updates alpha values only when the condition is true; if the condition is true, alpha is set to the updated signal; otherwise, it retains the previous signal', 
    'if_else(condition, signa*2, signal)' : 'Magnify the signal in a condition, returns the signal*2 if the condition is true, and returns signal if the condition is false'
    ]

    Time series: usually go with ''ts_'', used for modify weight of stocks, accompanied with look back days parameter (d) , d must be <512. 
    [
    'ts_rank(x, d)': 'rank the values of x for each instrument over the past d days, then return the rank of the current value' --> can be used for standardization (smooth the signal) for cross-sectional signal,
    'ts_zscore(x, d)': 'Z-score is a numerical measurement that describes a value's relationship to the mean of a group of values' --> can be used for standardization (smooth the signal) for cross-sectional signal,                 
    'ts_delta(x,d)': 'measure change in the value of current variable x with its d previous day value',
    'ts_mean(x, d)': 'the average value of a variable over the past d days',
    'ts_std_dev(x, d)': 'Returns standard deviation of x for the past d days'
    ]

    Cross-Sectional: perform operations across multiple stocks at each day
    [
    'rank': 'ranks the input among all the instruments and returns an equally distributed number between 0.0 and 1.0' --> can be used for standardization (smooth the signal) for cross-sectional signal,                
    'zscore(x)': 'z-score values of the stocks compared to others' --> can be used for standardization (smooth the signal) for cross-sectional signal,
    'quantile(x)': 'ranks and shifts an input Alpha vector, normalizing its values within a specified range, then applies Gaussian distribution to transform the values.' --> can be used for standardization (smooth the signal) for cross-sectional signal,
    ]

    Your input are a text of an alpha idea and a dictionary of datafields relating to that alpha idea. The format of an alpha idea is: 

    Long/short [signal([indicator])], short/long vice versa, (when/if [condition] → optional). 
    Condition is optional

    Your task is that after receive input, create a list, that has 2 python string items in the format of markdown, these 2 items are:
    1. A chain of thought to create an alpha, following the steps:
    First, understand the alpha idea to breakdown into components: indicator, signal, and condition (if provided). 
    Second, base on the alpha indicator, with given datafield dictionary and mainly Arithmetic operators, create indicator formula. 
    Third, based on the alpha signal for the indicator, choose and combine appropriate operators (such as time-series and cross-sectional operators) to transform the indicator into a signal. Important: if the indicator includes a datafield about FUNDAMENTAL or MODEL analysis, the lookback days parameter (d) of time series operator is implicitly randomly selected from this list: [60, 90, 130, 252]. If indicator involve none of those 2 types of datafields, it is randomly selected from [10, 22, 60, 120].
    (Optional) Fourth, base on alpha condition, with the Logical operators and the support of other operators, create a logical formula for condition. 
    Next step, create alpha formula, if there is no condition, alpha is the signal, if there is condition, with the Conditional operators, create alpha formula. If the condition go with 'when', use 'trade_when()', if the condition go with 'if', use 'if_else()'.
    Finally, combine everything into the final alpha formula
    2. Three creative alphas also by the same COT but by diversifying indicator interpretation, operators used in the indicator, signal, and condition. Output only: new trading strategies, justification for changes (similarity), and datafield description. No chain of thought, not thing more.
'''

USER_PROMPT = '''
Here is the trading strategy:
'{trading_strategy}'
Here is the datafield dictionary related to the trading strategy:
{datafields}
'''

OUTPUT_PARSING = """

Please transform the input string into a list of 2 string with the format like this:

[
        
        '''
        **Here is the step-by-step Chain of Thought (CoT) for creating an alpha formula based on your provided trading strategy:**
        
        **Step 1: Break Down the Alpha Idea into Components**  
        Alpha Idea:  
        - Short stocks with high investment relative to asset size, long vice versa.  
        - Condition: When the whole systematic risk of the market increases.  

        Breakdown: 
        - Indicator: The ratio of invested capital to total assets.  
        - Signal: Short stocks with higher invested capital-to-total-assets ratio.  
        - Condition: Trade only when systematic risk increases.  

        **Step 2: Define the Indicator Formula**  
        From the datafield dictionary:  
        - Invested capital is represented by `fnd6_newa1v1300_icapt` for 'Invested Capital - Total'.  
        - Total assets are represented by `fnd6_newa1v1300_at` for 'Assets - Total'.  
        
        The indicator will be the ratio of invested capital to total assets:  
        ```
        indicator = fnd6_newa1v1300_icapt / fnd6_newa1v1300_at;
        ```
        **Step 3: Define the Signal Formula**  
        Since the alpha calls for shorting stocks with high invested capital relative to total assets, we will rank the indicator using `rank()` to identify the stocks with the highest ratios. We then standardize the signal using `ts_zscore()` to smooth fluctuations, and because we are working with fundamental datafields, let's choose lookback days `d = 90`:  
        ```
        signal = ts_zscore(rank(indicator), 90);
        ```
        **Step 4: Define the Condition Formula**  
        The condition specifies that we trade when systematic risk increases. We will use the `systematic_risk_last_90_days` datafield to represent systematic risk and rank it over a 60-day period using `ts_rank()`. We will trade only when the systematic risk ranks in the top 50% of the dataset:  
        ```
        condition = ts_rank(systematic_risk_last_90_days, 60) > 0.5;
        ```
        **Step 5: Create Final Alpha Formula**  
        Since we need to apply the signal when the condition (high systematic risk) is met, we will use the `trade_when()` function to implement the logic. The final alpha formula looks like this:  
        ```
        alpha = trade_when(condition, signal, -1);
        ```
        **Step 6: Combine Everything into the Final Alpha**  
        Combine everything into the final alpha formula:  
        ```
        indicator = fnd6_newa1v1300_icapt / fnd6_newa1v1300_at;
        signal = ts_zscore(rank(indicator), 90);
        condition = ts_rank(systematic_risk_last_90_days, 60) > 0.5;
        alpha = trade_when(condition, signal, -1);
        alpha
        ```
        '''
        ,
        '''
        **Alpha 1:**
        - New Trading Strategy: Short stocks with high invested capital growth relative to asset size, long vice versa, when systematic risk last 30 days is high.
        - Justification for Change: Instead of just looking at the level of invested capital, we're focusing on the growth rate of invested capital. This provides insight into how quickly companies are investing, which can be an early indicator of overextension or underperformance relative to assets.
        - Datafields Used:
            + `fnd6_newa1v1300_icapt` (Invested Capital - Total)
            + `fnd6_newa1v1300_at` (Assets - Total)
            + `systematic_risk_last_30_days` (Systematic Risk Last 30 Days)
        ```
        indicator = ts_delta(fnd6_newa1v1300_icapt / fnd6_newa1v1300_at, 60);
        signal = ts_zscore(rank(indicator), 90);
        condition = ts_rank(systematic_risk_last_30_days, 30) > 0.6;
        alpha = trade_when(condition, signal, -1);
        alpha
        ```
        **Alpha 2:**
        - New Trading Strategy: Long stocks with total fair value assets relative to liabilities, short vice versa, when the market value decreases rapidly.
        - Justification for Change: Shifting focus to the ratio between fair value assets and total liabilities provides a better picture of a company's financial health, while using market value decrease as a trigger capitalizes on negative market sentiment.
        - Datafields Used:
            + `fnd6_tfva` (Total Fair Value Assets)
            + `fnd6_newa1v1300_lt` (Liabilities - Total)
            + `fnd6_mkvalt` (Market Value - Total)
        ```
        indicator = fnd6_tfva / fnd6_newa1v1300_lt;
        signal = ts_rank(indicator, 60);
        condition = ts_delta(fnd6_mkvalt, 30) < -0.1;
        alpha = trade_when(condition, signal, -1);
        alpha
        ```
        **Alpha 3:**
        - New Trading Strategy: Long stocks with invested capital-to-market capitalization ratio, short vice versa, when unsystematic risk last 90 days is high.
        - Justification for Change: By comparing invested capital to market capitalization, we're emphasizing market perception vs. capital investment. Unsystematic risk highlights stock-specific risk factors, which should increase alpha sensitivity.
        - Datafields Used:
            + `fnd6_newa1v1300_icapt` (Invested Capital - Total)
            + `fnd6_mkvalt` (Market Value - Total)
            + `unsystematic_risk_last_90_days` (Unsystematic Risk Last 90 Days)
        ```
        indicator = fnd6_newa1v1300_icapt / fnd6_mkvalt;
        signal = ts_zscore(rank(indicator), 120);
        condition = ts_rank(unsystematic_risk_last_90_days, 90) > 0.7;
        alpha = trade_when(condition, signal, -1);
        alpha
        ```
        '''
]

Here is the input strings, please transform its format:

{LLM_OUTPUT}

Your output is only the transformed list, not thing more. Do not return ```python
"""


