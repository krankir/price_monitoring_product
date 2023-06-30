from fastapi import FastAPI

from price_monitoring.router import router as router_monitoring


app = FastAPI(
    title='Monitoring price'
)

app.include_router(router_monitoring)
