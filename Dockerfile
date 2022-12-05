FROM python:3.10

ADD main.py services.py arxiv_dl.py springer_dl.py apikey.txt ./

RUN pip install requests pandas arxiv

CMD ["python", "./main.py"]
