# hello-world
This example shows how to install a program onto a Linux system using
the pipenv2deb tool.

## Program to be installed
The python code simply prints Hello World to stdout on the terminal from which
it is invoked. The hello-world.py file contains the following

```
#!/usr/bin/env python3

def main():
    print("Hello World")

if __name__ == '__main__':
    main()

```


## Required files
The only required file is debian/control. This provides some details on the program.

```
Package: python-hello-world
Section: Python
Priority: optional
Architecture: amd64
Essential: no
Maintainer: Paul Austen <pausten.os@gmail.com>
Description: pipenv2deb example code that insalls the hello-world python command.
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

Installing dependencies from Pipfile.lock (a8bd1f)…
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 2/2 — 00:00:04
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.

```

Once this has been done the program maybe executed inside the virtual environment using the following command.

```
pipenv run ./hello-world.py
Hello World

```

## Building the deb file
Once the virtual environment has been created the debian package maybe created using the following command.

```
sudo python3 -m pipenv2deb
INFO:  Removed build path
INFO:  Set executable attribute: create_pip_env.sh
INFO:  Copied root-fs to build
INFO:  Created build/DEBIAN

...

INFO:  Creating build/DEBIAN/postinst
INFO:  Set executable attribute: build/DEBIAN/postinst
INFO:  Set executable attribute: build/DEBIAN/control
INFO:  Set executable attribute: build/DEBIAN/postinst
INFO:  Set executable attribute: build/DEBIAN/preinst
INFO:  Created: build/usr/local/bin/hello_world
INFO:  Set executable attribute: build/usr/local/bin/hello_world
INFO:  Executing: dpkg-deb -Zgzip -b build packages/python-hello-world-1.0-amd64.deb
dpkg-deb: building package 'python-hello-world' in 'packages/python-hello-world-1.0-amd64.deb'.
INFO:  Removed build path

```

## Installing the hello-world Program
The debian package is installed as shown below

```
sudo dpkg -i packages/python-hello-world-1.0-amd64.deb
Selecting previously unselected package python-hello-world.
(Reading database ... 414511 files and directories currently installed.)
Preparing to unpack .../python-hello-world-1.0-amd64.deb ...
Unpacking python-hello-world (1.0) ...
Setting up python-hello-world (1.0) ...

```

## Running the hello-world command
Assuming that /usr/local/bin is in your path you can now run the program on the command line of any terminal.

E.G

```
hello_world
Hello World

```

## Uninstalling the hello-world Program
The debian package is installed as shown below

```
sudo dpkg -r python-hello-world
(Reading database ... 415089 files and directories currently installed.)
Removing python-hello-world (1.0) ..
```
