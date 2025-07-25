import os
import pickle
from typing import Dict

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

def classify_content(content: str) -> Dict:
    theme_path = os.path.join(ROOT_PATH, 'pickles/theme_model.pkl')
    with open(theme_path, 'rb') as f:
        theme_model = pickle.load(f)

    defi_path = os.path.join(ROOT_PATH, 'pickles/defi_model.pkl')
    with open(defi_path, 'rb') as f:
        defi_model = pickle.load(f)

    theme_pred = theme_model.predict([content])[0]
    defi_pred = defi_model.predict([content])[0]

    return {
        "theme": theme_pred,
        "defi": defi_pred
    }
