from dotenv import load_dotenv, find_dotenv
from models import DayOfPrayer
from datetime import datetime
import requests, os

load_dotenv(find_dotenv())

cache = []

def get_days_of_prayer() -> list[DayOfPrayer]:
    global cache

    if not cache or cache[0].date != datetime.now().date().isoformat():
        cache = __crawl_days_of_prayer()
    
    return cache

def __crawl_days_of_prayer() -> list[DayOfPrayer]:
    response = requests.post(
        url=os.getenv('UPSTREAM_API_URL'),
    )

    return [
        DayOfPrayer.model_validate(
            obj=item,
        ) for item in response.json()['items']
    ]
