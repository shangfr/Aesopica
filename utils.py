# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 16:57:00 2023

@author: shangfr
"""
import json
import requests

def get_access_token(ak,sk):
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """

    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}"

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def aigc_image(access_token, prompt, negative_prompt="", size="1024x768", steps=50, n=4):

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/sd_xl?access_token=" + access_token

    payload = json.dumps({
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "size": size,
        "steps": steps,
        "n": n,
        "sampler_index": "DPM++ SDE Karras"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()


def table_html(n):
    td = '''<td style="width: 50%; border: 1px solid black;">
<img src="data:image/PNG;base64,{}" style="width: 100%; height: auto;" />
</td>
'''

    match n:
        case 1:
            trtd = f"<tr>{td}</tr>"
            html_code = f"""<table style="width: 100%; border-collapse: collapse;">{trtd}</table>"""
            return html_code
        case 2:
            trtd = f"<tr>{td}</tr>\n<tr>{td}</tr>"
            html_code = f"""<table style="width: 100%; border-collapse: collapse;">{trtd}</table>"""
            return html_code
        case 3:
            trtd = f"<tr>{td}\n{td}</tr>\n<tr>{td}</tr>"
            html_code = f"""<table style="width: 100%; border-collapse: collapse;">{trtd}</table>"""
            return html_code
        case 4:
            trtd = f"<tr>{td}\n{td}</tr>\n<tr>{td}\n{td}</tr>"
            html_code = f"""<table style="width: 100%; border-collapse: collapse;">{trtd}</table>"""
            return html_code
        

from zhipuai import ZhipuAI
client = ZhipuAI() 

def aigc_image_url(prompt):

    response = client.images.generations(
        model="cogview-3", 
        prompt=prompt,
    )
    return response.data[0].url

