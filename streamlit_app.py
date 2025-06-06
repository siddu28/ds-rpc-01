import streamlit as st
import requests


# Session state to store login info
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

st.title("🔐 Role-Based Chatbot")

if not st.session_state.logged_in:
    st.subheader("Login to continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.get(
            "http://127.0.0.1:8000/login",
            auth=(username, password)
        )

        if response.status_code == 200:
            result = response.json()
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.password = password
            st.session_state.role = result.get("role")
            st.rerun()


        else:
            st.error("Invalid username or password.")

else:
    st.success(f"Welcome, {st.session_state.username}")
    query = st.text_input("Ask your question")

    if st.button("Ask"):
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                params={"message": query},
                auth=(st.session_state.username, st.session_state.password)
            )

            if response.status_code == 200:
                data = response.json()
                st.write("Answer:")
                st.markdown(data.get("answer", "No answer found"))
            else:
                st.error("Something went wrong!")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

