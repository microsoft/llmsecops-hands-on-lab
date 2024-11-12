import json
import os
from typing import List
from pydantic import BaseModel
import streamlit as st
import time
import promptflow as pf
from promptflow.entities import AzureOpenAIConnection
import dotenv
from pathlib import Path

# Define the path to the .env file
env_path = Path('/workspaces/hands-on-lab-quality-security-llmops/.env')

# Load environment variables from the .env file
dotenv.load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("AZURE_OPENAI_CHAT_KEY")
OPENAI_API_BASE = os.getenv("AZURE_OPENAI_CHAT_ENDPOINT")

PAGE_TITLE = "Promptflow + Streamlit"


#FLOW_OPTIONS = ["chat", "chat-with-pdf"]
FLOW_OPTIONS = ["chat"]
TITLE_FLOW_PATH = "flows/make_title"

# Initialize an empty list to save data for evaluations
eval_data = []

# Create a JSONL file at the start of the program
# with open('eval_data.jsonl', 'w') as f:
#     f.write('')


class Message(BaseModel):
    role: str
    content: str


class ChatThreadHistory(BaseModel):
    title: str
    is_default: bool = True
    messages: List[Message] = []

    def __post_init__(self):
        self.messages = [Message(**m) for m in self.messages]

    def to_promptflow_format(self):
        """Converts chat history to a format that can be used by PromptFlow"""
        promptflow_format = []
        for i in range(len(self.messages)//2):
            input = self.messages[i*2]
            output = self.messages[i*2+1]
            promptflow_format.append({"inputs": {"question": input.content},
                                      "outputs": {"answer": output.content}})

        return json.dumps(promptflow_format)


def save_chat_history(chat_history: List[ChatThreadHistory]):
    with open("chat_history.jsonl", "w") as f:
        f.truncate()
        for ch in chat_history:
            f.write(json.dumps(ch.model_dump()) + "\n")


def restore_chat_history():
    with open("chat_history.jsonl", "r") as f:
        st.session_state.chat_history = [ChatThreadHistory(**json.loads(ch))
                                         for ch in f.readlines()]


st.set_page_config(page_title=PAGE_TITLE)

# Set up PromptFlow
connection = AzureOpenAIConnection(name="azure_open_ai_connection",
                                   api_key=OPENAI_API_KEY,
                                   api_base=OPENAI_API_BASE)
pf_client = pf.PFClient()
pf_client.connections.create_or_update(connection)


# Init selectBox to choose Flow to run
# Create the select box
flow_selection = st.selectbox("Flow Selection", FLOW_OPTIONS)
#print(flow_selection)


#chat_flow = pf.load_flow(source=CHAT_FLOW_PATH)
chat_flow = pf.load_flow(source=f'flows/{flow_selection}')

chat_flow.context.streaming = True
title_flow = pf.load_flow(source=TITLE_FLOW_PATH)


# on first load, restore chat history from file
if "chat_history" not in st.session_state and \
        os.path.exists("chat_history.jsonl"):
    restore_chat_history()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history: List[ChatThreadHistory] = [
        ChatThreadHistory(title="New Chat")]

# Initialize session state if it doesn't exist
if 'feedback' not in st.session_state:
    st.session_state.feedback = ''
if 'like' not in st.session_state:
    st.session_state.like = False
if 'dislike' not in st.session_state:
    st.session_state.dislike = False
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False


#Init some state vals to be used to generate evaluation data
if 'eval_question' not in st.session_state:
    st.session_state.eval_question = ''
if 'eval_answer' not in st.session_state:
    st.session_state.eval_answer = ''
if 'eval_context' not in st.session_state:
    st.session_state.eval_context = ''


with st.sidebar:
    st.selectbox("Chat Selection",
                 key="chat_i",
                 options=reversed(range(len(st.session_state.chat_history))),
                 format_func=lambda i: st.session_state.chat_history[i].title)

    st.button("New chat",
              on_click=lambda: st.session_state.chat_history.append(
                  ChatThreadHistory(
                      title="New Chat")))

    def delete_chat():
        st.session_state.chat_history.pop(st.session_state.chat_i)
        if len(st.session_state.chat_history) == 0:
            st.session_state.chat_history.append(
                ChatThreadHistory(title="New Chat"))
        save_chat_history(st.session_state.chat_history)

    st.button("Delete chat", on_click=lambda: delete_chat())

st.title(st.session_state.chat_history[st.session_state.chat_i].title)

chat = st.empty()
#formbtn = st.button("Form")

# st.session_state.dislike = st.checkbox('👎 Dislike')
# st.session_state.feedback = st.text_input('Please enter your feedback here')


# Display chat messages from history on app rerun
for message in st.session_state.chat_history[st.session_state.chat_i].messages:
    with st.chat_message(message.role):
        st.markdown(message.content)

# Accept user input
if prompt := chat.chat_input("Type a message..."):
    # Add user message to chat history
    chat_history = st.session_state.chat_history
    chat_history[st.session_state.chat_i].messages.append(
        Message(role="user", content=prompt))
    st.session_state.chat_history = chat_history
    save_chat_history(chat_history)
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Convert session state message to format
        messages = []

        result = chat_flow(
            question=prompt,
            chat_history=str(
                st.session_state.chat_history[
                    st.session_state.chat_i].to_promptflow_format()))

        print(result.get("context", "NO CONTEXT AVAILABLE"))
        # Stream of response
        for r in result["answer"]:
            full_response += r
            time.sleep(0.08)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)


        # Set the flag to show feedback widgets
        st.session_state.show_feedback = True

        #save eval values to be used below
        st.session_state.eval_question = prompt
        st.session_state.eval_answer = full_response
        st.session_state.eval_context = result.get("context", "")

    # Add assistant response to chat history
    chat_history[st.session_state.chat_i].messages.append(
        Message(role="assistant", content=full_response))
    st.session_state.chat_history = chat_history
    save_chat_history(chat_history)

    

    # If the first message is a question, use it to generate a title
    if chat_history[st.session_state.chat_i].is_default:
        title = title_flow(user_question=chat_history[
            st.session_state.chat_i].messages[0].content)["title"]
        chat_history[st.session_state.chat_i].title = title
        chat_history[
            st.session_state.chat_i].is_default = False
        st.session_state.chat_history = chat_history
        save_chat_history(chat_history)
        st.rerun()

