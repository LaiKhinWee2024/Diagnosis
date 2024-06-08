import streamlit as st
from streamlit_chat import message
import openai
import streamlit as st
import os
import toml
from custom_chatbot import custom_chatbot  # Import the custom chatbot function from the other file

# Set your OpenAI API key here
openai.api_key = st.secrets["api_secret"]

def generate_response(prompt, temperature, model):
    try:
        completions = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'system', 'content': "You are a honest doctor informing patient about their chances of living. Elaborate on the potential cause of death during the hospital stay." },
                      {'role': 'user', 'content': prompt}
                     ],
            temperature=temperature
        )
        # Extract the response message
        message_content = completions.choices[0].message['content']
        return message_content
    except Exception as e:
        return f"Error: {e}"

# Create a role for chatbot
#role_bot = st.sidebar.text_input("Role of Chatbot: ", key = "role")

# Main Streamlit code
def main():
    # Display image
    st.sidebar.image("https://raw.githubusercontent.com/LimVictoria/GPT-EMR-Chatbot/main/bot.webp",
                     use_column_width=True)

    # Create a slider for temperature with a unique key
    temperature = st.sidebar.slider('Creativity of generated responses', min_value=0.1, max_value=1.0, step=0.1,
                                    value=0.3, key="temperature_slider")

    # Create radio button for model selection
    model_option = st.sidebar.radio("Select Model", ("Consultation", "General Inquiries", "MIMIC–III", "Diagnostic Bot"))  # Changed "Custom" to "Diagnostic Bot"

    # Map model option to actual model names
    model_map = {    "Consultation": "ft:gpt-3.5-turbo-0125:personal::9NwRJ5QF",
                     "General Inquiries": "ft:gpt-3.5-turbo-0125:personal::9LBU24JF",
                     "MIMIC–III" : "ft:gpt-3.5-turbo-0125:personal::92Yef7J0",
                     "Diagnostic Bot": "custom_model"}  

    selected_model = model_map[model_option]


    # Call the custom chatbot function if the "Diagnostic Bot" radio button is selected
    if model_option == "Diagnostic Bot":
        custom_chatbot()
    else:
        # Display title
        st.title("GPT–EMR Chatbot")

        # Display prompt box
        def get_text():
            input_text = st.text_input("Medical Inquiries: ", key="input")
            return input_text

        # Define user input
        user_input = get_text()

        if user_input:
            # Generate response
            response = generate_response(user_input, temperature, selected_model)

            # Insert the user input at the beginning of the list
            st.session_state['past'].insert(0, user_input)  # This is the user input (prompt)

            # Insert the generated response just after the user input
            st.session_state['past'].insert(1, response)  # This is the generated response

        # create empty container to store the chat
        if 'past' not in st.session_state:
            st.session_state['past'] = []

        if st.session_state['past']:
            for i in range(len(st.session_state['past'])):
                is_user = i % 2 == 0  # True if i is even, False if i is odd
                key = str(i) + ('_user' if is_user else '_generated')
                message(st.session_state['past'][i], is_user=is_user, key=key)


if __name__ == '__main__':
    main()
