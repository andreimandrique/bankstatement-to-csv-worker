import os
import boto3
import pdfplumber
import csv
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

s3 = boto3.client(
    service_name='s3',
    endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name='auto', 
)

def process_bankstatement(**kwargs):
    
    file_bucket = kwargs.get('fileBucket') 
    file_key = kwargs.get('fileKey')
    file_name = kwargs.get('fileName') 
    google_id = kwargs.get('googleId')

    s3.download_file(file_bucket, file_key, f"{file_name}.pdf")

    pdf_filename = f"{file_name}.pdf"
    csv_filename = f"{file_name}.csv"

    with pdfplumber.open(pdf_filename) as pdf:
        
        page = pdf.pages[0]

        page_height = page.height
        page_width = page.width

        bbox = (0,272, page_width, 740)
        cropped_page = page.crop(bbox)

        table = cropped_page.extract_table({
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        })

        clean_table = []
        for row in table:
            if any(cell.strip() for cell in row if cell):
                clean_table.append(row)

        final_table = []
        for row in clean_table:
            description = " ".join(row[1:4]).strip()
            col4 = row[4].lstrip('P')
            col5 = row[5].lstrip('P')
            col6 = row[6].lstrip('P')
            new_row = [row[0], description, col4, col5, col6]
            final_table.append(new_row)

        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(final_table)
      
    s3.upload_file(f"{file_name}.csv", file_bucket, f"bankstatement-csv/{file_name}.csv", ExtraArgs={'ContentType': 'text/csv'})

    Path(pdf_filename).unlink(missing_ok=True)
    Path(csv_filename).unlink(missing_ok=True)

    url = os.getenv('BACKEND_URL')
    data = {
        "success": 'true',
        "google_id": google_id
    }

    try:
        requests.post(f"{url}/transaction", json=data, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"request error: {e}")

