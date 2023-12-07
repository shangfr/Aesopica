# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 16:31:04 2023

@author: shangfr
"""
import streamlit as st
import pandas as pd
from uitls import aigc_image, table_html

# Setting page title and header
st.set_page_config(
    page_title="AIGC",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Klkqubb9w',
        'Report a bug': "https://github.com/Stability-AI/generative-models",
        'About': "Stable Diffusion XL是一个二阶段的级联扩散模型，包括Base模型和Refiner模型。其中Base模型的主要工作和Stable Diffusion一致，具备文生图，图生图，图像inpainting等能力。在Base模型之后，级联了Refiner模型，对Base模型生成的图像Latent特征进行精细化，其本质上是在做图生图的工作。"
    }
)

st.markdown("<h1 style='text-align: center;'>🧩 AIGC - 插图</h1>",
            unsafe_allow_html=True)

if "access_token" not in st.session_state:
    from utils import get_access_token
    ak = st.secrets["llm_baidu"]["QIANFAN_AK"]
    sk = st.secrets["llm_baidu"]["QIANFAN_SK"]
    st.session_state.access_token = get_access_token(ak, sk)


@st.cache_data
def st_aigc_image(**kwargs):
    aigc_image(**kwargs)


@st.cache_data
def get_fable():
    df = pd.read_csv('data_csv/books_all.csv')
    return df


@st.cache_data
def get_prompt(fable):
    import qianfan
    response = qianfan.ChatCompletion().do(
        model=model,
        messages=[
            {"role": "user", "content": "Read the following short story:"},
            {"role": "assistant", "content": fable},
            {"role": "user", "content": "Write a descriptive sentence to illustrate a story."}
        ],
        system="You are an excellent assistant.",
    )
    result = response['result']
    return result


col0, col1 = st.columns([1, 2])
model = col0.selectbox(
    '模型',
    ('ERNIE-Bot', 'ERNIE-Bot-turbo', 'ERNIE-Bot-4'))

df = get_fable()

number = col0.number_input('寓言选择', 0, df.shape[0], value=1)

title = df.loc[number]['Title_CN']
fable = df.loc[number]['Fable_CN']
moral = df.loc[number]['Moral_CN']

col1.markdown(f"### `{title}`\n\n{fable}\n\n`{moral}`")

if col0.button(label='生成插图', use_container_width=True):
    prompt = df.loc[number]['Title']+" "+get_prompt(df.loc[number]['Fable'])
    prompt = f"comic {prompt} . graphic illustration, comic art, graphic novel art, vibrant, highly detailed"
    results = aigc_image(prompt, st.session_state["access_token"])
    img_lst = [r['b64_image'] for r in results['data']]
    html_code = table_html(4)
    st.markdown(html_code.format(*img_lst), unsafe_allow_html=True)
