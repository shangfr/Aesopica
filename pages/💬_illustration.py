# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 16:31:04 2023

@author: shangfr
"""
import os
import json
import openai
import streamlit as st
import pandas as pd

openai.api_key = st.secrets['api_key']

os.environ['CURL_CA_BUNDLE'] = ''

st.markdown("<h1 style='text-align: center;'>🧩 AIGC - 插图</h1>",
            unsafe_allow_html=True)

if 'text2img' not in st.session_state:
    with open('prompts_dict.json', "r", encoding='utf8') as json_file:
        st.session_state['text2img'] = json.load(json_file)


@st.cache_data
def save_local(output_dict):
    st.session_state['text2img']['info'].append(output_dict)
    with open('prompts_dict.json', 'w', encoding='utf8') as f:
        json.dump(st.session_state['text2img'],
                  f, ensure_ascii=False, indent=2)


@st.cache_data
def get_fable():
    df = pd.read_csv('data_csv/books_all.csv')
    return df


@st.cache_data
def get_prompt(fable):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Read the short story below."},
            {"role": "assistant", "content": fable},
            {"role": "user", "content": "Using 10 words, provide the main characters in the story's context, including their modifiers."}
        ]
    )

    result = response.choices[0]["message"]["content"]
    return result


@st.cache_data
def get_image_bytes(prompt):
    import io
    import requests
    from PIL import Image
    #API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

    headers = {"Authorization": st.secrets['API_TOKEN']}
    payload = {'inputs': prompt,  "parameters": {'height': 512, 'width': 768}}
    response = requests.post(API_URL, headers=headers, json=payload)

    image = Image.open(io.BytesIO(response.content))
    #st.image(img, prompt)
    # img.save("test.png")
    return image


@st.cache_data
def get_image_url(prompt):

    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']

    return image_url


df = get_fable()

col0, col1 = st.sidebar.columns(2)

option = col0.selectbox('文生图', ('生成', '查看'))

if option == '查看':
    data_df = pd.DataFrame(st.session_state['text2img']['info'])

    st.data_editor(
        data_df,
        column_config={
            "url": st.column_config.ImageColumn(
                "Preview Image", help="Streamlit app preview screenshots"
            ),
            "quality": st.column_config.SelectboxColumn(
                "App Category",
                help="The category of the app",
                width="medium",
                options=[
                    "一般",
                    "差",
                    "好",
                ],
            )
        },
        hide_index=True,
    )


elif option == '生成':
    cola, colb = st.columns([3,2])
    container = colb.container()
    
    number = col1.number_input('寓言选择：', 0, df.shape[0])

    fable = df['Fable'][number]
    cola.markdown(f"{fable}")

    if st.sidebar.button(label='开始', use_container_width=True):
        prompt = get_prompt(fable)
        container.caption(prompt)
        img_url = get_image_url(prompt)
        if img_url:
            container.markdown(
                f'<img src="{img_url}" width = "100%" height = "100%" alt="fable" align=center />', unsafe_allow_html=True)
            output_dict = {"id": number,
                           "prompt": prompt,
                           "url": img_url,
                           "quality": "一般"}
            save_local(output_dict)
