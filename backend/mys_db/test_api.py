import json
from typing import Union
from fastapi import FastAPI

app = FastAPI()

def load_json_data(json_path):
    """Load data from a JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)

data = load_json_data('generated.json')

@app.get("/db")
def read_root():
    return data

