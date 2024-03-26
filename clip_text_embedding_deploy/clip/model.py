import hashlib
import math
import numpy as np
import os,io
import requests
import time
import torch
from PIL import Image
import base64
from io import BytesIO
import json

from dataclasses import dataclass
from transformers import CLIPProcessor, CLIPModel, AutoTokenizer
from tqdm import tqdm
from typing import List, Optional
from djl_python import Input, Output
from safetensors.numpy import load_file, save_file



@dataclass 
class Config:
    # models can optionally be passed in directly
    caption_model = None
    caption_tokenizer = None
    
    clip_offload: bool = False
    
    device: str = ("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")

   
class Clip():
    def __init__(self, config: Config, properties):
        self.config = config
        self.device = config.device
        self.dtype = torch.float16 if self.device == 'cuda' else torch.float32
        self.load_clip_model(properties)
        self.caption_offloaded = True

    def load_clip_model(self, properties):
        if self.config.caption_model is None:
            model_path = properties["model_id"]
            if any(os.listdir(model_path)):
                files_in_folder = os.listdir(model_path)
                print('model path files:')
                for file in files_in_folder:
                    print(file)
            else:
                raise ValueError('Please make sure the model artifacts are uploaded to s3')

            print(f'model path: {model_path}')
            model = CLIPModel.from_pretrained(model_path, cache_dir="/tmp",)
            self.caption_tokenizer = AutoTokenizer.from_pretrained(model_path)

            model.eval()
            if not self.config.clip_offload:
                model = model.to(self.config.device)
            self.caption_model = model
        else:
            self.caption_model = self.config.caption_model
            self.caption_tokenizer = self.config.caption_tokenizer

    def generate_caption(self, prompt: str) -> str:
        assert self.caption_model is not None, "No caption model loaded."
        self._prepare_caption()
        
        prompt = prompt.split(',')
        inputs = self.caption_tokenizer(prompt, padding=True, return_tensors="pt").to(self.device)
        inputs = inputs.to(self.dtype)
        
        with torch.no_grad():
            text_tensor = self.caption_model.get_text_features(**inputs)
        
        text_features = {'text_embedding':text_tensor.tolist()}
        return text_features

    def _prepare_caption(self):
        if self.caption_offloaded:
            self.caption_model = self.caption_model.to(self.device)
            self.caption_offloaded = False


config = None
_service = None

def handle(inputs: Input) -> Optional[Output]:
    global config, _service
    if not _service:
        config = Config()
        _service = Clip(config, inputs.get_properties())
    
    if inputs.is_empty():
        return None
    data = inputs.get_as_json()
    
    if 'prompt' in data:
        prompt = data.pop("prompt")
    else:
        prompt = None
            
    probs = _service.generate_caption(prompt)

    return Output().add(probs)
