# Production Dockerfile
FROM python:3.11
RUN python3 -m pip install --upgrade pip
COPY ./requirements.txt /workspace/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /workspace/backend/requirements.txt
COPY ./gunicorn.conf.py /workspace/gunicorn.conf.py
COPY ./backend /workspace/backend
WORKDIR /workspace

EXPOSE 8080
ENV TZ="America/New_York"

CMD ["gunicorn", "-c", "gunicorn.conf.py", "backend.main:app"]