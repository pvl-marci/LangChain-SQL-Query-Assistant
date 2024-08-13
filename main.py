from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain, SQLDatabaseSequentialChain
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv('.env')

# Access the variables
host = os.environ.get('HOST')
port = os.environ.get('PORT')
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
database = os.environ.get('DATABASE')
open_ai_key = os.environ.get('OPEN_AI_KEY')

# Connection
pg_uri = f"postgresql+psycopg2://{username}:{
    password}@{host}:{port}/{database}"
db = SQLDatabase.from_uri(pg_uri)


llm = ChatOpenAI(temperature=0, openai_api_key=open_ai_key,
                 model_name='gpt-3.5-turbo')


PROMPT = """ 
Given an input question, first create a syntactically correct postgresql query to run,  
then look at the results of the query and return the answer.  
The question: {question}
"""

db_chain = SQLDatabaseChain(
    llm=llm, database=db, verbose=True, top_k=3)

question = "Entwicklung der Verkäufe von 'Retail and food services sales, total'"
# use db_chain.run(question) instead if you don't have a prompt
db_chain.run(PROMPT.format(question=question))
