from flask import Flask, render_template, request
from chatbot import get_retriever, get_chain_general
from flask_cors import CORS

app = Flask(__name__, static_folder='templates')
CORS(app)
retriever = get_retriever()
chain_general = get_chain_general()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_query = request.form['user_query']
    chat_context = retriever(user_query)
    bot_response = chain_general.run(query=user_query, context=chat_context)
    return bot_response

if __name__ == '__main__':
    app.run(debug=True)
