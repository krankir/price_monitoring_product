FROM python:3.9-slim

RUN mkdir /mvideo_scrap_bot

WORKDIR /mvideo_scrap_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
# run app
CMD ["python3", "mvideo_scrap_price_bot.py"]