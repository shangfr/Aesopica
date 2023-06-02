# -*- coding: utf-8 -*-
"""
Created on Wed May 31 15:38:04 2023

@author: shangfr
"""
import os
import openai
import streamlit as st
from streamlit_chat import message
from vecdb import load_vectordb

# Setting page title and header
st.set_page_config(
    page_title="Aesopica",
    page_icon="📚",
    layout="wide",
    #initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/shangfr/shangfr.github.io',
        'Report a bug': "https://github.com/shangfr/shangfr.github.io",
        'About': "# FollowAI. Simple example of usage of streamlit and FastAPI for ML model serving."
    }
)

st.markdown("<h1 style='text-align: center;'>📚 Chat With Aesop</h1>", unsafe_allow_html=True)

os.environ["OPENAI_API_KEY"] = st.secrets['api_key']


# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.write(
    '<span style="font-size: 78px; line-height: 1">🐱</span>',
    unsafe_allow_html=True,
)
model_name = st.sidebar.radio("Choose a model:", ("Chat","Reading"))
counter_placeholder = st.sidebar.empty()
counter_placeholder.caption(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("清空 - Clear", key="clear")


# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


@st.cache_resource
def get_db_session(directory='fables_db'):
    vectordb = load_vectordb(directory)
    return vectordb

@st.cache_data
def get_fable(prompt):
    vectordb = get_db_session()
    results = vectordb.similarity_search_with_score(prompt,k=1)
    if results[0][1]<0.35:
        response = results[0][0].page_content.split('\n')
        response = '\n\n'.join(response[4:7])   
    else:
        response= ''
    return response

    
# generate a response
def generate_response(prompt,model):
    response = get_fable(prompt)
    if response:
        prompt = prompt+'\n请参考下面内容：\n'+response
    st.session_state['messages'].append({"role": "user", "content": prompt})

    # Map model names to OpenAI model IDs
    if model_name == "Chat":
        model = "gpt-3.5-turbo"
        with st.spinner('Wait for ChatGPT...'):
            completion = openai.ChatCompletion.create(
                model=model,
                messages=st.session_state['messages']
            )
        response = completion.choices[0].message.content
        st.session_state['messages'].append({"role": "assistant", "content": response})
    
        # print(st.session_state['messages'])
        total_tokens = completion.usage.total_tokens
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        return response, total_tokens, prompt_tokens, completion_tokens

    else:
        response = response.replace('\n','\n- ')
        st.session_state['messages'].append({"role": "assistant", "content": response})
        return response, 0, 0, 0
# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input,model_name)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = 0

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
            st.caption(
                f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            counter_placeholder.caption(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")