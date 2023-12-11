# -*- coding: utf-8 -*-
"""
Created on Fri May 26 15:11:41 2023

@author: shangfr
"""

import pandas as pd

df = pd.read_csv('data_csv/books_all.csv')

dfa = df.loc[df['TOC']=="其他"]
dfa.loc[dfa['Title_CN'].str.contains('鹰'),'TOC']='鹰'
dfa.loc[dfa['Title_CN'].str.contains('蚂蚁'),'TOC']='蚂蚁'
dfa.loc[dfa['Title_CN'].str.contains('狮'),'TOC']='狮子'
dfa.loc[dfa['Title_CN'].str.contains('农夫'),'TOC']='农夫'
dfa.loc[dfa['Title_CN'].str.contains('牛'),'TOC']='牛'
dfa.loc[dfa['Title_CN'].str.contains('蛇'),'TOC']='蛇'


lst = " ".join(dfa['Title'].tolist()).split(" ")

out = pd.Series(lst).value_counts()
#df.to_csv('data_csv/books_all.csv',index=False)

'''
tle = df['Title_CN']


from paddlenlp import Taskflow
ner = Taskflow("ner")
tle_cluster = ner(tle.tolist())

any_t = [t[0] for tt in tle_cluster for t in tt if t[1]=='生物类_动物']
any_t1 = [t[0] for tt in tle_cluster for t in tt if t[1]=='生物类_植物']

ts = pd.Series(any_t).value_counts()
ts1 = pd.Series(any_t1).value_counts()
toc = ['狐狸', '狼', '狗', '驴', '青蛙', '猫', '山羊', '老鼠', '猴子', '公鸡']

def get_toc(title):
    
    for t in toc:
        if t in title:
            return t
        else:
            pass
            
df['TOC'] = df['Title_CN'].apply(get_toc)

df['TOC'].fillna("其他",inplace=True)

'''

#ebook_table = df[['ID', 'Title', 'Title_CN']].to_markdown(index=False)
#ebook += ebook_table+'\n\n'


def save_file(filename, content):
    with open(filename, 'w',encoding='utf-8') as f:
        f.write(content)


chat_url = "<p align='right'>[😺 不明白？问问伊索吧。](https://shangfr-aesopica-app-xr2547.streamlit.app/)</p>"
chat_url_cn = "<p align='right'>[😺 Not sure? Ask Aesop.](https://shangfr-aesopica-app-xr2547.streamlit.app/)</p>"



grouped = df.groupby('TOC')
sidebar="{sidebar}"
tabset="{tab-set}"
tabitem="{tab-item}"
admonition="{admonition}"
bg="{.bg-warning width=100px align=center}"



for name, group in grouped:
    ebook = f'# {name}篇\n> 共{len(group)}个寓言故事'

    for i, r in group.iterrows():
        url = f"https://quantile.shangfr.site/fables/audio{r['ID']}.mp3"
        url_cn = f"https://quantile.shangfr.site/fables/audio{r['ID']}_cn.mp3"

        fables = f'''
## {r['Title_CN']}  {r['Title']} 

<img src="../_static/illustration/{r['ID']}-{r['Title'].replace(" ","_")}-0.png" width=24.5% alt="插图1" />
<img src="../_static/illustration/{r['ID']}-{r['Title'].replace(" ","_")}-1.png" width=24.5% alt="插图2" />
<img src="../_static/illustration/{r['ID']}-{r['Title'].replace(" ","_")}-2.png" width=24.5% alt="插图3" />
<img src="../_static/illustration/{r['ID']}-{r['Title'].replace(" ","_")}-3.png" width=24.5% alt="插图4" />

::::{tabset}
:::{tabitem} 中文
{r['Fable_CN']}
```{admonition} **寓意**
:class: tip
> **{r['Moral_CN']}**  {chat_url}
👇 听寓言故事
<audio src='{url_cn}' style='width: 100%' preload='none' controls>你的浏览器不支持 audio 标签。</audio>
```
:::
:::{tabitem} English
{r['Fable']}
```{admonition} **Moral**
:class: tip
> **{r['Moral']}**  {chat_url_cn}
👇 Listen to this fable
<audio src='{url}' style='width: 100%' preload='none' controls>Your browser does not support the audio element.</audio>
```
:::
::::
'''
        ebook += fables
    
    save_file(f'docs/source/fables/{name}.md', ebook)



#```{sidebar} {r['Title_CN']}
#```
import base64
import qianfan
from utils import get_access_token,aigc_image
df = pd.read_csv('data_csv/books_all.csv')

access_token = get_access_token()


def get_prompt(fable):
    response = qianfan.ChatCompletion(ak="uEt8HHkVrwEHZWNnRG26Ck2P", sk="Fkr4VPTGMZoxfCTFwpbikkRsIcoGx25X").do(
        model='ERNIE-Bot',
        messages=[
            {"role": "user", "content": "Read the following short story:"},
            {"role": "assistant", "content": fable},
            {"role": "user", "content": "Write a descriptive sentence to illustrate a story."}
        ],
        system="You are an excellent illustrator.",
    )
    result = response['result']
    return result


for number in range(77,df.shape[0]):
    title = df.loc[number]['Title']
    prompt = title+" "+get_prompt(df.loc[number]['Fable'])
    prompt = f"comic {prompt} . graphic illustration, comic art, graphic novel art, vibrant, highly detailed"
    negative_prompt='photograph, deformed, glitch, noisy, realistic, stock photo'
    results = aigc_image(access_token,prompt,negative_prompt)
    img_lst = [r['b64_image'] for r in results['data']]

    for index, b64_str in enumerate(img_lst):
        # 解码Base64字符串为字节数据
        image_data = base64.b64decode(b64_str)
        with open(f'static/illustration/{number}-{title.replace(" ","_")}-{index}.png', 'wb') as file:
            file.write(image_data)













