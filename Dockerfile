FROM python:3.11

RUN pip install -U --pre python-telegram-bot

ADD main.py .

CMD ["python", "main.py"]