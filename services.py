import pathlib
from datetime import datetime

now = datetime.now()
date = now.strftime("%Y-%m-%d")
time = now.strftime("%H-%M")

def create_folder(query, keyword=False):
    query = query.lower().replace(" ", "_")
    PATH = f'data/{date}/{time}/{query}/'
    pathlib.Path(PATH).mkdir(parents=True, exist_ok=True)
    return PATH


