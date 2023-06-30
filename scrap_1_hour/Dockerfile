FROM python:3.9-slim

RUN mkdir /scrap_1_hour

WORKDIR /scrap_1_hour

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
# run app
CMD ["python3", "scrap_price_each_hour.py"]