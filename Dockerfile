FROM python:3.12

ADD main.py .

COPY dependencies.txt .

RUN pip install -r dependencies.txt

CMD ["python", "./main.py"]
