# gui-hello-world
This example shows how to install a GUI program onto a Linux system using
the pipenv2deb tool.

## Program to be installed
The python code simply prints Hello World in a small window when
it is invoked. The gui-hello-world.py file contains the following

```
#!/usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QPushButton

app = QApplication([])
app.setStyle('Fusion')
palette = QPalette()
palette.setColor(QPalette.ButtonText, Qt.red)
app.setPalette(palette)
button = QPushButton('Hello World')
button.show()
app.exec_()

```

## Required files
The only required file is debian/control. This provides some details on the program.

```
Package: python-gui-hello-world
Section: Python
Priority: optional
Architecture: amd64
Essential: no
Maintainer: Paul Austen <pausten.os@gmail.com>
Description: pipenv2deb example code that installs the gui-hello-world python command.
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
./create_virtual_env.sh
The pypi server must be running before running this.
Installing dependencies from Pipfile.lock (ca72e7)…
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 0/0 — 00:00:00
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
```

Once this has been done the program maybe executed inside the virtual environment using the following command.

```
pipenv run ./gui-hello-world.py

```

## Building the deb file
Once the virtual environment has been created the debian package maybe created using the following command.

```
sudo pipenv2deb
Checking PEP 508 requirements…
Passed!
Checking installed package safety…
All good!
INFO:  Copied root-fs to build
INFO:  Created build/DEBIAN
INFO:  Set executable attribute: build/DEBIAN/postinst
INFO:  Set executable attribute: build/DEBIAN/postrm
INFO:  Set executable attribute: build/DEBIAN/prerm
INFO:  Set executable attribute: build/DEBIAN/preinst
INFO:  Set executable attribute: build/DEBIAN/control
INFO:  Created build/usr/local/bin/python-gui-hello-world.pipenvpkg
INFO:  Copied virtual environment to build/usr/local/bin/python-gui-hello-world.pipenvpkg/.venv
INFO:  Copied Pipfile to build/usr/local/bin/python-gui-hello-world.pipenvpkg
INFO:  Copied /scratch/git_repos/python3/pipenv2deb/examples/gui_hello_world/gui-hello-world.py to build/usr/local/bin/python-gui-hello-world.pipenvpkg
INFO:  Created: build/usr/local/bin/gui-hello-world
INFO:  Set executable attribute: build/usr/local/bin/gui-hello-world
INFO:  Executing: dpkg-deb -Zgzip -b build packages/python-gui-hello-world-1.0-amd64.deb
dpkg-deb: building package 'python-gui-hello-world' in 'packages/python-gui-hello-world-1.0-amd64.deb'.
INFO:  Removed build path
```

## Installing the hello-world Program
The debian package is installed as shown below

```
sudo dpkg -i packages/python-gui-hello-world-1.0-amd64.deb
Selecting previously unselected package python-gui-hello-world.
(Reading database ... 415090 files and directories currently installed.)
Preparing to unpack .../python-gui-hello-world-1.0-amd64.deb ...
Unpacking python-gui-hello-world (1.0) ...
Setting up python-gui-hello-world (1.0) ...
Processing triggers for desktop-file-utils (0.23+linuxmint5) ...
Processing triggers for gnome-menus (3.13.3-11ubuntu1.1) ...
Processing triggers for mime-support (3.60ubuntu1) ...
```

## Running the gui-hello-world command
From the applications menu enter gui-hello-world. This should show the start icon and when selected with a mouse the small Hello World window is displayed.


## Uninstalling the hello-world Program
The debian package is installed as shown below

```
sudo dpkg -r python-gui-hello-world
(Reading database ... 418008 files and directories currently installed.)
Removing python-gui-hello-world (1.0) ...
Processing triggers for desktop-file-utils (0.23+linuxmint5) ...
Processing triggers for gnome-menus (3.13.3-11ubuntu1.1) ...
Processing triggers for mime-support (3.60ubuntu1) ...
```
