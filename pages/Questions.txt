import streamlit as st
import time
import requests

BACKEND_URL_API = st.secrets['BACKEND_URL_API']
SESSION_STATE_KEY_QA = "questions_answers_data"

def clear_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]

if "backend_chat_api" not in st.session_state:
    st.session_state.add_question_api = f"{BACKEND_URL_API}/api/add/qa"

##################################################
### CALL API FUNCTIONS
##################################################

def load_all_questions_answers():
    try:
        response = requests.get(f"{BACKEND_URL_API}/api/qa")
        if response.status_code == 200:
            data = response.json()
            return {item['id']: item for item in data['data'] if item}
        else:
            st.write(f"Lỗi: {response.status_code}. Không thể tải dữ liệu.")
    except requests.exceptions.RequestException as e:
        st.write(f"Lỗi khi gửi yêu cầu: {e}")

def load_qa(qa_id):
    try:
        response = requests.get(f"{BACKEND_URL_API}/api/qa/{qa_id}")
        if response.status_code == 200:
            data = response.json()
            return data['data'] if data and 'data' in data else None
        else:
            st.write(f"Lỗi: {response.status_code}. Không thể tải câu hỏi.")
    except requests.exceptions.RequestException as e:
        st.write(f"Lỗi khi gửi yêu cầu: {e}")

def add_question_answer(payload):
    try: 
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = requests.post(f"{BACKEND_URL_API}/api/add/qa", json=payload, headers=headers)
        if response.status_code == 201:
            try:
                res = response.json()
                st.toast(f"Câu hỏi đã được thêm thành công!", icon="✅")
                time.sleep(1)
            except requests.exceptions.JSONDecodeError as e:
                st.write(f"Lỗi phân tích JSON: {e}")
                st.write(f"Nội dung phản hồi: {response.text}")
        elif response.status_code == 405:
            st.write(f"Lỗi 405: Phương thức không được phép cho URL {response.url}")
            st.write("Kiểm tra URL và đảm bảo sử dụng POST cho /api/qa")
        else:
            st.write(f"Lỗi: {response.status_code}. Không thể thêm câu hỏi.")
            st.write(f"Nội dung phản hồi: {response.text}")
    except requests.exceptions.RequestException as e:
        st.write(f"Lỗi khi gửi yêu cầu: {e}")

def delete_question_answer(qa_id):
    try:
        response = requests.delete(f"{BACKEND_URL_API}/api/delete/qa/{qa_id}")
        if response.status_code == 200:
            st.toast(f"Câu hỏi đã được xóa thành công!", icon="✅")
            time.sleep(1)  # Delay to ensure the UI updates
        else:
            st.write(f"Lỗi: {response.status_code}. Không thể xóa câu hỏi.")
    except requests.exceptions.RequestException as e:
        st.write(f"Lỗi khi gửi yêu cầu: {e}") 

def update_question_answer(qa_id, payload):
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = requests.put(f"{BACKEND_URL_API}/api/update/qa/{qa_id}", json=payload, headers=headers)
        if response.status_code == 200:
            st.toast(f"Câu hỏi đã được cập nhật thành công!", icon="✅")
            time.sleep(1) 
        else:
            st.write(f"Lỗi: {response.status_code}. Không thể cập nhật câu hỏi.")
    except requests.exceptions.RequestException as e:
        st.write(f"Lỗi khi gửi yêu cầu: {e}")

##################################################
### STREAMLIT CALLBACKS
##################################################

# These functions handle the logic when a user interacts with a widget (button, form).
# The usual workflow for those callbacks is:
# 1. Get form input data through st.session_state form widget keys,
# 2. Perform database operations,
# 3. Refresh session state by reading from database.


def create_qa_callback():
    # 1. Get form input data
    require_fields = {'new_question_form_topic': 'Chủ đề', 'new_question_form_question': 'Câu hỏi',  'new_question_form_answer': 'Câu trả lời'}

    for key, value  in require_fields.items():
        if not st.session_state.get(f"{key}"):
            st.toast(f"{value} không được để trống", icon="⚠️")
            return

    new_qa_data = {
        "topic": st.session_state[f"new_question_form_topic"],
        "question": st.session_state["new_question_form_question"],
        "answer": st.session_state["new_question_form_answer"],
        "is_chunk": False,
    }

    # 2. Call backend API to add new question answer
    add_question_answer(new_qa_data)

    # 3. Refresh session state from database
    st.session_state[SESSION_STATE_KEY_QA] = load_all_questions_answers()


def open_update_callback(qa_id: int):
    st.session_state[f"currently_editing__{qa_id}"] = True


def cancel_update_callback(qa_id: int):
    st.session_state[f"currently_editing__{qa_id}"] = False


def update_qa_callback(qa_id: int):
    # 1. Get form input data
    updated_values = {
        "topic": st.session_state[f"edit_qa_form_{qa_id}__topic"],
        "question": st.session_state[f"edit_qa_form_{qa_id}__question"],
        "answer": st.session_state[f"edit_qa_form_{qa_id}__answer"],
    }

    require_fields = ['topic', 'question', 'answer']
    for field in require_fields:
        if not updated_values[field]:
            st.toast(f"{field} không được để trống", icon="⚠️")
            st.session_state[f"currently_editing__{qa_id}"] = True
            return
    
    # 2. Call backend API to update qa
    update_question_answer(qa_id, updated_values)
    # 3. Refresh session state from database
    st.session_state[SESSION_STATE_KEY_QA][qa_id] = load_qa(qa_id)
    st.session_state[f"currently_editing__{qa_id}"] = False


