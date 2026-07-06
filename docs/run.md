### Sync Commands

#### Sync Everything
Sync all data (contacts, products, and sale orders) with optional limits.

```command
docker compose run --rm app python main.py --all

docker compose run --rm app python main.py --all --contacts-limit 10 --products-limit 10 --orders-limit 10
```

#### Sync Contacts Only

```command
docker compose run --rm app python main.py --contacts
```

#### Sync Products Only

```command
docker compose run --rm app python main.py --products
```

#### Sync Sale Orders Only

```command
docker compose run --rm app python main.py --orders
```

#### Check Sync Status
```command
docker compose run --rm app python main.py --status
```

#### Get Help With The Commands
```command
docker compose run --rm app python main.py --help
```