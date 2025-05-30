import streamlit as st
import requests
import uuid

BACKEND_URL_API = st.secrets['BACKEND_URL_API']

def clear_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]

st.header("Chatbot")

if "backend_chat_api" not in st.session_state:
    st.session_state.backend_chat_api = "{}/chat".format(BACKEND_URL_API)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for message in st.session_state.chat_history:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role):
        st.markdown(content) 

query = st.chat_input(f"Nhập tin nhắn...")

if query:

    with st.chat_message("user"):
        st.markdown(query)

    user_response = {
        "role" : "user",
        "content": query
    }
    st.session_state.chat_history.append(user_response)

    with st.chat_message("assistant"):
        payload = [{
			"role": "user",
			"parts": [
				{
					"text": query
				}
			]
		}]

        response = requests.post(st.session_state.backend_chat_api, json = payload)

        if response.status_code == 200:
            api_response = response.json()
            assistant_msg = api_response["parts"][0]["text"]
            assistant_response = {
                "role" : "assistant",
                "content": assistant_msg
            }
            st.session_state.chat_history.append(assistant_response)
            st.markdown(assistant_msg)
        else:
            st.error(f"Error: {response.status_code}")


    