import re
import openai
from time import time, sleep
import textwrap
import yaml
import streamlit as st
import os
from halo import Halo


###     file operations


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


###     API functions


def chatbot(conversation, model="gpt-3.5-turbo-0125", temperature=0, max_tokens=2000):
    max_retry = 7
    retry = 0
    while True:
        try:
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()

            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature,
                                                    max_tokens=max_tokens)
            text = response['choices'][0]['message']['content']

            spinner.stop()

            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            exit(5)


def chat_print(text):
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in
                       text.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print('\n\n\nCHATBOT:\n\n%s' % formatted_text)


########################################################################################################################

if __name__ == '__main__':
    openai.api_key = st.secrets["api_secret"]

    # Display image
    st.sidebar.image("https://raw.githubusercontent.com/LimVictoria/GPT-EMR-Chatbot/main/bot.webp",
                     use_column_width=True)  # ,caption="GPT–EMR")

    # Create a slider for temperature
    temperature = st.sidebar.slider('Creativity of generated responses', min_value=0.1, max_value=1.0, step=0.1,
                                    value=0.5)
    # st.sidebar.write("Adjust temperature with low temperature for accurate response, high temperature for creativity.")

    # Display title
    st.title("GPT–EMR Chatbot")

    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
    user_messages = list()
    all_messages = list()
    #st.write("Describe your symptoms to the GPT–EMR Chatbot. Type DONE when done.")

    ## INTAKE PORTION

    text = None
    input_index = 0

    # Loop until user types "DONE"
    while text != 'DONE':
        # get user input
        
        text = st.text_area("Describe your symptoms to the GPT–EMR Chatbot. Type DONE when done.",
                            key=f"input_{input_index}", value=None)
        input_index += 1

        if text != 'DONE':
            user_messages.append(text)
            all_messages.append('PATIENT: %s' % text)
            conversation.append({'role': 'user', 'content': text})
            response, tokens = chatbot(conversation)
            conversation.append({'role': 'assistant', 'content': response})
            all_messages.append('INTAKE: %s' % response)
            st.write('\n\nGPT–EMR Chatbot: %s' % response)
            print('\n\nINTAKE: %s' % response)

    ########################################################################################################################

    ## CHARTING NOTES

    st.write('\n\nGenerating Intake Notes')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_02_prepare_notes.md')})
    text_block = '\n\n'.join(all_messages)
    chat_log = '<<BEGIN PATIENT INTAKE CHAT>>\n\n%s\n\n<<END PATIENT INTAKE CHAT>>' % text_block
    conversation.append({'role': 'user', 'content': chat_log})
    notes, tokens = chatbot(conversation)
    st.write('\n\nNotes version of conversation:\n\n%s' % notes)
    print('\n\nNotes version of conversation:\n\n%s' % notes)

    ## GENERATING REPORT

    st.write('\n\nGenerating Hypothesis Report')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_03_diagnosis.md')})
    conversation.append({'role': 'user', 'content': notes})
    report, tokens = chatbot(conversation)
    st.write('\n\nHypothesis Report:\n\n%s' % report)
    print('\n\nHypothesis Report:\n\n%s' % report)

    ## CLINICAL EVALUATION

    st.write('\n\nPreparing for Clinical Evaluation')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_04_clinical.md')})
    conversation.append({'role': 'user', 'content': notes})
    clinical, tokens = chatbot(conversation)
    st.write('\n\nClinical Evaluation:\n\n%s' % clinical)
    print('\n\nClinical Evaluation:\n\n%s' % clinical)

    ## REFERRALS & TESTS

    st.write('\n\nGenerating Referrals and Tests')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_05_referrals.md')})
    conversation.append({'role': 'user', 'content': notes})
    referrals, tokens = chatbot(conversation)
    st.write('\n\nReferrals and Tests:\n\n%s' % referrals)
    print('\n\nReferrals and Tests:\n\n%s' % referrals)
