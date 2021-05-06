# file logger
This example shows how to install a program onto a Linux system using
the pipenv2deb tool.

## Program to be installed
The python code logs data to a file and records the PID of process.

```
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
```


## Required files
The only required file is debian/control. This provides some details on the program.

```
Package: python-file-logger
Section: Python
Priority: optional
Architecture: amd64
Essential: no
Maintainer: Paul Austen <pausten.os@gmail.com>
Description: pipenv2deb example code that run a process that will start when the computer starts.
Version: 1.0
```

This example includes a debian/preinst file that checks for the existence of the pip3
and pip3env packages that must be present on the target system in order to
install the virtual environment.

The debian/postinst, debian/prerm and debian/postrm files are present but empty.

#Creating the virual environment
Before the program can be executed or packaged the python virtual environment must be built. Execute the create_virtual_env.sh to do this.
E.G

```
./create_pip_env.sh
Creating a virtualenv for this project...

...

Installing dependencies from Pipfile.lock (db4242)...
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 0/0 — 00:00:00
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
```

## Building the deb file
Once the virtual environment has been created the debian package maybe created using the following command.

```
sudo python3 -m pipenv2deb
INFO:  Set executable attribute: create_pip_env.sh
INFO:  Copied root-fs to build
INFO:  Created build/DEBIAN
INFO:  Created build/usr/local/bin/python-file-logger.pipenvpkg

...

INFO:  Creating build/DEBIAN/postinst
INFO:  Set executable attribute: build/DEBIAN/postinst
INFO:  Set executable attribute: build/DEBIAN/postrm
INFO:  Set executable attribute: build/DEBIAN/control
INFO:  Set executable attribute: build/DEBIAN/postinst
INFO:  Set executable attribute: build/DEBIAN/prerm
INFO:  Set executable attribute: build/DEBIAN/preinst
INFO:  Created: build/usr/local/bin/file_logger
INFO:  Set executable attribute: build/usr/local/bin/file_logger
INFO:  Executing: dpkg-deb -Zgzip -b build packages/python-file-logger-1.0-amd64.deb
dpkg-deb: building package 'python-file-logger' in 'packages/python-file-logger-1.0-amd64.deb'.
INFO:  Removed build path
```

## Installing the hello-world Program
The debian package is installed as shown below

```
sudo dpkg -i packages/python-file-logger-1.0-amd64.deb
#Selecting previously unselected package python-file-logger.
(Reading database ... 447928 files and directories currently installed.)
Preparing to unpack .../python-file-logger-1.0-amd64.deb ...
Unpacking python-file-logger (1.0) ...
Setting up python-file-logger (1.0) ...

...

✔ Successfully created virtual environment!
Virtualenv location: /usr/local/bin/python-file-logger.pipenvpkg/.venv
Installing dependencies from Pipfile.lock (db4242)...
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 0/0 — 00:00:00
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
********************************************
*** The file_logger command is installed ***
********************************************

To start the file logger service enter 'sudo service file_logger start'
To stop the file logger service enter 'sudo service file_logger stop'

Processing triggers for systemd (245.4-4ubuntu3.6) ...
```

## Checking the logger programming is running
As described when the logger was installed run the following command to start the file logger running

```
sudo service file_logger start
```

Check the logger is running by running

```
tail -f /var/log/file_log.txt
count=1
count=2
count=3
count=4
count=5
count=6
count=7
count=8
count=9
count=10
count=11
count=12
count=13
```

Running the following command will stop the file logger running.

```
sudo service file_logger stop
```

## Uninstalling the file logger program
The debian package is installed as shown below

```
udo dpkg -r python-file-logger
(Reading database ... 447936 files and directories currently installed.)
Removing python-file-logger (1.0) ...
**************************************************
*** The file logger command is going to be removed
**************************************************
************************************************
*** The file_logger command has been removed ***
************************************************
Processing triggers for systemd (245.4-4ubuntu3.6) ...
```
