from fastapi import FastAPI
from pydantic import BaseModel

app =FastAPI()

class User(BaseModel):
    name: str
    email: str
    password: str

@app.post('/user')
def create_user(request: User):
    return request

