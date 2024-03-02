from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain import FAISS
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import openai
from pymongo import MongoClient
import os

# Set your OpenAI API key as an environment variable
os.environ["OPENAI_API_KEY"] = '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'

def process_text(text):
    # Split the text into chunks using Langchain's CharacterTextSplitter
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Convert the chunks of text into embeddings to form a knowledge base
    embeddings = OpenAIEmbeddings()
    knowledgeBase = FAISS.from_texts(chunks, embeddings)

    return knowledgeBase

def retriever(query):
    docs = knowledgebase.similarity_search(query)
    return docs

def store_feedback(query, response, additional_data):
    feedback_data = {
        "query": query,
        "response": response,
        "other_data": additional_data,
    }
    collection.insert_one(feedback_data)
    print("Feedback stored in MongoDB.")

with open("ngit.txt", 'r', encoding='utf-8') as file:
    text = file.read()
    knowledgebase = process_text(text)

conversational_memory = ConversationBufferMemory(
    memory_key="chat_history",
    k=6,
    input_key="query",
    return_messages=True,
)

template_general = """
You are a university administrator who is well aware of all the administration processes and other details of the university.
You will be provided with a query and Content. Content is the data retrieved from the database. Use it wisely wherever the query is relevant to Context.

{chat_history}

Context = {context}
query: {query}
Assistant:

"""

prompt_general = PromptTemplate(
    input_variables=["chat_history", "query", "context"],
    template=template_general
)

chain_general = LLMChain(
    llm=ChatOpenAI(temperature=0.4, model='gpt-3.5-turbo-16k', streaming=True),
    prompt=prompt_general,
    verbose=True,
    memory=conversational_memory
)

# Set your MongoDB connection details
try:
    mongo_client = MongoClient("mongodb+srv://user1:Sanchaar@cluster0.10l02sn.mongodb.net/",
                               connectTimeoutMS=30000,  # 30 seconds
                               socketTimeoutMS=30000,   # 30 seconds
                               serverSelectionTimeoutMS=30000)  # 30 seconds

    db = mongo_client["sanchaar_data"]
    collection = db["Feedbacks"]

    print("Connected to MongoDB Atlas successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")


    print("Connected to MongoDB Atlas successfully.")
def handle_issue():
    # Get issue from user
    issue = input("Please describe the issue: ")

    # Store issue in MongoDB
    store_issue(issue)

    print("Issue recorded and will be sent to the concerned authorities. Thank you.")

# Define a function to store issues in the MongoDB collection
def store_issue(issue):
    issue_data = {
        "issue": issue
    }
    db["Issues"].insert_one(issue_data)
def main():
    print("Welcome to the University Chatbot!")

    while True:
        # Get user input
        user_query = input("You: ")

        # Check if the user wants to exit
        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye! have a nice day")
            break

        # Check if the query starts with 'feedback:'
        if user_query.lower().startswith('feedback'):
            # Get feedback response
            feedback_response = input("Please provide feedback: ")
            store_feedback(user_query, feedback_response, "Additional data for feedback")
            #print("Feedback stored in MongoDB.")
        elif user_query.lower().startswith('issue'):
        # Handle issue
          handle_issue()
        else:
            # Run the language model chain
            chat_context = retriever(user_query)
            bot_response = chain_general.run(query=user_query, context=chat_context)
            print("Bot:", bot_response)
def get_retriever():
    return retriever

def get_chain_general():
    return chain_general

if __name__ == "__main__":
    main()