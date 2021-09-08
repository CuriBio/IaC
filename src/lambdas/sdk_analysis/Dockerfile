FROM python:3.9-slim


COPY ./src/app.py   ./
COPY ./src/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

CMD ["python", "./app.py"]
