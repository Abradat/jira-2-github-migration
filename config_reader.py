
import json

def load_config(config_file):
    with open(config_file, mode='r', encoding='utf-8') as file:
        config = json.load(file)
    return config