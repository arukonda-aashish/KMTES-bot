from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import WebBaseLoader
#from textblob import TextBlob
from pymongo import MongoClient
import os
import smtplib

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

def notify_admin(report_type, query, response):
    """Notifies the admin about a feedback or issue report."""
    sender_email = "ksadhvinay@gmail.com"  # Replace with your email address
    recipient_email = "sravanchilla07@gmail.com"  # Replace with admin's email address
    password = "uhpg gbom eeem pvwu"  # Replace with your email password
    print("Sender email:", sender_email)
    print("Password (masked):", "*" * len(password))

    subject = f"New {report_type} Reported to Chatbot"
    body = f"""
    A new {report_type} has been reported to the chatbot:

    Query: {query}
    Response: {response}

    Please review and take necessary actions.
    """

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, f"Subject: {subject}\n\n{body}")
        
def store_feedback(query, response):
    feedback_data = {
        "query": query,
        "response": response
    }
    feedback_collection.insert_one(feedback_data)
    print("Feedback stored in MongoDB.")

def store_issue(query, response):
    issue_data = {
        "query": query,
        "response": response
    }
    issues_collection.insert_one(issue_data)
    print("Issue stored in MongoDB.")

# Use WebBaseLoader to load data from the specified URL
urls = ["https://ngit.ac.in/", "https://ngit.ac.in/administration-main-menu/"]
data_list = []
for url in urls:
    loader = WebBaseLoader(url)
    data = loader.load()
    data_list.append(data)


# Process the loaded data
knowledgebase = process_text(str(data))

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
    feedback_collection = db["Feedbacks"]  # Corrected collection assignment
    issues_collection = db["Issues"]

    print("Connected to MongoDB Atlas successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")

# ...

def main():
    print("Welcome to the University Chatbot!")

    while True:
        # Get user input
        user_query = input("You: ")

        # Check if the user wants to exit
        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
        
        collection_fn = None

        # Check if the query starts with 'feedback:'
        if user_query.lower().startswith('feedback:'):
            user_query = user_query.removeprefix('feedback:').strip()
            collection_fn = store_feedback
        elif user_query.lower().startswith('issue:'):
            user_query = user_query.removeprefix('issue:').strip()
            collection_fn = store_issue
        
        # Run the language model chain
        chat_context = retriever(user_query)
        bot_response = chain_general.run(query=user_query, context=chat_context)
        print("Bot:", bot_response)
        
        if collection_fn is not None:
            collection_fn(user_query, bot_response)
            notify_admin(collection_fn.__name__.capitalize(), user_query, bot_response)
        

if __name__ == "__main__":
    main()