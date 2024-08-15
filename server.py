from flask import Flask, request, render_template, session
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain import hub
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv('.env')

# Flask app
app = Flask(__name__)
# Replace with a unique, random string
app.secret_key = 'alksdjgalskjncalksd-asdglökasdc-asdfsw'

# Access the variables
host = os.environ.get('HOST')
port = os.environ.get('PORT')
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
database = os.environ.get('DATABASE')
open_ai_key = os.environ.get('OPEN_AI_KEY')


# Connection to the database
pg_uri = f"postgresql+psycopg2://{username}:{
    password}@{host}:{port}/{database}"
db = SQLDatabase.from_uri(pg_uri)


# Prompt template
PROMPT = """You are an agent designed to interact with a SQL database.

Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer with the value. Don't put the SQL-Query in ```. Answer in the users language.

Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting examples in the database.

Handle NULL Values correctly. If a column has NULL values, you should not return those rows in the results.

Never query for all the columns from a specific table, only ask for the relevant columns given the question.

You have access to tools for interacting with the database.

Only use the below tools. Only use the information returned by the below tools to construct your final answer.

You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.

Do NOT skip this step.

Then you should query the schema of the most relevant tables.
The question: {question}"""


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'conversation' not in session:
        session['conversation'] = []  # Initialize conversation history

    if request.method == 'POST':
        question = request.form['question']
        selected_model = request.form['selected_model']

        # Create the LLM with the selected model
        llm = ChatOpenAI(
            # hard coded cause of syntax error
            temperature=0, openai_api_key=open_ai_key, model_name=selected_model)

        # Create the database chain with the new LLM
        db_chain = SQLDatabaseChain(
            llm=llm, database=db, verbose=True, top_k=3)

        # Run the query and get the result
        result = db_chain.run(PROMPT.format(
            question=question, dialect='postgresql', top_k=3))

        # Save the question and result to the conversation history
        session['conversation'].append(
            {'question': question, 'result': result})

    return render_template('index.html', conversation=session['conversation'])


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
