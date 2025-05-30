import streamlit as st
import pandas as pd
import requests

BACKEND_URL_API = st.secrets['BACKEND_URL_API']

if "backend_file_api" not in st.session_state:
    st.session_state.backend_file_api = "{}/file".format(BACKEND_URL_API)

if "backend_knowledge_api" not in st.session_state:
    st.session_state.backend_knowledge_api = "{}/knowledge".format(BACKEND_URL_API)

st.header("Knowledge")
uploaded_file = st.file_uploader(
    "Choose a pdf file", accept_multiple_files=False
)

save_button = st.button("Lưu")

if save_button:
    if not uploaded_file:
        st.warning('Bạn chưa tải file lên', icon="⚠️")
    else:
        payload = {
            "file" : uploaded_file
        }
        
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

        res = requests.post(st.session_state.backend_file_api, files=files)

        api_res = res.json()

        if res.status_code == 201:
            file_id = api_res['id']
            st.text(file_id)
            st.success('Tải file lên thành công!', icon="✅")

            if file_id:
                insert_button = st.button("Thêm kiến thức")
                if insert_button:
                    res = requests.get(f"{st.session_state.backend_knowledge_api}/{files_id[0]}")
                    st.text(res)
                    if res.status_code == 200:
                        st.success('Thêm kiến thức thành công!', icon="✅")
                    else: 
                        st.error(f"Error: {res.status_code}.")
        else:
            st.error(f"Error: {res.status_code}.")





response = requests.get(st.session_state.backend_file_api)
files = response.json()

st.subheader("Các tài liệu đã tải lên: ")
for file in files:
    st.text(file["name"])
       