dislike = False
# Show feedback widgets only if the flag is set
if st.session_state.show_feedback:
    with st.form(key='feedback_form'):
        st.session_state.dislike = st.checkbox('👎 Dislike')
        feedback_input = st.text_input('Please enter the correct answer (groundtruth)','',autocomplete=None)
        st.session_state.feedback = feedback_input

        # Add 'Send' button
        submit_button = st.form_submit_button(label='Send')

        if submit_button:
            # Print values of 'Dislike' checkbox and feedback text
            print('Dislike:', st.session_state.dislike)
            dislike = st.session_state.dislike
            print('Feedback:', st.session_state.feedback)
            st.session_state.show_feedback = False
            st.rerun()


#save conversation as eval data format
# Define the new item
new_item = {'question': st.session_state.eval_question, 
            'answer': st.session_state.eval_answer, 
            'context': st.session_state.eval_context, 
            "groundtruth": st.session_state.feedback,
            "dislike": st.session_state.dislike,
            "flow": flow_selection}

# Check for existing item
# for item in eval_data:
#     if item['question'] == new_item['question'] and item['answer'] == new_item['answer'] and item['context'] == new_item['context']:
#         # Update feedback
#         item['groundtruth'] = new_item['groundtruth']
#         item['dislike'] = new_item['dislike']
#         break
# else:
#     # If no existing item is found, append the new item
#     eval_data.append(new_item)

# Load existing data
with open('eval_data.jsonl', 'r') as f:
    eval_data = [json.loads(line) for line in f]

# Check for existing item
for item in eval_data:
    if item['question'] == new_item['question'] and item['answer'] == new_item['answer'] and item['context'] == new_item['context']:
        # Update feedback
        item['groundtruth'] = new_item['groundtruth']
        item['dislike'] = new_item['dislike']
        break
else:
    # If no existing item is found, append the new item
    if new_item['question'] != "" and new_item['answer']:
        eval_data.append(new_item)

# Save the changes by writing the updated list to the JSONL file
with open('eval_data.jsonl', 'w') as f:
    for item in eval_data:
        f.write(json.dumps(item) + '\n')


#st.experimental_rerun() 

            
