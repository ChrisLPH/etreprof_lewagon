from fastapi import FastAPI
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_package.models import classify_content


app = FastAPI(title="ÊtrePROF Classification API", version="1.0.0")

@app.get("/")
def root():
    return {"greetings": "Welcome !", "status": "running"}

@app.post("/classify")
def classify(content: str):
    result = classify_content(content)
    return {"success": True, "data": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
