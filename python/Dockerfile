FROM python:3.9
COPY video_extract.py /app/script.py
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
CMD ["python", "/app/script.py"]
