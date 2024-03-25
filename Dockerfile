# Production Dockerfile
FROM python:3.11

# Install supervisord
RUN apt-get update && apt-get install -y supervisor

RUN python3 -m pip install --upgrade pip
COPY ./requirements.txt /workspace/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /workspace/backend/requirements.txt
COPY ./gunicorn.conf.py /workspace/gunicorn.conf.py
COPY ./backend /workspace/backend
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /workspace

EXPOSE 8080
ENV TZ="America/New_York"

# CMD ["gunicorn", "-c", "gunicorn.conf.py", "backend.main:app"]
CMD ["/usr/bin/supervisord"]