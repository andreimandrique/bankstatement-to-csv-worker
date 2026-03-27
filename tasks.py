import os
from celery import Celery
from dotenv import load_dotenv
from process_task import process_bankstatement

load_dotenv()

app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))

@app.task(name="tasks.add") 
def add(**kwargs):
    return process_bankstatement(**kwargs)