# -*- coding: utf-8 -*-
"""
Created on Fri May 26 15:11:41 2023

@author: shangfr
"""

import pandas as pd

df = pd.read_csv('data_csv/books_all.csv')
df.to_csv('data_csv/books_all.csv',index=False)

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


chat_url = "<p align='right'>[😺 不明白？问问伊索吧。](//shangfr-aesopica-app-xr2547.streamlit.app/)</p>"
chat_url_cn = "<p align='right'>[😺 Not sure? Ask Aesop.](//shangfr-aesopica-app-xr2547.streamlit.app/)</p>"



grouped = df.groupby('TOC')

for name, group in grouped:
    ebook = f'# {name}篇\n\n'

    for i, r in group.iterrows():
        url = f"http://quantile.shangfr.site/fables/audio{r['ID']}.mp3"
        url_cn = f"http://quantile.shangfr.site/fables/audio{r['ID']}_cn.mp3"
        


        moral = "```{admonition} **Moral**\n:class: tip\n"+f"> {r['Moral']}  {chat_url_cn}\n\n👇 Listen to this fable\n\n<audio src='{url}'  style='width: 100%' preload='none' controls>Your browser does not support the audio element.</audio>\n\n```"
        moral_cn =  "```{admonition} **寓意**\n:class: tip\n"+f"> {r['Moral_CN']}  {chat_url}\n\n👇 听寓言故事\n\n<audio src='{url_cn}'  style='width: 100%' preload='none' controls>你的浏览器不支持 audio 标签。</audio>\n\n```" 

        doc = f"{r['Fable']}\n\n{moral}\n\n"
        doc_cn = f"{r['Fable_CN']}\n\n{moral_cn}\n\n"
        
        fables = f"## {r['Title_CN']}\n\n"+'''
::::{tab-set}
:::{tab-item} 中文
'''+doc_cn+''' 
:::
:::{tab-item} English
'''+f"## {r['Title']}\n\n"+doc+ ''' 
:::
::::
    
'''   
    
        ebook += fables
    
    save_file(f'docs/source/fables/{name}.md', ebook)


