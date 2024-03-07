import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_community.llms import OpenAI

# initialise session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []  # output
if "past" not in st.session_state:
    st.session_state["past"] = []  # past
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

# Set your OpenAI API key here
api = st.secrets.get("api_secret")

def get_text():
    input_text = st.text_input("Medical Inquiries: ", st.session_state["input"], key="input")
    return input_text

# Main Streamlit code
def main():
    try:
        # Display title
        st.title("GPT–EMR Chatbot")

        if api:
            llm = OpenAI(
                openai_api_key=api,
                temperature=0.5,  # Adjust as needed
                model_name="gpt-3.5-turbo-1106",  # Adjust as needed
            )

            if "entity_memory" not in st.session_state:
                st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=10)

            # Create the conversation Chain
            Conversation = ConversationChain(
                llm=llm,
                prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                memory=st.session_state.entity_memory
            )

            user_input = get_text()

            if user_input and Conversation:
                output = Conversation.run(input=user_input)
                st.session_state.past.append(user_input)
                st.session_state.generated.append(output)

        else:
            st.warning("OpenAI API key is missing. Please set up the 'api_secret' in Streamlit secrets.")

        # Display the conversation
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            st.info(st.session_state["past"][i], icon="🤓")
            st.success(st.session_state["generated"][i], icon="🤖")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
