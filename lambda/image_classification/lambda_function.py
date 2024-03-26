import json
import requests

import boto3
import base64

smr_client = boto3.client("sagemaker-runtime")

def encode_image(url):
    img_str = base64.b64encode(requests.get(url).content)
    base64_string = img_str.decode("latin1")
    return base64_string


def run_inference(endpoint_name, inputs):
    response = smr_client.invoke_endpoint(EndpointName=endpoint_name, Body=json.dumps(inputs))
    return response["Body"].read().decode("utf-8")


response = {
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Origin": '*'
    },
    "isBase64Encoded": False
}

def lambda_handler(event, context):
    
    print("event:",event)
    evt_body = event
    if 'queryStringParameters' in event.keys():
        evt_body = event['queryStringParameters']
        
    url = ""
    if "url" in evt_body.keys():
        url = evt_body['url']
    print('url:',url)
    
    task = "classification"
    if "task" in evt_body.keys():
        task = evt_body['task']
    print('task:',task)
    
    endpoint_name = ''
    if "endpoint_name" in evt_body.keys():
        endpoint_name = evt_body['endpoint_name']
    print('endpoint_name:',endpoint_name)
    
    protential_tags = ""
    if "protential_tags" in evt_body.keys():
        protential_tags = evt_body['protential_tags']
    print('protential_tags:',protential_tags)
    
    if task == "classification":
        protential_tags = protential_tags.split(',')
        tag_confidentials = {}
        if len(endpoint_name) >0 and len(url) > 0 and len(protential_tags) > 0:
            prompts = [f"a photo of {item}" for item in protential_tags]
            base64_string = encode_image(url)
            inputs = {"image": base64_string, "prompt": prompts}
            
            output = run_inference(endpoint_name, inputs)
            print('output:',output)
            
            confidential_scores = json.loads(output)[0]
            print('confidential_scores:',confidential_scores)
            
            tag_confidentials = dict(zip(protential_tags,confidential_scores))
            print('tag_confidentials',tag_confidentials)
        
        response['body'] = json.dumps(
        {
            'tag_confidentials': tag_confidentials
        })
    
    elif task == "image_embedding":
        
        image_embedding = ''
        if len(endpoint_name) >0 and len(url) > 0:
            base64_string = encode_image(url)
            inputs = {"image": base64_string}
            output = run_inference(endpoint_name, inputs)
            output = json.loads(output)
            image_embedding = output['image_embedding'][0]
        response['body'] = json.dumps(
        {
            'image_embedding': image_embedding
        })
        
    elif task == "text_embedding":
        
        text_embedding = ''
        if len(endpoint_name) >0 and len(protential_tags) > 0:
            inputs = {"prompt": protential_tags}
            output = run_inference(endpoint_name, inputs)
            output = json.loads(output)
            text_embedding = output['text_embedding'][0]
        response['body'] = json.dumps(
        {
            'text_embedding': text_embedding
        })
        
    
    return response
        

