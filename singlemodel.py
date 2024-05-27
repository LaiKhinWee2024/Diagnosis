import openai
import streamlit as st
import os
import toml
from streamlit_chat import message

openai.api_key = st.secrets["api_secret"]

# creating a function which will generate the calls from the api
def generate_response(prompt, temperature):
    try:
        completions = openai.ChatCompletion.create(
            model="ft:gpt-3.5-turbo-0125:personal::9NwRJ5QF",  
            messages=[{'role': 'system', 'content': "You are a well-rounded doctor that answer questions with high accuracy." },
                      {'role': 'user', 'content': prompt}
                     ],
            temperature=temperature
        )
        # Extract the response message
        message_content = completions.choices[0].message['content']
        return message_content
    except Exception as e:
        return f"Error: {e}"


# Main Streamlit code
def main():

    # Display image
    st.sidebar.image("https://raw.githubusercontent.com/LimVictoria/GPT-EMR-Chatbot/main/bot.webp", use_column_width=True) #,caption="GPT–EMR")

    # Create a slider for temperature
    temperature = st.sidebar.slider('Creativity of generated responses', min_value=0.1, max_value=1.0, step=0.1, value=0.3)
    #st.sidebar.write("Adjust temperature with low temperature for accurate response, high temperature for creativity.")


    # Display title
    st.title("Chatbot A") #GPTEMR

    # Display prompt box
    def get_text():
        input_text = st.text_input("Medical Inquiries: ", key="input")
        return input_text

    # Define user input
    user_input = get_text()

    if user_input:
        # Generate response
        response = generate_response(user_input, temperature)

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

    
