#!/usr/bin/env python3

import  os
from    time import sleep

def main():

    pid=os.getpid()
    fd = open("/var/run/file_logger.pid", 'w')
    fd.write("{}\n".format(pid))
    fd.close()

    count=0
    while True:
        fd = open("/var/log/file_log.txt", 'a')
        fd.write("count={}\n".format(count))
        fd.close()
        sleep(1)
        count=count+1

if __name__ == '__main__':
    main()
