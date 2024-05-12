import openai
import streamlit as st
import textwrap
from halo import Halo

def custom_chatbot():
    # Set OpenAI API key
    openai.api_key = st.secrets["api_secret"]

    def open_file(filepath):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
            return infile.read()

    def chatbot(prompt, model="ft:gpt-3.5-turbo-0125:personal::9NwRJ5QF", temperature=0, max_tokens=2000):
        max_retry = 7
        retry = 0
        while True:
            try:
                spinner = Halo(text='Thinking...', spinner='dots')
                spinner.start()

                response = openai.ChatCompletion.create(model=model, messages=prompt, temperature=temperature,
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

    # Display title
    st.title("GPT–EMR Chatbot")

    prompt = list()
    prompt.append({'role': 'system', 'content': open_file('system_01_intake.md')})
    user_messages = list()
    all_messages = list()

    # INTAKE PORTION
    text = None
    input_index = 0

    # Loop until user types "DONE"
    while text != 'DONE':
        # Get user input
        text = st.text_input("Describe your symptoms to the GPT–EMR Chatbot. Type DONE when done.",
                            key=f"input_{input_index}", value=None)
        input_index += 1

        if text != 'DONE':
            user_messages.append(text)
            all_messages.append('PATIENT: %s' % text)
            prompt.append({'role': 'user', 'content': text})
            response, tokens = chatbot(prompt)
            prompt.append({'role': 'assistant', 'content': response})
            all_messages.append('INTAKE: %s' % response)
            st.write('\n\nGPT–EMR Chatbot: %s' % response)

    # CHARTING NOTES
    st.write('\n\nGenerating Intake Notes')
    prompt = list()
    prompt.append({'role': 'system', 'content': open_file('system_02_prepare_notes.md')})
    text_block = '\n\n'.join(all_messages)
    chat_log = '<<BEGIN PATIENT INTAKE CHAT>>\n\n%s\n\n<<END PATIENT INTAKE CHAT>>' % text_block
    prompt.append({'role': 'user', 'content': chat_log})
    notes, tokens = chatbot(prompt)
    st.write('\n\nNotes version of conversation:\n\n%s' % notes)

    # GENERATING REPORT
    st.write('\n\nGenerating Hypothesis Report')
    prompt = list()
    prompt.append({'role': 'system', 'content': open_file('system_03_diagnosis.md')})
    prompt.append({'role': 'user', 'content': notes})
    report, tokens = chatbot(prompt)
    st.write('\n\nHypothesis Report:\n\n%s' % report)

    # CLINICAL EVALUATION
    st.write('\n\nPreparing for Clinical Evaluation')
    prompt = list()
    prompt.append({'role': 'system', 'content': open_file('system_04_clinical.md')})
    prompt.append({'role': 'user', 'content': notes})
    clinical, tokens = chatbot(prompt)
    st.write('\n\nClinical Evaluation:\n\n%s' % clinical)

    # REFERRALS & TESTS
    st.write('\n\nGenerating Referrals and Tests')
    prompt = list()
    prompt.append({'role': 'system', 'content': open_file('system_05_referrals.md')})
    prompt.append({'role': 'user', 'content': notes})
    referrals, tokens = chatbot(prompt)
    st.write('\n\nReferrals and Tests:\n\n%s' % referrals)

if __name__ == '__main__':
    custom_chatbot()
