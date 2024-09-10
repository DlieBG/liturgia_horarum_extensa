from crawl import get_days_of_prayer
from fastapi import FastAPI


app = FastAPI()

@app.get('/')
def get():
    return get_days_of_prayer()
