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

import fire
LLAMA_PATH = os.environ["LLAMA_PATH"]
sys.path.append(LLAMA_PATH)

from llama import Llama, Dialog



# #############
import pickle

chat_args = SimpleNamespace()
chat_args.model_path = os.getenv("LLAVA_CKPT_PATH")
chat_args.conv_mode = "v0_mmtag" # "multimodal"
chat_args.num_gpus = 1

# rich console for pretty printing
console = rich.console.Console()


query = "Describe the central object in the image."
pick_captions = []
put_captions = []
console.print("[bold red]User:[/bold red] " + query)

file_path = 'FloorPlan1_9685294.pkl'

with open(file_path, 'rb') as f:
    data = pickle.load(f)

file_path = 'refined_pick_captions.pkl'

with open(file_path, 'rb') as f:
    refined_pick_captions = pickle.load(f)

actions = data['action_list']
pick_counter = 0
# Loop through all images in the folder
for i in range(len(actions)):
    # if actions[i] == "open":
    #     print("###################################")

    #     query = "Describe which object in the image has been opened"

    #     image_file = f"images/{i}_{actions[i]}_{1}.jpg"
    #     args2 = type('Args', (), {
    #         "model_path": chat_args.model_path,
    #         "model_base": None,
    #         "model_name": get_model_name_from_path(chat_args.model_path),
    #         "query": query,
    #         "conv_mode":  chat_args.conv_mode,
    #         "image_file": image_file,
    #         "sep": ",",
    #         "temperature": 0,
    #         "top_p": None,
    #         "num_beams": 1,
    #         "max_new_tokens": 512
    #     })()

    #     output1 = eval_model(args2)

    #     image_file = f"images_action_crops/{i}_{1}.jpg"
    #     args2 = type('Args', (), {
    #         "model_path": chat_args.model_path,
    #         "model_base": None,
    #         "model_name": get_model_name_from_path(chat_args.model_path),
    #         "query": query,
    #         "conv_mode":  chat_args.conv_mode,
    #         "image_file": image_file,
    #         "sep": ",",
    #         "temperature": 0,
    #         "top_p": None,
    #         "num_beams": 1,
    #         "max_new_tokens": 512
    #     })()

    #     output2 = eval_model(args2)


    #     console.print(image_file)
    #     console.print("[bold green]LLaVA:[/bold green] " + output1)
    #     console.print("[bold green]LLaVA:[/bold green] " + output2)
    #     captions.append([output1,output2])

    # if actions[i] == "close":
    #     print("###################################")
        
    #     query = "Describe which object in the image has been opened"

    #     image_file = f"images/{i}_{actions[i]}_{0}.jpg"
    #     args2 = type('Args', (), {
    #         "model_path": chat_args.model_path,
    #         "model_base": None,
    #         "model_name": get_model_name_from_path(chat_args.model_path),
    #         "query": query,
    #         "conv_mode":  chat_args.conv_mode,
    #         "image_file": image_file,
    #         "sep": ",",
    #         "temperature": 0,
    #         "top_p": None,
    #         "num_beams": 1,
    #         "max_new_tokens": 512
    #     })()

    #     output1 = eval_model(args2)

    #     image_file = f"images_action_crops/{i}_{0}.jpg"
    #     args2 = type('Args', (), {
    #         "model_path": chat_args.model_path,
    #         "model_base": None,
    #         "model_name": get_model_name_from_path(chat_args.model_path),
    #         "query": query,
    #         "conv_mode":  chat_args.conv_mode,
    #         "image_file": image_file,
    #         "sep": ",",
    #         "temperature": 0,
    #         "top_p": None,
    #         "num_beams": 1,
    #         "max_new_tokens": 512
    #     })()

    #     output2 = eval_model(args2)


    #     console.print(image_file)
    #     console.print("[bold green]LLaVA:[/bold green] " + output1)
    #     console.print("[bold green]LLaVA:[/bold green] " + output2)
    #     captions.append([output1,output2])

    # if actions[i] == "take":
    #     print("###################################")

    #     query1 = "Describe the central object in the image"
    #     query2 = "Describe the object in the image"

    #     image_file = f"images/{i}_{actions[i]}_{1}.jpg"
    #     args1 = type('Args', (), {
    #         "model_path": chat_args.model_path,
    #         "model_base": None,
    #         "model_name": get_model_name_from_path(chat_args.model_path),
    #         "query": query1,
    #         "conv_mode":  chat_args.conv_mode,
    #         "image_file": image_file,
    #         "sep": ",",
    #         "temperature": 0,
    #         "top_p": None,
    #         "num_beams": 1,
    #         "max_new_tokens": 512
    #     })()

    #     output1 = eval_model(args1)

    #     image_file = f"images_ego_crops/{i}_{1}.jpg"
    #     args2 = type('Args', (), {
    #         "model_path": chat_args.model_path,
    #         "model_base": None,
    #         "model_name": get_model_name_from_path(chat_args.model_path),
    #         "query": query1,
    #         "conv_mode":  chat_args.conv_mode,
    #         "image_file": image_file,
    #         "sep": ",",
    #         "temperature": 0,
    #         "top_p": None,
    #         "num_beams": 1,
    #         "max_new_tokens": 512
    #     })()

    #     output2 = eval_model(args2)

    #     image_file = f"images_action_crops/{i}_{0}.jpg"
    #     args3 = type('Args', (), {
    #         "model_path": chat_args.model_path,
    #         "model_base": None,
    #         "model_name": get_model_name_from_path(chat_args.model_path),
    #         "query": query2,
    #         "conv_mode":  chat_args.conv_mode,
    #         "image_file": image_file,
    #         "sep": ",",
    #         "temperature": 0,
    #         "top_p": None,
    #         "num_beams": 1,
    #         "max_new_tokens": 512
    #     })()

    #     output3 = eval_model(args3)


    #     console.print(image_file)
    #     console.print("[bold green]LLaVA:[/bold green] " + output1)
    #     console.print("[bold green]LLaVA:[/bold green] " + output2)
    #     console.print("[bold green]LLaVA:[/bold green] " + output3)
    #     pick_captions.append([output1,output2,output3])

