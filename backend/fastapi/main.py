from fastapi import FastAPI

app = FastAPI()


@app.get("/status")
def read_root():
    return "OK"
