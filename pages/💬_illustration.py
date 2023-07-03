# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 16:31:04 2023

@author: shangfr
"""
import os
import uuid
import openai
import streamlit as st
import pandas as pd

openai.api_key = st.secrets['api_key']

os.environ['CURL_CA_BUNDLE'] = ''

st.markdown("<h1 style='text-align: center;'>🧩 AIGC - 插图</h1>",
            unsafe_allow_html=True)

if 'text2img' not in st.session_state:
    pictures = pd.read_csv('data_csv/pictures.csv')
    st.session_state['text2img'] = pictures.loc[pictures["quality"] == '好']

@st.cache_data   
def save_image(srs):
    
    import requests
    if srs['save']:
        return True
    else:
        url = srs['url']
    
        filename = f"static/illustration/{srs['id']}_{srs['uuid']}.jpg"
        
        response = requests.get(url)
        
        with open(filename, "wb") as f:
            f.write(response.content)
            
        return True
    

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

    edited_df = st.data_editor(
        st.session_state['text2img'],
        column_config={
            "url": st.column_config.ImageColumn(
                "Preview", 
                width="medium",
                help="Preview Image"
            ),
            "quality": st.column_config.SelectboxColumn(
                "Quality",
                help="The quality of the image",
                options=[
                    "一般",
                    "差",
                    "好",
                ],
            )
        },
        hide_index=True,
    )
    st.session_state['text2img'] = edited_df
    edited_df.to_csv('data_csv/pictures.csv',index=False)
    edited_df.loc[edited_df["quality"] == '好','save'] = edited_df.loc[edited_df["quality"] == '好'].apply(save_image,axis=1)


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
            
            u = uuid.uuid3(uuid.NAMESPACE_DNS, img_url)
            uid = str(u).replace("-", "")
            
            container.markdown(
                f'<img src="{img_url}" width = "100%" height = "100%" alt="fable" align=center />', unsafe_allow_html=True)
            output_dict = {"id": number,
                           "quality": "一般",
                           "url": img_url,
                           "uuid":uid,
                           "save":False,
                           "prompt": prompt
                           }
            st.session_state['text2img'] = pd.concat([st.session_state['text2img'],  pd.DataFrame.from_dict([output_dict])], ignore_index=True)
    else:
        pictures = st.session_state['text2img']
        fable_pictures = pictures[(pictures['id'] == number) & (pictures['quality']=='好')]
        if len(fable_pictures)>0:
            from PIL import Image
            img_url = f"static/illustration/{number}_{fable_pictures['uuid'].tolist()[0]}.jpg" 
            image = Image.open(img_url)
            container.image(image, caption=fable_pictures['prompt'].tolist()[0])