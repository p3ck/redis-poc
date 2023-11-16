## Compose sample application

### Python/Flask application using a Redis database

## Deploy with podman-compose

```
$ podman-compose up -d
```

## Expected result

Listing containers must show one container running and the port mapping as below:

## Monitoring Redis keys

Connect to redis database by using ```redis-cli``` command and monitor the keys.
```
redis-cli -p 6379
127.0.0.1:6379> monitor
OK
1646634062.732496 [0 172.21.0.3:33106] "INCRBY" "hits" "1"
1646634062.735669 [0 172.21.0.3:33106] "GET" "hits"
```


Stop and remove the containers
```
$ docker compose down
```
