from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import constants
import json
import backoff
import openai
# Path to persist the Chroma database
PERSIST_DIRECTORY = "DB"

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def query_datafield(factors_dicts):
    
    embeddings = OpenAIEmbeddings()

    datafield_dict = {}

    for factor, databases in factors_dicts.items():
        for database in databases:
            # Load the persisted database
            db = Chroma(persist_directory=PERSIST_DIRECTORY + f"/{database}", embedding_function=embeddings)
            if database == "FUNDAMENTAL":
                results = db.similarity_search(factor, k = 8)
            elif database == "PRICE_VOLUME":
                results = db.similarity_search(factor, k = 2)
            else:  
                results = db.similarity_search(factor, k = 4)           
            # Filter out duplicates based on datafield or page_content
            unique_results = []
            seen_datafields = []

            for result in results:
                datafield = result.metadata['datafield']
                if datafield not in seen_datafields:
                    seen_datafields.append(datafield)
                    unique_results.append(result)
            for i in range(len(unique_results)):
                a = unique_results[i].metadata['datafield']
                b = unique_results[i].page_content
                datafield_dict[a] = b

    return datafield_dict

if __name__ == "__main__":

    QUERY = '''{
    "Volume": ["PRICE_VOLUME"],
    "Debt": ["FUNDAMENTAL"],
    "projected Free Cash Flow": ["MODEL", "ANALYST"]
    }'''        
    a =  query_datafield(json.loads(QUERY))
    print(a)



