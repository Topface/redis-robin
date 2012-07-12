#!/usr/bin/env python

import socket
import time


class Logger(object):

    def __init__(self, path, verbose):
        self.fd      = open(path, "a")
        self.verbose = verbose


    def write(self, message):
        self.fd.write(self.get_line(message) + "\n")
        if self.verbose:
            print self.get_line(message)


    def get_line(self, message):
        return time.strftime("[%Y-%m-%d %H:%m:%S] ") + message


    def __del__(self):
        self.fd.close()


class Redis(object):

    def __init__(self, host, port):
        self.host   = host
        self.port   = port
        self.logger = None


    def set_logger(self, logger):
        self.logger = logger


    def log(self, message):
        if self.logger is not None:
            self.logger.write("[" + self.host + ":" + str(self.port) + "] " + message)


    def simple_ask(self, command, arguments = []):
        redis = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
        redis.connect((self.host, self.port))

        redis.send("*" + str(1 + len(arguments)) + "\r\n")
        redis.send("$" + str(len(command)) + "\r\n")
        redis.send(command + "\r\n")
        for argument in arguments:
            redis.send("$" + str(len(argument)) + "\r\n")
            redis.send(argument + "\r\n")

        response = redis.recv(65536)

        redis.close()

        return "\n".join(response.split("\r\n")[1:-1])


    def get_info(self):
        result = {}
        for line in self.simple_ask("INFO").split("\n"):
            if len(line) == 0:
                continue
            (key, value) = line.split(":")
            result[key] = value
        return result


    def get_save_value(self):
        return self.simple_ask("config", ["get", "save"]).split("\n")[3]


    def is_saving(self):
        return int(self.get_info()["bgsave_in_progress"]) == 1


    def check(self):
        if len(self.get_save_value()) > 0:
            self.log("save value is set!")
            return False
        if self.is_saving():
            self.log("already saving!")
            return False
        return True

    def save(self):
        self.log("starting bgsave..")
        self.simple_ask("BGSAVE")
        while True:
            if not self.is_saving():
                break
            time.sleep(1)
        self.log("finished bgsave")

class Robin(object):

    def __init__(self, instances, logger, success_file):
        self.instances    = instances
        self.logger       = logger
        self.success_file = success_file

    def run(self):
        success = True
        for instance in self.instances:
            if not self.process_instance(instance):
                success = False

        if success and self.success_file is not None:
            with open(self.success_file, "w") as success_file:
                success_file.write(str(int(time.time())) + "\n")


    def process_instance(self, instance):
        redis = Redis(instance[0], instance[1])
        try:
            if logger:
                redis.set_logger(self.logger)
            if redis.check():
                redis.save()
                return True
            return False
        except Exception as e:
            redis.log("Got exception: " + str(e))
            return False



if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Save redis data to disk for good.")
    parser.add_argument("-c", "--config-file", help="config file location", default="/etc/redis-robin.conf", type=str, metavar="path")
    parser.add_argument("-l", "--log-file", help="log file location", type=str, metavar="path")
    parser.add_argument("-s", "--success-file", help="file to store latest success unix timestamp", type=str, metavar="path")
    parser.add_argument("-v", "--verbose", help="duplocate log to stdout", action="store_true")

    args = parser.parse_args(sys.argv[1:])

    def get_instances(config_file_path):
        instances = []
        with open(config_file_path, "r") as config_file:
            for line in config_file.read().split("\n"):
                line = line.strip()
                if len(line) < 1 or line[0] == '#':
                    continue
                (host, port) = line.split(":")
                instances.append((host, int(port)))
        return instances

    logger = None
    if args.log_file is not None:
        logger = Logger(args.log_file, args.verbose)

    robin = Robin(get_instances(args.config_file), logger, args.success_file)
    robin.run()
