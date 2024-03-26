import requests
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd

threshold = 0.95

def get_protential_tags(image_url,protential_tags,classification_invoke_url,endpoint_name):
    url = classification_invoke_url + '/image_classification?'
    url += ('&url='+image_url)
    url += ('&protential_tags='+protential_tags)
    url += ('&endpoint_name='+endpoint_name)
    
    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print("result:",result)
    tag_confidentials = result['tag_confidentials']
    
    return tag_confidentials

def get_image_embedding(image_url,classification_invoke_url,endpoint_name):
    url = classification_invoke_url + '/image_classification?'
    url += ('&url='+image_url)
    url += ('&endpoint_name='+endpoint_name)
    url += ('&task=image_embedding')

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    #print("result:",result)
    image_embedding = result['image_embedding']

    return image_embedding

def get_text_embedding(protential_tags,classification_invoke_url,endpoint_name):
    url = classification_invoke_url + '/image_classification?'
    url += ('&protential_tags='+protential_tags)
    url += ('&endpoint_name='+endpoint_name)
    url += ('&task=text_embedding')

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    #print("result:",result)
    text_embedding = result['text_embedding']

    return text_embedding



# Re-initialize the chat
def new_image() -> None:
    st.session_state.url = ''
    st.session_state.protential_tags = ''
    
    
with st.sidebar:

    classification_invoke_url = st.text_input(
        "Please input a image classification api url",
        "",
        key="classification_invoke_url",
    )
    classification_endpoint = st.text_input(
        "Please input image classification sagemaker endpoint",
        "",
        key="classification_endpoint",
    )
    task  = st.radio("Task",["classification","image_embedding","text_embedding"])    

# Add a button to start a new chat
st.sidebar.button("New Image", on_click=new_image, type='primary')

st.session_state.url = st.text_input(label="Please input image URL", value="")
st.session_state.protential_tags = st.text_input(label="Please input protential tags,such as: cats,dogs,birds,trees", value="")

if st.button('Get Image Category'):
    if len(st.session_state.url) ==0:
        st.write("Image url is None")
    elif len(st.session_state.protential_tags) == 0:
        st.write("protential tags is None")
    elif len(classification_invoke_url) == 0:
        st.write("classification invoke url is None")
    elif len(classification_endpoint) == 0:
        st.write("classification sagemaker endpoint is None")
    else:

        if task == 'classification':
            tag_confidentials = get_protential_tags(st.session_state.url,st.session_state.protential_tags,classification_invoke_url,classification_endpoint) 
            st.write('tag confidentials')
            category = [tag for tag in tag_confidentials if tag_confidentials[tag] > threshold]
        
            tags = list(tag_confidentials.keys())
            scores = [round(score,3) for score in tag_confidentials.values()]
            data = {
                "category": tags,
                "scores": scores
            }
            df = pd.DataFrame(data)
            st.dataframe(df)
            st.write('Category:')
            st.write(category)
        elif task == 'image_embedding':
            image_embedding = get_image_embedding(st.session_state.url,classification_invoke_url,classification_endpoint)
            st.write(image_embedding)
        elif task == 'text_embedding':
            text_embedding = get_text_embedding(st.session_state.protential_tags,classification_invoke_url,classification_endpoint)
            st.write(text_embedding)