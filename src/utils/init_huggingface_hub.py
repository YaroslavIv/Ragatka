import os
from huggingface_hub import login
from dotenv import load_dotenv

def init_huggingface_hub():
    load_dotenv()
    huggingface_token = os.getenv("HUGGINGFACE_HUB_TOKEN")

    if huggingface_token:
        login(token=huggingface_token)
    else:
        raise ValueError("HUGGINGFACE_HUB_TOKEN not found. Please set it in .env.")