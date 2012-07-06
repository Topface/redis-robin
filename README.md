# Redis Robin

Redis robin will help you to keep bunch of redis servers from saving to disk at the same time.
Define your pool, add redis-robin to crontab and monitor your cluster with zabbix (or not).

## Configuration

Example configuration file (`/etc/redis-robin.conf` used by default):

```
# This is comment line.
# Every used line is host:port string of redis server
# from the pool you want to save one after another.

# this server will be saved first
127.0.0.1:10001
# this server will be saved after first
127.0.0.1:10002
# this server will be saved last
127.0.0.1:10003
```

## Running

Don't forget to disable implicit save in `redis.conf` for every redis-server in pool.

Getting help:

```
redis-robin.py -h
```

Getting things done:

```
redis-robin.py -c /etc/redis-robin.conf -l /var/log/redis-robin.log -s /tmp/redis-robin.state
```

It's very useful too add this line to crontab, just like that:

```
# saving the whole pool one-by-one every hour
0 * * * * /usr/bin/redis-robin.py -c /etc/redis-robin.conf -l /var/log/redis-robin.log -s /tmp/redis-robin.state
```

## Monitoring with zabbix

To be written.

## Author

* [Ian Babrou](https://github.com/bobrik)
