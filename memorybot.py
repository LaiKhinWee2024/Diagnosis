import streamlit as st
from streamlit_chat import message
import os
import toml
#import openai
from custom_chatbot import custom_chatbot  # Import the custom chatbot function from the other file
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_community.chat_models import ChatOpenAI

# initialise session states

if "generated" not in st.session_state:
    st.session_state["generated"] = []          # output
if "past" not in st.session_state:
    st.session_state["past"] = []               # past
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = [] 

# Set your OpenAI API key here
api = st.secrets["api_secret"]

def get_text():
        input_text = st.text_input("Medical Inquiries: ",
                                  st.session_state["input"],
                                  key="input")
        return input_text


# Main Streamlit code
def main():
    # Display image
    st.sidebar.image("https://raw.githubusercontent.com/LimVictoria/GPT-EMR-Chatbot/main/bot.webp",
                     use_column_width=True)

    # Create a slider for temperature with a unique key
    temperature = st.sidebar.slider('Creativity of generated responses', min_value=0.1, max_value=1.0, step=0.1,
                                    value=0.5, key="temperature_slider")

    # Create radio button for model selection
    MODEL = st.sidebar.radio("Select Model", ("Base model", "PubMed", "MIMIC III", "Diagnostic Bot"))  # Changed "Custom" to "Diagnostic Bot"
    

    # Map model option to actual model names
    model_map = {"Base model": "gpt-3.5-turbo-1106",
                 "PubMed": "ft:gpt-3.5-turbo-0613:personal::8gPrCzxV",
                 "MIMIC III": "ft:gpt-3.5-turbo-0613:personal::8sQDXUeK",
                 "Diagnostic Bot": "custom_model"}  

    selected_model = model_map[MODEL]

    # Call the custom chatbot function if the "Diagnostic Bot" radio button is selected
    if MODEL == "Diagnostic Bot":
        custom_chatbot()
    else:
        # Display title
        st.title("GPT–EMR Memorybot")

        if api:
            llm = ChatOpenAI(
                openai_api_key = api,
                temperature = temperature,
                model_name = selected_model
            )
            
            if "entity_memory" not in st.session_state:
                st.session_state.entity_memory = ConversationEntityMemory(llm = llm, k = 10)
            
            # Create the conversation Chain
            Conversation = ConversationChain(
                llm = llm,
                prompt = ENTITY_MEMORY_CONVERSATION_TEMPLATE, 
                memory = st.session_state.entity_memory
                )

        try:
            user_input = get_text()
            
            if user_input and Conversation:  # Check if Conversation is not None before using it
                output = Conversation.run(input=user_input)
                st.session_state.past.append(user_input)
                st.session_state.generated.append(output)

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")

        # Display the conversation
        if Conversation:  # Check if Conversation is not None before using it
            for i in range(len(st.session_state['generated'])-1,-1,-1):
                st.info(st.session_state["past"][i], icon="🤓")
                st.success(st.session_state["generated"][i], icon="🤖")
        else:
            st.warning("Conversation could not be initiated because API is not available.")


if __name__ == '__main__':
    main()

