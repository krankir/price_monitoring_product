from fastapi import FastAPI

app = FastAPI(
    title='Monitoring price'
)


@app.get('/')
def home():
    return('Hello my litl poni!')

