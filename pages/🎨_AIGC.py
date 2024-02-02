# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 16:31:04 2023

@author: shangfr
"""
import streamlit as st
from styles import sdxl_styles
from utils import aigc_image, table_html

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

st.markdown("<h1 style='text-align: center;'>📚 Stable Diffusion XL</h1>",
            unsafe_allow_html=True)


if "access_token" not in st.session_state:
    from utils import get_access_token
    ak = st.secrets["llm_baidu"]["QIANFAN_AK"]
    sk = st.secrets["llm_baidu"]["QIANFAN_SK"]
    st.session_state.access_token = get_access_token(ak, sk)


@st.cache_data
def st_aigc_image(**kwargs):
    aigc_image(**kwargs)


on = st.toggle('中文模式')

if on:
    style_sd = sdxl_styles["styles_cn"]
    prompt_demo = "穿着蓝色太空服的大熊猫，坐在酒吧里，富士XT3相机，远景拍摄"
else:
    style_sd = sdxl_styles["styles"]
    prompt_demo = "panda wearing a blue spacesuit, sitting in a bar, Fujifilm XT3, long shot"

cola, colb = st.columns(2)

with cola:
    col0, col1 = st.columns(2)

    n = col0.slider(
        '生成图片数量',
        1, 4, 1, 1, help="默认值为1，取值范围为1-4，单次生成的图片较多及请求较频繁可能导致请求超时。")

    steps = col1.slider(
        '迭代轮次',
        10, 50, 20, 5, help="默认值为20，取值范围为10-50。")

    size = col0.selectbox(
        '生成图片长宽',
        ["1024x576", "1024x768", "1024x1024", "768x768", "576x1024", "768x1024"])

    style = col1.selectbox(
        '风格', [s["Style"] for s in style_sd]
    )
    style_dcit = [s for s in style_sd if s["Style"] == style][0]

    prompt = st.text_area(
        "提示词",
        prompt_demo,
    )
    prompt = style_dcit['Prompt'].format(prompt)
    ph0 = st.caption(prompt)

    access_token = st.session_state["access_token"]

    with st.expander("Advanced"):
        negative_prompt = st.text_area(
            "反向提示词",
            style_dcit['Negative prompt'],
        )

with colb:
    ph1 = st.image(f'static/styles/{style}.png', caption=style)

if prompt and cola.button(label='开始', use_container_width=True):
    results = aigc_image(prompt, access_token, negative_prompt, size, steps, n)
    if results.get('error_code'):
        st.error(results)
        st.stop()
    img_lst = [r['b64_image'] for r in results['data']]
    html_code = table_html(n)
    ph0.empty()
    ph1.empty()
    ph1.markdown(html_code.format(*img_lst), unsafe_allow_html=True)
