# Run all tests (mappers + repositories + services)
```command
docker compose run --rm app pytest tests/ -v
```

# Run all tests with coverage report
```command
docker compose run --rm app pytest tests/ -v --cov=. --cov-report=term
```

# Run all tests with detailed output
```command
docker compose run --rm app pytest tests/ -v -s
```