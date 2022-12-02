import pathlib
from datetime import datetime


def create_folder(query):
    query = query.lower().replace(" ", "_")
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H-%M")
    PATH =f'data/{date}/{time}/{query}'
    pathlib.Path(PATH).mkdir(parents=True, exist_ok=True)
    return PATH