FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY exporter.py run.sh ./
EXPOSE 8001
CMD ["bash","run.sh"]
