# Scanbandz Backend

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Note: This project is no longer maintained. Originally private, some parts may need updating for open-source use. It was part of a larger project, but only the backend is included here. Feel free to ask questions or report issues.

Scanbandz processed over $100,000 in payments and donations, and I’m open-sourcing it in case it's helpful to others. In production, the backend ran as a scalable cluster with PostgreSQL and Redis databases, and Celery workers handled background tasks like ticket sending. If revisiting, I would 1) add Redis-backed rate limiting to authentication endpoints and 2) move workers to a separate Docker image and separate workers by task type (e.g., payments, ticketing, communications).

I wrote this three times over my college career. The first time was when I learned to code (entirely in Django), the second time was fixing all my mistakes (still in Django), and the third was after much experience and separating the frontend and backend (FastAPI). It was a great learning experience, and I hope it helps you too. I will never open source my Django code as it haunts my sleep.

Note: Instructions for running may need troubleshooting due to the quick port to open source.

## Features

- FastAPI backend with multiple APIs to manage events, guests, tickets, and payments.
- Integration with Celery and Redis for background task processing.
- Support for PostgreSQL database with SQLAlchemy and Alembic for migrations.
- Docker and Docker Compose support for development and production.
- Supervisord for process management in production.

## Table of Contents

- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Directory Structure](#directory-structure)
- [License](#license)

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/scanbandz-backend.git
cd scanbandz-backend
```

Install dependencies (recommended to use a virtual environment):

```bash
pip install -r requirements.txt
```

Make sure to set up the required environment variables in a `.env` file, copy `.env.template` to `.env` and fill in the required values.
**Environment file is expected in the `backend/settings` directory.**

## Running the Application

To run the application using Gunicorn (no support for Celery workers):

```bash
gunicorn -c gunicorn.conf.py backend.main:app
```

Or use supervisord to manage processes (server and Celery workers):

```bash
supervisord -c supervisord.conf
```

### Docker

For production, the app is containerized using Docker. To build and run the app with Docker Compose:

```bash
docker-compose up --build
```

The backend will be available at http://localhost:8080.

For local development, use the .devcontainer setup:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

This will spin up the development environment with a PostgreSQL database.

## Development Setup

1. Clone the repository and navigate to the project directory.
2. Install dependencies via pip or Docker as shown above.
3. For development, you can use the provided VSCode .devcontainer for remote container development.
4. Set up the PostgreSQL database for development:

```bash
docker-compose -f .devcontainer/dev-docker-compose.yml up
```

5. Run database migrations:

```bash
alembic upgrade head
```

## Production Setup

The production Docker setup uses supervisord to manage both Gunicorn and Celery workers.

### Dockerfile (Production)

To build and run the production setup:

```bash
docker build -t scanbandz-backend .
docker run -p 8080:8080 scanbandz-backend
```

## Directory Structure

```bash
.
├── backend
│   ├── apis          # API endpoints
│   ├── assets        # Email templates
│   ├── communication # Azure email client interfaces
│   ├── entities      # Database entities (SQLAlchemy)
│   ├── exceptions    # Custom exceptions
│   ├── migrations    # Alembic migrations
│   ├── models        # Pydantic models
│   ├── scripts       # Utility DB scripts
│   ├── services      # Business logic for various services
│   ├── settings      # Configs, logging, and celery workers
├── alembic.ini       # Alembic configuration file
├── Dockerfile        # Production Dockerfile
├── docker-compose.yml # Docker Compose for production
├── requirements.txt  # Python dependencies
├── supervisord.conf  # Supervisor configuration
├── gunicorn.conf.py  # Gunicorn configuration
└── .devcontainer     # Development container configuration
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Key Sections Explained:

- **Features**: Highlights the major functionalities of your backend.
- **Installation**: Provides steps to set up the project.
- **Running the Application**: Details how to run the application with `gunicorn`, `supervisord`, and Docker.
- **Development & Production Setup**: Shows how to run the app locally and in production.
- **Directory Structure**: Offers an overview of the backend folder and key files for new developers to navigate through.
- **License**: Specifies that the project is open-sourced under the MIT License.

Let me know if you need any modifications or additions!