#     if actions[i] == "put":
#         print("###################################")
        
#         query1 = "Describe the central object in the image"
#         query2 = "Describe the object in the image"

#         image_file = f"images/{i}_{actions[i]}_{0}.jpg"
#         args2 = type('Args', (), {
#             "model_path": chat_args.model_path,
#             "model_base": None,
#             "model_name": get_model_name_from_path(chat_args.model_path),
#             "query": query1,
#             "conv_mode":  chat_args.conv_mode,
#             "image_file": image_file,
#             "sep": ",",
#             "temperature": 0,
#             "top_p": None,
#             "num_beams": 1,
#             "max_new_tokens": 512
#         })()

#         output1 = eval_model(args2)

#         image_file = f"images_ego_crops/{i}_{0}.jpg"
#         args2 = type('Args', (), {
#             "model_path": chat_args.model_path,
#             "model_base": None,
#             "model_name": get_model_name_from_path(chat_args.model_path),
#             "query": query1,
#             "conv_mode":  chat_args.conv_mode,
#             "image_file": image_file,
#             "sep": ",",
#             "temperature": 0,
#             "top_p": None,
#             "num_beams": 1,
#             "max_new_tokens": 512
#         })()

#         output2 = eval_model(args2)
        
# #removed since objects are not placed in action grids:
#         # image_file = f"images_action_crops/{i}_{1}.jpg"
#         # args3 = type('Args', (), {
#         #     "model_path": chat_args.model_path,
#         #     "model_base": None,
#         #     "model_name": get_model_name_from_path(chat_args.model_path),
#         #     "query": query2,
#         #     "conv_mode":  chat_args.conv_mode,
#         #     "image_file": image_file,
#         #     "sep": ",",
#         #     "temperature": 0,
#         #     "top_p": None,
#         #     "num_beams": 1,
#         #     "max_new_tokens": 512
#         # })()

#         # output3 = eval_model(args3)


#         console.print(image_file)
#         console.print("[bold green]LLaVA:[/bold green] " + output1)
#         console.print("[bold green]LLaVA:[/bold green] " + output2)
#         console.print("[bold green]LLaVA:[/bold green] " + output3)
#         put_captions.append([output1,output2,output3])


# file_path = "put_captions.pkl"

# # Open the file in binary write mode
# with open(file_path, 'wb') as f:
#     pickle.dump(put_captions, f)

# file_path = "pick_captions.pkl"

# # Open the file in binary write mode
# with open(file_path, 'wb') as f:
#     pickle.dump(pick_captions, f)











    if actions[i] == "take":
        obj = refined_pick_captions[pick_counter]['object_tag'][0]
        print("###################################")

        query1 = "Describe the central object in the image"
        query2 = "Describe where the"+obj+"is placed."

        image_file = f"images/{i}_{actions[i]}_{1}.jpg"
        args1 = type('Args', (), {
            "model_path": chat_args.model_path,
            "model_base": None,
            "model_name": get_model_name_from_path(chat_args.model_path),
            "query": query1,
            "conv_mode":  chat_args.conv_mode,
            "image_file": image_file,
            "sep": ",",
            "temperature": 0,
            "top_p": None,
            "num_beams": 1,
            "max_new_tokens": 512
        })()

        output1 = eval_model(args1)

        image_file = f"images/{i}_{actions[i]}_{1}.jpg"
        args2 = type('Args', (), {
            "model_path": chat_args.model_path,
            "model_base": None,
            "model_name": get_model_name_from_path(chat_args.model_path),
            "query": query2,
            "conv_mode":  chat_args.conv_mode,
            "image_file": image_file,
            "sep": ",",
            "temperature": 0,
            "top_p": None,
            "num_beams": 1,
            "max_new_tokens": 512
        })()

        output2 = eval_model(args2)

        image_file = f"images_action_crops/{i}_{0}.jpg"
        args3 = type('Args', (), {
            "model_path": chat_args.model_path,
            "model_base": None,
            "model_name": get_model_name_from_path(chat_args.model_path),
            "query": query2,
            "conv_mode":  chat_args.conv_mode,
            "image_file": image_file,
            "sep": ",",
            "temperature": 0,
            "top_p": None,
            "num_beams": 1,
            "max_new_tokens": 512
        })()

        output3 = eval_model(args3)

        image_file = f"images_ego_crops/{i}_{0}.jpg"
        args4 = type('Args', (), {
            "model_path": chat_args.model_path,
            "model_base": None,
            "model_name": get_model_name_from_path(chat_args.model_path),
            "query": query2,
            "conv_mode":  chat_args.conv_mode,
            "image_file": image_file,
            "sep": ",",
            "temperature": 0,
            "top_p": None,
            "num_beams": 1,
            "max_new_tokens": 512
        })()

        output4 = eval_model(args4)


        console.print(image_file)
        console.print("[bold green]LLaVA:[/bold green] " + output1)
        console.print("[bold green]LLaVA:[/bold green] " + output2)
        console.print("[bold green]LLaVA:[/bold green] " + output3)
        console.print("[bold green]LLaVA:[/bold green] " + output3)
        pick_captions.append([output4,output2,output3])
        pick_counter = pick_counter + 1