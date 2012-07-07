# Redis Robin

Redis robin will help you to keep bunch of redis servers from saving to disk at the same time.
Define your pool, add redis-robin to crontab and monitor your cluster with zabbix (or not).

## Why do I need it?

Redis itself may save data to disk, of course.

But if you have 8 redis servers on 8 CPU and 8Gb server under load and each redis server keeps 800Mb of memory,
you may go out of memory all of your redis servers start saving at the same moment. Redis Robin will prevent them
from this mistake. It will save every server one after another keeping some free memory for everybody.

Just as simple as that.

## Configuration

Disable `save` option in your redis.config for each server to keep them from making it automatically.

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

If you want to be sure that everything goes okay with your redis servers' persistence, you may monitor redis-robin with zabbix.

1. Make sure that you use `--success-file` (`-s`) option when you run `redis-robin`. For example, you keep success file in `/tmp/redis-robin.success`.

2. Add item to zabbix to monitor success file mtime: `vfs.file.time[/tmp/redis-robin.success,modify]`.

3. Add `fuzzytime` trigger to your item. If you want to keep your pool not above 10 minutes from persistent storage (disk): `{webserver:vfs.file.time[/tmp/redis-robin.success,modify]}.fuzzytime(600)}=0`.

This will fire your trigger if last success save of your pool was more than 10 minutes (600 seconds) in the past.

## Author

* [Ian Babrou](https://github.com/bobrik)
