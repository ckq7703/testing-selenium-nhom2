import json
import os

def load_test_data(filename):
    path = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