def delete_qa_callback(qa_id: int):
    # 1. Get form input data

    # 2. call backend API to delete qa
    delete_question_answer(qa_id)

    # 3. Refresh session state from database
    st.session_state[SESSION_STATE_KEY_QA] = load_all_questions_answers()
    st.session_state[f"currently_editing__{qa_id}"] = False


def mark_learn_callback(qa_id: int):
    # 1. Get form input data
    current_is_chunk_status = st.session_state[SESSION_STATE_KEY_QA][qa_id]['is_chunk']

    # 2. Call backend API to mark as learned
    payload = {
        "is_chunk": not current_is_chunk_status,
    }
    update_question_answer(qa_id, payload)

    # 3. Refresh session state from database
    st.session_state[SESSION_STATE_KEY_QA][qa_id] = load_qa(qa_id)


##################################################
### UI WIDGETS
##################################################

# These functions render parts of the UI.
# They take data like a QA object and display it using Streamlit widgets.


# Function to display a single qa item as a card
def qa_card(qa_item):
    qa_id = qa_item['id']

    with st.container(border=True):
        display_question = f"**Câu hỏi**: {qa_item['question']}"
        display_answer = f"**Câu trả lời**: {qa_item['answer']}"
        display_topic = f"**Chủ đề**: {qa_item['topic']}"

        st.subheader(display_question)
        st.markdown(display_answer)
        st.markdown(display_topic)

        learn_col, edit_col, delete_col = st.columns(3)
        learn_col.button(
            "Cho AI Học" if not qa_item['is_chunk'] else "Đã Học",
            icon=":material/check_circle:",
            key=f"display_qa_{qa_id}__learn",
            on_click=mark_learn_callback,
            args=(qa_id,),
            type="secondary" if qa_item['is_chunk'] else "primary",
            disabled=qa_item['is_chunk'],
            use_container_width=True,
        )
        edit_col.button(
            "Chỉnh sửa",
            icon=":material/edit:",
            key=f"display_qa_{qa_id}__edit",
            on_click=open_update_callback,
            args=(qa_id,),
            disabled=qa_item['is_chunk'],
            use_container_width=True,
        )
        if delete_col.button(
            "Xóa",
            icon=":material/delete:",
            key=f"display_qa_{qa_id}__delete",
            use_container_width=True,
        ):
            delete_qa_callback(qa_id)
            st.rerun(scope="app")


# Function to display the inline form for editing an existing qa item
def qa_edit_widget(qa_item):
    qa_id = qa_item['id']

    with st.form(f"edit_qa_form_{qa_id}"):
        st.text_input(
            "Chủ đề", value=qa_item['topic'], key=f"edit_qa_form_{qa_id}__topic"
        )
        st.text_input(
            "Câu hỏi", value=qa_item['question'], key=f"edit_qa_form_{qa_id}__question"
        )
        st.text_area(
            "Câu trả lời",
            value=qa_item['answer'],
            key=f"edit_qa_form_{qa_id}__answer",
        )

        submit_col, cancel_col = st.columns(2)
        submit_col.form_submit_button(
            "Cập nhập",
            icon=":material/save:",
            type="primary",
            on_click=update_qa_callback,
            args=(qa_id,),
            use_container_width=True,
        )

        cancel_col.form_submit_button(
            "Hủy",
            on_click=cancel_update_callback,
            args=(qa_id,),
            use_container_width=True,
        )


# If a script rerun by widget interaction is triggered from a @st.fragment function
# Instead of a script rerun, Streamlit only reruns the fragment function

# Any widget interaction and callback that occurs within this function
# only affects the database state and session state of the input qa item
# so the fragment reruns to reload and display the state of the qa item


@st.fragment
def qa_component(qa_id: int):
    # Load qa item fields from session state
    # Syncing from database to session state was done in callback
    qa_item = st.session_state[SESSION_STATE_KEY_QA][qa_id]
    currently_editing = st.session_state.get(f"currently_editing__{qa_id}", False)

    if not currently_editing:
        qa_card(qa_item)

    else:
        qa_edit_widget(qa_item)

##################################################
### USER INTERFACE
#################################################

#    This happens on the first run or if the state was cleared.
if SESSION_STATE_KEY_QA not in st.session_state:
    with st.spinner("Loading QA..."):
        st.session_state[SESSION_STATE_KEY_QA] = load_all_questions_answers()

# --- Display create Question form ---
with st.form(f"new_question_form", enter_to_submit=False, clear_on_submit=True):
        st.subheader(":material/add_circle: Thêm câu hỏi mới")
        topic = st.text_input("Chủ đề", placeholder="Câu hỏi thuộc về chủ đề gì?", key=f"new_question_form_topic")
        question = st.text_input("Câu hỏi", placeholder="Nhập câu hỏi", key=f"new_question_form_question")
        answer = st.text_area("Câu trả lời", placeholder="Nhập câu trả lời", key=f"new_question_form_answer")

        st.form_submit_button(
            "Thêm câu hỏi", 
            on_click=create_qa_callback,
            type="primary"
        )

# --- Display all questions and answers ---
current_questions_answers = st.session_state.get(SESSION_STATE_KEY_QA, {})
for qa_id in current_questions_answers.keys():
    # Initialize editing state for qa item
    if f"currently_editing__{qa_id}" not in st.session_state:
        st.session_state[f"currently_editing__{qa_id}"] = False
    qa_component(qa_id)

