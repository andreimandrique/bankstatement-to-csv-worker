from process_task import process_bankstatement
import os
import boto3
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

s3 = s3 = boto3.client(
    service_name='s3',
    endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name='auto', 
)

app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))

@app.task(name="tasks.add") 
def add(**kwargs):
    
    file_bucket = kwargs.get('fileBucket') 
    file_key = kwargs.get('fileKey')
    file_name = kwargs.get('fileName') 
    
    print(f"Bucket: {file_bucket}")
    print(f"Key: {file_key}")
    print(f"Name: {file_name}")

    s3.download_file(file_bucket, file_key, f"{file_name}.pdf")
    
    return True