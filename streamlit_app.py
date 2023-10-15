from itertools import zip_longest
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import os
import dotenv
from dotenv import find_dotenv, load_dotenv
import speech_recognition as sr
from IPython.display import display, HTML
import time
#r.adjust_for_ambient_noise(source)


# Load environment variables
_ = load_dotenv(find_dotenv())

# Retrieve the API key from environment variables
api_key = os.environ['openai_api_key']

# Set up Streamlit page configuration
st.set_page_config(page_title="Hope to Skill ChatBot")
st.title("AI Mentor")

# Initialize session state variables
if 'entered_prompt' not in st.session_state:
    st.session_state['entered_prompt'] = ""  # Store the latest user input

if 'generated' not in st.session_state:
    st.session_state['generated'] = []  # Initialize 'generated' with an empty list

if 'past' not in st.session_state:
    st.session_state['past'] = []  # Store past user inputs

if 'voice_input' not in st.session_state:
    st.session_state['voice_input'] = ""  # Initialize voice input


# Initialize the ChatOpenAI model
chat = ChatOpenAI(
    temperature=0.5,
    model_name="gpt-3.5-turbo",
    api_key=api_key,
    max_tokens=50
)

# Define function to submit user input
def submit():
    # Set entered_prompt to the current value of prompt_input
    st.session_state.entered_prompt = st.session_state.prompt_input
    # Clear prompt_input
    st.session_state.prompt_input = ""

# Define function to process voice input
def process_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = r.listen(source)
    try:
        voice_input = r.recognize_google(audio)
        st.session_state.voice_input = voice_input
    except sr.UnknownValueError:
        st.write("Sorry, I couldn't understand the audio.")
    except sr.RequestError:
        st.write("Sorry, I couldn't request results.")
        
        
# Build a list of messages including system, human, and AI messages
def build_message_list():
    zipped_messages = [SystemMessage(
        content="""your name is AI Mentor. You are an AI Technical Expert for Artificial Intelligence, here to guide and assist students with their AI-related questions and concerns. Please provide accurate and helpful information, and always maintain a polite and professional tone.

1. Greet the user politely, ask the user's name, and ask how you can assist them with AI-related queries.
2. Provide informative and relevant responses to questions about artificial intelligence, machine learning, deep learning, natural language processing, computer vision, and related topics.
3. Avoid discussing sensitive, offensive, or harmful content. Refrain from engaging in any form of discrimination, harassment, or inappropriate behavior.
4. If the user asks about a topic unrelated to AI, politely steer the conversation back to AI or inform them that the topic is outside the scope of this conversation.
5. Be patient and considerate when responding to user queries, and provide clear explanations.
6. If the user expresses gratitude or indicates the end of the conversation, respond with a polite farewell.
7. Do not generate long paragraphs in response. The maximum word count should be 100.

Remember, your primary goal is to assist and educate students in the field of Artificial Intelligence. Always prioritize their learning experience and well-being."""
    )]

    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(content=human_msg))
        if ai_msg is not None:
            zipped_messages.append(AIMessage(content=ai_msg))

    return zipped_messages

# Generate AI response using the ChatOpenAI model
def generate_response():
    zipped_messages = build_message_list()
    ai_response = chat(zipped_messages)
    response = ai_response.content
    return response

# Create Streamlit elements for user interaction
st.text_input('YOU: ', key='prompt_input', on_change=submit)

if st.button("For speaking"):
    process_voice_input()

if st.session_state.entered_prompt != "":
    user_query = st.session_state.entered_prompt
else:
    user_query = st.session_state.voice_input

if user_query:
    st.session_state.past.append(user_query)
    output = generate_response()
    st.session_state.generated.append(output)

if st.session_state.generated:
    for i in range(len(st.session_state.generated) - 1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
