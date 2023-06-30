# -*- coding: utf-8 -*-
"""
Created on Wed May 31 15:38:04 2023

@author: shangfr
"""
import os
import openai
import streamlit as st

openai.api_key = st.secrets['api_key']
os.environ["OPENAI_API_KEY"] = st.secrets['api_key']

# Setting page title and header
st.set_page_config(
    page_title="Aesopica",
    page_icon="📚",
    layout="wide",
    # initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/shangfr/shangfr.github.io',
        'Report a bug': "https://github.com/shangfr/shangfr.github.io",
        'About': "# FollowAI. 对话伊索讲寓言."
    }
)

st.markdown("<h1 style='text-align: center;'>📚 Chat With Aesop</h1>",
            unsafe_allow_html=True)

home_text = '''
> 《伊索寓言》中收录有300多则寓言，内容大多与动物有关。书中讲述的故事简短精练，刻画出来的形象鲜明生动，每则故事都蕴含哲理，或揭露和批判社会矛盾，或抒发对人生的领悟，或总结日常生活经验。
---
> 📝 对话样例 👇
> - 你好，伊索。请给我讲一个关于狐狸的寓言故事。
> - 这个故事的寓意是什么？
> - 我不明白，请简单说明一下这个寓意。

'''


@st.cache_resource
def get_db_session(directory='fables_db'):
    from vecdb import load_vectordb
    vectordb = load_vectordb(directory)
    return vectordb


@st.cache_data
def get_fable(prompt):
    vectordb = get_db_session()
    results = vectordb.similarity_search_with_score(prompt, k=1)
    if results[0][1] < 0.35:
        response = results[0][0].page_content.split('\n')
        response = '\n\n'.join(response[4:7])
        response = response.replace("Title_CN:", "###").replace(
            "Fable_CN: ", "").replace("Moral_CN:", "`")+"`"
    else:
        response = ''
    return response


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.checkbox("Clear History"):
    st.session_state.messages = []

if st.session_state.messages == []:
    st.markdown(home_text)
    
only_for_chat = st.sidebar.checkbox('Only For Chat')

for message in st.session_state.messages:
    if message["role"] == 'system':
        pass
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if prompt := st.chat_input("问一下伊索?"):
    if not only_for_chat:
        if fable := get_fable(prompt):
            placeholder = st.sidebar.empty()
            placeholder.info(f"{fable}")
            st.session_state.messages.append(
                {'role': 'system', 'content': '\n请参考下面的故事回答问题：\n'+fable})

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages,
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})