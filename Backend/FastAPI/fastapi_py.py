
from fastapi import FastAPI
import tensorflow as pd

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}