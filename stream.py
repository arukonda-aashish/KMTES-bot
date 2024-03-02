import streamlit as st
from chatbot import get_retriever, get_chain_general,store_feedback,store_issue

# Get retriever and chain objects
retriever = get_retriever()
chain_general = get_chain_general()

# Streamlit UI
st.title("Sanchaar")

# User input
user_input = st.text_input("You:")

# Check if the user wants to exit
if user_input.lower() in ['exit', 'quit', 'bye']:
    st.write("Goodbye! have a nice day")
else:
    # Check if the query starts with 'feedback:'
    if user_input.lower().startswith('feedback'):
        feedback_response = st.text_area("Please provide feedback:")
        # Store feedback
        store_feedback(user_input, feedback_response, "Additional data for feedback")
        st.write("Feedback stored. Thank you!")
    elif user_input.lower().startswith('issue'):
        # Handle issue
        st.write("Please describe the issue:")
        issue = st.text_area("Issue:")
        if st.button("Submit Issue"):
            # Store issue
            store_issue(issue)
            st.write("Issue recorded and will be sent to the concerned authorities. Thank you.")
    else:
        # Run the language model chain
        chat_context = retriever(user_input)
        bot_response = chain_general.run(query=user_input, context=chat_context)
        st.text_area("Bot:", value=bot_response, height=200)
