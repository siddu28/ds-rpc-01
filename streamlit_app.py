import streamlit as st
import requests


# Session state to store login info
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False ## session state is useful in terms of remembering the username ,password and logged_in state ,with out reloading again from starting
    st.session_state.username = ""
    st.session_state.role = ""

st.title("🔐 Role-Based Chatbot")

if not st.session_state.logged_in:
    st.subheader("Login to continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):          ## sending the login get request to fastapi server to check the credentials 
        response = requests.get(
            "http://127.0.0.1:8000/login",   ## this is fastapi local server which sends login get request
            auth=(username, password)
        )

        if response.status_code == 200:  ## server returns 200 if the credentials are correct
            result = response.json()
            st.success("Login successful!")
            st.session_state.logged_in = True ## then making the logged_in state as true so that it won't show the login page when you rerun it.
            st.session_state.username = username
            st.session_state.password = password
            st.rerun()  ## you have to rerun inorder to complete login page so that it will set loggeg_in to true then it will rerun and go to else part in which user can ask questions to chatbot


        else:
            st.error("Invalid username or password.")

else:
    st.success(f"Welcome, {st.session_state.username}")
    query = st.text_input("Ask your question")  ## this is input holder in which user can enter the question

    if st.button("Ask"):
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            response = requests.post(  ## this is post request to the fastapi backend server by passing the user query along with the login credentials
                "http://127.0.0.1:8000/chat",
                params={"message": query},
                auth=(st.session_state.username, st.session_state.password)
            )

            if response.status_code == 200: ## if the post request done successfully then it will return 200 and displays the answer according to the user question
                data = response.json()
                st.write("Answer:")
                st.markdown(data.get("answer", "No answer found"))
            else:
                st.error("Something went wrong!")

    if st.button("Logout"):  ## you can logout if you want to login as another person with different role
        st.session_state.logged_in = False
        st.rerun()

