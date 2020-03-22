# Build Linux deb installers from a pipenv program.

This includes support for

- Debian preinst, posinst, prerm and postrm files.
- Installing startup scripts into the /etc/init.d folder.
- Installing python modules next to the destination .venv folder.
- Installing files and folders in any location below /.

The command line help for the program (pipenv2deb -h) is shown below.

```
Build deb Linux install packages from a python pipenv environment.

This command must be executed in a folder containing.
Pipfile       The pipenv Pilefile (required).
.venv         The pipenv .venv (virtual environment) folder (required).
<python file> At least one python file wih a main entry point (required).
debian:       A folder containing the debian build files as detailed below (required).
              control:  The debian config file (required).
              preinst:  Script executed before installation (optional).
              postinst: Script executed after installation (optional).
              prerm:    Script executed before removal (optional).
              postrm:   Script executed after removal (optional).

- root_fs:    Contains files/folders to be copied into the root of the destination file system (optional).
- init.d:     Contains startup script file/s to be installed into /etc/init.d (optional).
              To auto start these on install the postinst script must install them.
- ******      Any other folder name (optional) that is not in the follwing list will be copied to
              the package folder: debian, packages, build, .venv

The output *.deb package file is placed in the local packages folder.


Options:
  -h, --help  show this help message and exit
  --debug     Enable debugging.
  --clean     Remove the packages folder.
  --lbp       Leave build path. A debugging option to allow the 'build' folder
              to be examined after the build has completed. This 'build'
              folder is normally removed when the build is complete.

```

## Building the pipenv2deb debian file

To build a deb installer file for this package ensure p3build is installed
and enter 'sudo p3build'. This will create the *.deb file in the packages
folder.
