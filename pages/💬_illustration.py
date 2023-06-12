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

openai.api_key = os.getenv("OPENAI_API_KEY")

os.environ['CURL_CA_BUNDLE'] = ''


if 'text2img' not in st.session_state:
    with open('prompts_dict.json', "r", encoding='utf8') as json_file:
        st.session_state['text2img'] = json.load(json_file)


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

option = st.sidebar.selectbox('文生图',('生成', '查看'))

match option:
    case '查看':
        data_df = pd.DataFrame(st.session_state['text2img']['info'])
        
        st.data_editor(
            data_df,
            column_config={
                "url": st.column_config.ImageColumn(
                    "Preview Image", help="Streamlit app preview screenshots"
                )
            },
            hide_index=True,
        )


    case '生成':

        col0,col1 = st.sidebar.columns(2)
        number = col0.number_input('寓言选择：', 0, df.shape[0])
        qlt = col1.selectbox('生成质量',('一般', '差', '好'))
        
        fable = df['Fable'][number]
        st.markdown(f"{fable}")
        
        prompt = get_prompt(fable)
        st.caption(prompt)
        
        img_url = get_image_url(prompt)
        st.markdown(f"![]({img_url})")
        
        output_dict = {"id": number,
                       "prompt": prompt,
                       "url": img_url,
                       "quality": qlt}
        
        with st.sidebar:
            if st.button('保存'):
                st.write('DO IT.')
                st.session_state['text2img']['info'].append(output_dict)
        
                with open('prompts_dict.json', 'w', encoding='utf8') as f:
                    json.dump(st.session_state['text2img'],
                              f, ensure_ascii=False, indent=2)
        
            else:
                st.caption('Save prompt & illustration.')
