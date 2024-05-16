"""
Build a scene graph from the segment-based map and captions from LLaVA.
"""

import gc
import gzip
import json
import os
import pickle as pkl
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import List, Literal, Union
from textwrap import wrap

import cv2
import matplotlib.pyplot as plt

import numpy as np
import rich
import torch
import tyro
from PIL import Image
from tqdm import tqdm, trange
from transformers import logging as hf_logging

import sys
LLAVA_PYTHON_PATH = os.environ["LLAVA_PYTHON_PATH"]
sys.path.append(LLAVA_PYTHON_PATH)

from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path
from llava.eval.run_llava import eval_model

from typing import List, Optional
LLAMA_PATH = os.environ["LLAMA_PATH"]
sys.path.append(LLAMA_PATH)

from llama import Llama, Dialog


import pickle



def prjson(input_json, indent=0):
    """ Pretty print a json object """
    if not isinstance(input_json, list):
        input_json = [input_json]
        
    print("[")
    for i, entry in enumerate(input_json):
        print("  {")
        for j, (key, value) in enumerate(entry.items()):
            terminator = "," if j < len(entry) - 1 else ""
            if isinstance(value, str):
                formatted_value = value.replace("\\n", "\n").replace("\\t", "\t")
                print('    "{}": "{}"{}'.format(key, formatted_value, terminator))
            else:
                print(f'    "{key}": {value}{terminator}')
        print("  }" + ("," if i < len(input_json) - 1 else ""))
    print("]")


ckpt_dir = "/home/hypatia/Sachin_Workspace/llama/llama-2-7b-chat"
tokenizer_path = "/home/hypatia/Sachin_Workspace/llama/tokenizer.model"

generator = Llama.build(
    ckpt_dir=ckpt_dir,
    tokenizer_path=tokenizer_path,
    model_parallel_size = 1,
    max_seq_len=2000,
    max_batch_size=6,
)

from LLAMAPrompt import LLAMAPrompt
gpt_messages = LLAMAPrompt().get_json()

file_path = 'pick_captions.pkl'

with open(file_path, 'rb') as f:
    data = pickle.load(f)

print(str(data[0]))

TIMEOUT = 25  # Timeout in seconds

responses = []
unsucessful_responses = 0


# loop over every object
for i in trange(len(data)):
    
    # Prepare the object prompt 
    _dict = {}
    _dict["captions"] = data[i][:2]
    # _dict["low_confidences"] = _caption["low_confidences"]
    # Convert to printable string
    
    # Make and format the full prompt
    preds = json.dumps(_dict, indent=0)

    start_time = time.time()

    curr_chat_messages = gpt_messages[:]
    curr_chat_messages.append({"role": "user", "content": preds})
    # print(curr_chat_messages)
            

#######################################################################
    #LLM: GPT 4
    # chat_completion = openai.ChatCompletion.create(
    #     # model="gpt-3.5-turbo",
    #     model="gpt-4",
    #     messages=curr_chat_messages,
    #     timeout=TIMEOUT,  # Timeout in seconds
    # )

    # for dialog, result in zip(curr_chat_messages, chat_completion):
    #     for msg in dialog:
    #         print(f"{msg['role'].capitalize()}: {msg['content']}\n")
    #     print(
    #         f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
    #     )
    #     print("\n==================================\n")

        
    # count unsucessful responses
    
    
    # responses.append(chat_completion["choices"][0]["message"]["content"].strip("\n"))

#######################################################################
    #LLM: LLAMA

    
    curr_chat_messages = [curr_chat_messages] 

    chat_completion = generator.chat_completion(
        curr_chat_messages,  # type: ignore
        max_gen_len=512,
        temperature=0.6,
        top_p=0.9,
    )

    torch.cuda.empty_cache()
    import gc
    gc.collect()

    elapsed_time = time.time() - start_time
    if elapsed_time > TIMEOUT:
        print("Timed out exceeded!")
        _dict["response"] = "FAIL"
        # responses.append('{"object_tag": "FAIL"}')
        # save_json_to_file(_dict, responses_savedir / f"{_caption['id']}.json")
        responses.append(json.dumps(_dict))
        unsucessful_responses += 1
        continue
    
    if "invalid" in chat_completion[0]['generation']['content'].strip("\n"):
        unsucessful_responses += 1

    # print output
    prjson([{"role": "user", "content": preds}])
    print(chat_completion[0]['generation']['content'])
    print(f"Unsucessful responses so far: {unsucessful_responses}")
    _dict["response"] = chat_completion[0]['generation']['content'].strip("\n")
    responses.append(json.loads(_dict["response"]))
    # save the response

print(responses)

file_path = "refined_pick_captions.pkl"

# Open the file in binary write mode
with open(file_path, 'wb') as f:
    pickle.dump(responses, f)