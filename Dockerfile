FROM python:3.10-slim

LABEL maintainer="gitdeeper@gmail.com"
LABEL version="1.0.0"
LABEL description="STRATICA - Stratigraphic Pattern Recognition Framework"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STRATICA_HOME=/opt/stratica \
    STRATICA_CONFIG=/etc/stratica/config.yaml

WORKDIR /opt/stratica

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

EXPOSE 8000 8501

CMD ["stratica", "serve", "--all"]
