# -*- coding: utf-8 -*-
"""
Created on Wed May 31 15:38:04 2023

@author: shangfr
"""
import os
import time
import qianfan
import streamlit as st

os.environ["QIANFAN_AK"] = st.secrets["llm_baidu"]["QIANFAN_AK"]
os.environ["QIANFAN_SK"] = st.secrets["llm_baidu"]["QIANFAN_SK"]


# Setting page title and header
st.set_page_config(
    page_title="Aesopica",
    page_icon="📚",
    layout="wide",
    # initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/shangfr/shangfr.github.io',
        'Report a bug': "https://github.com/shangfr/shangfr.github.io",
        'About': "FollowAI. 对话伊索讲寓言."
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

with st.sidebar:
    col0,col1 = st.columns([2,1])
    RAG = col1.checkbox('RAG')
    stream = col1.checkbox('Stream',value=True)
    model = col0.selectbox(
        '模型',
        ('ERNIE-Bot', 'ERNIE-Bot-turbo', 'ERNIE-Bot-4'))

@st.cache_resource
def get_db_session(directory='fables_db'):
    from vecdb import load_vectordb
    vectordb = load_vectordb(directory)
    return vectordb


@st.cache_data
def get_fable(prompt):
    vectordb = get_db_session()
    results = vectordb.similarity_search_with_score(prompt, k=1)
    if results[0][1] > 0.8:
        response = results[0][0].page_content.split('\n')
        response = '\n\n'.join(response[1:-1])
        response = response.replace("Title_CN:", "###").replace(
            "Fable_CN: ", "").replace("Moral_CN:", "`")+"`"
    else:
        response = ''
    return response


def reset():
    st.session_state.messages = []
    st.session_state.system_role = ""

if "messages" not in st.session_state:
    reset()

if st.sidebar.button("Clear History",use_container_width=True):
    reset()
    
if st.session_state.messages == []:
    st.markdown(home_text)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("问一下伊索?"):
    
    with st.chat_message("user"):
        st.info(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
    if RAG:
        if fable := get_fable(prompt):
            st.session_state.system_role = '\n请参考下面的故事回答问题：\n'+fable
            with st.expander("参考"):
                st.info(f"{fable}")
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in qianfan.ChatCompletion().do(
                model=model,
                messages=st.session_state.messages,
                system=st.session_state.system_role,
                stream=stream):
            rr = response['result']
            for i in range(len(rr)):
                full_response += rr[i]
                message_placeholder.markdown(full_response)
                time.sleep(0.05)
        message_placeholder.success(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
