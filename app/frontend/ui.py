import streamlit as st
import requests

from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

st.set_page_config(page_title="Multi AI Agent", layout="centered")
st.title("Multi AI Agent using Groq and Tavily")

system_prompt = st.text_area("Define your AI Agent ", height=70)
select_model = st.selectbox("Choose your AI Model", settings.ALLOWED_MODELS_NAME)

allow_web_search = st.checkbox("Allow web search")

user_query = st.text_area("Enter your query: ", height=150)

API_URL = "http://127.0.0.1:9999/chat"

if st.button("Ask Agent") and user_query.strip():

    payload = {
        "model_name": select_model,
        "messages": [user_query],
        "allow_search": allow_web_search,
        "system_prompt": system_prompt,

    }

    try:
        logger.info("sending request to backend")

        response = requests.post(API_URL, json=payload)

        if response.status_code==200:
            agent_response = response.json().get("response","")
            logger.info("Successfully received response from backend")

            st.subheader("Agent Response")
            st.markdown(agent_response.replace("\n","<br>"), unsafe_allow_html=True)

        else:
            logger.error("Backend Error")
            st.error("Backend Error")

    except Exception as e:
        logger.error("Error occureed while sending request to backend")
        st.error(str(CustomException("Failed to communicate to backend")))            