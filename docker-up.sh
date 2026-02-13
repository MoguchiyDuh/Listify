#!/bin/bash
docker compose up --build -d
echo "Waiting for backend to be ready..."
sleep 5
docker compose exec backend alembic upgrade head
echo "Stack is up and migrations are applied."
