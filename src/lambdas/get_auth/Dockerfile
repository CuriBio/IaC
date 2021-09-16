FROM public.ecr.aws/lambda/python:3.8.2021.03.22.18


COPY ./src/app.py   ./
COPY ./src/requirements.txt ./requirements.txt
CMD ["app.handler"]
