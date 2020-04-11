# Roslynka bot (WIP)

Run application:
```shell script
docker-compose up app
```

Generate database schema migration:
```shell script
CURRENT_UID=$(id -u):$(id -g) docker-compose run --rm app db migrate -m "Initial migration"
```

Migrate database schema:
```shell script
docker-compose run --rm app db upgrade
```
