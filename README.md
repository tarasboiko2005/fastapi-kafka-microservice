# FastAPI Event-Driven Microservice 🚀

An asynchronous Python microservice for order management built with **FastAPI** and **Apache Kafka**. This project demonstrates the principles of distributed systems, data reliability, and modern backend architecture.

## 🛠 Tech Stack
* **Framework:** FastAPI (Asynchronous)
* **Database:** PostgreSQL + SQLAlchemy 2.0 (Async)
* **Migrations:** Alembic
* **Messaging:** Apache Kafka (aiokafka)
* **Auth:** JWT (HS256)
* **Monitoring:** Structured Logging & Timing Middleware
* **Infrastructure:** Docker & Docker Compose
* **CI/CD:** GitHub Actions (Linting & Build Checks)

## 🌟 Key Features & Reliability
This project implements critical patterns for scalable and production-ready systems:
- **Event-Driven Architecture:** Every order status change triggers a Kafka event for asynchronous downstream processing.
- **Retry Logic & DLQ (Dead Letter Queue):** The worker implements **Exponential Backoff** for error handling. Messages that fail after 3 retries are automatically routed to the `orders.failed` topic for manual inspection.
- **Cloud-Ready (K8s Healthchecks):** Dedicated `/health/live` and `/health/ready` endpoints are implemented to support Kubernetes Liveness and Readiness probes.
- **Database Versioning:** Managed database schema evolution using Alembic migrations.
- **Observability:** Centralized logging and custom middleware to track request execution time and performance.
- **Automated Quality Control:** A CI/CD pipeline ensures PEP8 compliance (flake8) and validates Docker builds on every Pull Request.


## 🏗 Project Structure
- `app/routers/` — API Layer (Controllers)
- `app/services/` — Business Logic Layer
- `app/repositories/` — Data Access Layer (Repository Pattern)
- `app/worker.py` — Kafka Consumer with robust error handling logic
- `.github/workflows/` — CI/CD Pipeline configurations
- `docker-compose.yml` — Orchestrates the entire system (API, Worker, Kafka, Zookeeper, PostgreSQL)
- `alembic/` — Database migration scripts
- `README.md` — Project documentation and setup instructions
- `requirements.txt` — Python dependencies

### 🚀 How to Run

## 1. Prepare Environment
Create a .env file in the root directory (refer to .env.example for required variables). You can control the number of workers here:

```Bash
WORKER_REPLICAS=3  # Number of parallel workers
KAFKA_NUM_PARTITIONS=3 # Match partitions with worker count
```

2. Launch System

```Bash
docker-compose up --build
Note: The backend will automatically run migrations and start the server. Three worker instances will start to listen for events.
```

3. Explore API
Swagger UI: http://localhost:8000/docs

Health Status: http://localhost:8000/health/ready

Worker Logs: 
```Bash
docker compose logs -f worker
```

### 4. Explore API

Swagger UI: http://localhost:8000/docs

Health Status: http://localhost:8000/health/ready

Metrics: http://localhost:8000/metrics