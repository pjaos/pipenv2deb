# Build Linux deb installers from a pipenv program.
Allows Linux deb installers to be built from python applications that use pipenv.


## Installing pipenv2deb
To install pipenv2deb run the following command on a debian based (E.G Ubuntu,
  Debian etc) Linux computer.

```
sudo pip3 install pipenv2deb
```

## Using pipenv2deb
To use the pipenv2deb tool run the 'sudo python3 -m pipenv2deb' command in a folder containing the following.

 - Pipfile This defines the environment that you program or programs will execute in.
   (See https://realpython.com/what-is-pip/ for more information on pip).
 - debian:     A folder containing the debian build files as detailed below (required).
```
               control:  The debian config file (required).
               preinst:  Script executed before installation (optional).
               postinst: Script executed after installation (optional).
               prerm:    Script executed before removal (optional).
               postrm:   Script executed after removal (optional).
```

 See https://www.debian.org/doc/manuals/debian-faq/pkg-basics.en.html for more information on these files.

 Other folders are optional

   - root-fs:    Contains files/folders to be copied into the root of the destination file
               system.

   - init.d:     Contains startup script file/s to be installed into /etc/init.d (optional).
               To auto start these on install the postinst script must start the service.

   Any other folder name (optional) that is not debian, packages, build or .venv
   is copied to the package folder unless an exclude_folder_list.txt file exists.
   If this file exists then each line should detail folder that is to be excluded.

   Folders that are installed will typically be python modules that are required
   by your application.

 Finally there should be at least one python file with a main entry point (required).

## Examples
The https://github.com/pjaos/pipenv2deb/tree/master/examples folder provides examples of how to use pipenv2deb.


## Command line help
Run the 'sudo python3 -m pipenv2deb -h' command (once pipenv2deb is installed) for command line help as shown below.


```
Build deb Linux install packages from a python pipenv environment.

This command must be executed in a folder containing.
Pipfile       The pipenv Pilefile (required).
<python file> At least one python file with a main entry point (required).
debian:       A folder containing the debian build files as detailed below (required).
              control:  The debian config file (required).
              preinst:  Script executed before installation (optional).
              postinst: Script executed after installation (optional).
              prerm:    Script executed before removal (optional).
              postrm:   Script executed after removal (optional).

 root-fs:    Contains files/folders to be copied into the root of the destination file
              system (optional).
 init.d:     Contains startup script file/s to be installed into /etc/init.d (optional).
              To auto start these on install the postinst script must start the service.

              Any other folder name (optional) that is not debian, packages, build
              or .venv is copied to the package folder unless
              a exclude_folder_list.txt file exists. If this file exists then each line should
              detail folder that is to be excluded. This folder list is in addition to those detailed above.

              Folders that are installed will typically be python modules that are required
              by your application.

The output *.deb package file is placed in the local packages folder.

Options:
  -h, --help  show this help message and exit
  --debug     Enable debugging.
  --venv      Include the .venv folder from the output deb file. This
              increases the size output deb file but ensures the virtual
              environment is copied rather than rebuilt on the target machine.
  --clean     Remove the packages output folder containing the deb installer
              files.
  --lbp       Leave build path. A debugging option to allow the 'build' folder
              to be examined after the build has completed. This 'build'
              folder is normally removed when the build is complete.
  --rpm       Produce an RPM installer as well as the debian installer.
  --tgz       Produce a TGZ installer as well as the debian installer.
  --check     Perform a 'pipenv check' before building the installer.
  --venv_oip  If this option is used the .venv folder is not placed in the
              install path. The default is for the .venv foldler to be placed
              in the install path under /usr/local/bin/<app folder name>. If
              this option is used then the default pipenv location is used
              which is typically under ~/.local/share/virtualenvs
```
