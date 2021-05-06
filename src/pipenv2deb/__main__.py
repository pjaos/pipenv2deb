#!/usr/bin/env python3

import os
import shutil
import getpass
import stat
from optparse import OptionParser
from subprocess import check_call

class DebBuilderError(Exception):
    pass


class UIO(object):
    """@brief Responsible for user output"""

    def info(self, line):
        """@breif Show an info level message
           @param line The line of text."""
        print('INFO:  %s' % (line))

    def error(self, line):
        """@breif Show an error level message
           @param line The line of text."""
        print('ERROR: %s' % (line))


class DebBuilder(object):
    """@brief Responsible for building debian files using distutils and python-stdeb packages"""

    PIP_FILE = "Pipfile"
    PIP_LOCK_FILE = "Pipfile.lock"
    DEBIAN_FOLDER = "debian"
    BUILD_FOLDER = "build"
    INITD_FOLDER = "init.d"
    ROOT_FS_FOLDER = "root-fs"
    GIT_FOLDER = ".git"
    PYCACHE_FOLDER = "__pycache__"
    DEBIAN_CONTROL_FILE = os.path.join(DEBIAN_FOLDER, "control")
    DEBIAN_POST_INST_FILE = os.path.join(DEBIAN_FOLDER, "postinst")
    CREATE_PIPENV_FILENAME = "create_pip_env.sh"
    OUTPUT_FOLDER = "packages"
    PIPENV2DEB_PY = "pipenv2deb.py"
    VENV_FOLDER = ".venv"
    TARGET_BIN_FOLDER = "/usr/local/bin"
    DEBIAN_POST_INST_FILE = os.path.join(DEBIAN_FOLDER, "postinst")
    BUILD_DEBIAN_FOLDER = os.path.join(BUILD_FOLDER, "DEBIAN")
    BUILD_INITD_FOLDER = os.path.join(BUILD_FOLDER, os.path.join("etc", INITD_FOLDER))
    BUILD_BIN_FOLDER = "{}{}".format(BUILD_FOLDER, TARGET_BIN_FOLDER)
    VALID_DEBIAN_FOLDER_FILE_LIST = ["control", "preinst", "postinst", "prerm", "postrm"]
    USER_EXCLUDE_LIST = "exclude_folder_list.txt"
    EXCLUDE_FOLDER_LIST = [DEBIAN_FOLDER, OUTPUT_FOLDER, BUILD_FOLDER, VENV_FOLDER, ROOT_FS_FOLDER, GIT_FOLDER, PYCACHE_FOLDER]
    BUILD_POST_INST_FILE = os.path.join(BUILD_DEBIAN_FOLDER, "postinst")

    def __init__(self, uio, options):
        """@brief Constructor
           @param uio A UIO instance
           @param options The command line options instance"""

        self._uio = uio
        self._options = options
        self._packageName = None
        self._version = None

    def _ensureRootUser(self):
        """@brief Ensure this script is run as root """

        username = getpass.getuser()
        if username != 'root':
            raise DebBuilderError("Please run build.py as root using sudo.")

    def _clean(self, removeOutputFolder=False):
        """@brief Clean up files
           @param removePackagesFolder If True then remove the packages folder."""

        localDir = DebBuilder.BUILD_FOLDER
        if os.path.isdir(localDir):
            shutil.rmtree(localDir)
            self._uio.info("Removed %s path" % (localDir))

        if os.path.isdir(DebBuilder.OUTPUT_FOLDER) and removeOutputFolder:
            shutil.rmtree(DebBuilder.OUTPUT_FOLDER)
            self._uio.info("Removed %s path" % (DebBuilder.OUTPUT_FOLDER))

    def _checkPipenvInstalled(self):
        """@brief Check pipenv is installed."""
        try:
            check_call(["pipenv", "check"])
        except OSError:
            raise DebBuilderError("pipenv not installed. Run 'pip3 install pipenv'")

    def _checkFS(self):
        """@brief Check the required files and folders exist."""

        if not os.path.isfile(DebBuilder.PIP_FILE):
            raise DebBuilderError("%s file not found in local path." % (DebBuilder.PIP_FILE))

        if not os.path.isfile(DebBuilder.DEBIAN_CONTROL_FILE):
            raise DebBuilderError("%s required file not found." % (DebBuilder.DEBIAN_CONTROL_FILE))

        # Ensure only valid filenames exist in the debian folder
        entryList = os.listdir(DebBuilder.DEBIAN_FOLDER)
        for entry in entryList:
            if entry not in DebBuilder.VALID_DEBIAN_FOLDER_FILE_LIST:
                raise DebBuilderError(
                    "{} is an invalid {} folder file.".format(entry, DebBuilder.VALID_DEBIAN_FOLDER_FILE_LIST))

        self._pythonFiles = self._getPythonFiles()
        if len(self._pythonFiles) == 0:
            raise DebBuilderError("No python files found to install. These should be in the local python folder.")

    def _loadPackageAttr(self):
        """@brief Get the name of the package to be built.
            _getDebianFiles() must have been called previously."""
        packageName = None
        # Existance of DebBuilder.DEBIAN_CONTROL_FILE is checked in _checkFS()
        if os.path.isfile(DebBuilder.DEBIAN_CONTROL_FILE):
            fd = open(DebBuilder.DEBIAN_CONTROL_FILE)
            lines = fd.readlines()
            fd.close()
            for line in lines:
                line = line.strip()
                if line.startswith("Package: "):
                    packageName = line[8:]
                    self._packageName = packageName.strip()
                if line.startswith("Version: "):
                    version = line[8:]
                    self._version = version.strip()
                if line.startswith("Architecture: "):
                    version = line[13:]
                    self._architecture = version.strip()

    def _getPythonFiles(self):
        """@brief Get the python files that are to be installed.
                  The python files should be in the folder where pipenv2deb is executed."""
        pythonFolder = os.getcwd()
        entryList = os.listdir(pythonFolder)
        pythonFileList = []
        for entry in entryList:
            if entry == DebBuilder.PIPENV2DEB_PY:
                continue
            if not entry.endswith(".py"):
                continue
            pythonFileList.append(os.path.join(pythonFolder, entry))

        self._checkPythonFiles(pythonFileList)

        return pythonFileList

    def _checkPythonFiles(self, pythonFileList):
        """@brief Check that we have a valid python files list"""
        # As long as one python file exists thats ok.
        # Note _getPythonFiles() only loads the pythonFileList with files ending
        # *.py
        if len(pythonFileList) == 0:
            raise DebBuilderError("No python files found to install in current folder.")

    def _getPackageFolderList(self):
        """@brief Get a list of the folders that should sit next to the Pipfile and .venv folders when installed.
                  These folders will be installed next to the top level python command files and so maybe python
                  modules that are imported, or may contain any other files type."""
        folderList = []
        cwd = os.getcwd()
        if os.path.isdir(cwd):
            entryList = os.listdir(cwd)
            for entry in entryList:
                _entry = os.path.join(cwd, entry)
                if os.path.isdir(_entry) and entry not in DebBuilder.EXCLUDE_FOLDER_LIST:
                    folderList.append(_entry)

        return folderList

    def _getPackageFolder(self):
        """@brief Get the package folder. This is the location that the virtual env is installed."""
        return os.path.join(DebBuilder.BUILD_BIN_FOLDER, "{}.pipenvpkg".format(self._packageName))

    def _getTargetPackageFolder(self):
        """@brief Get the package folder when installed.
           @return The package folder."""
        return os.path.join(DebBuilder.TARGET_BIN_FOLDER, "{}.pipenvpkg".format(self._packageName))

    def _createLocalRebuildPipenvScript(self):
        """@brief Create a script to rebuild the pipenv in the local folder.
                  This can be useful during development but is not used in the deb file.
           @return None"""
        createPipEnvFile = os.path.join(DebBuilder.CREATE_PIPENV_FILENAME)
        fd = open(createPipEnvFile, 'w')
        fd.write("#!/bin/sh\n")
        fd.write("export PIPENV_VENV_IN_PROJECT=enabled\n")
        fd.write("pipenv --three install\n")
        fd.close()
        self._setExecutable(createPipEnvFile)

    def _createTargetRebuildPipenvScript(self, packageFolder):
        """@brief Create a script to rebuild the pipenv in the installed fileset.
           @param packageFolder The target package folder.
           @return None"""
        createPipEnvFile = os.path.join(packageFolder, DebBuilder.CREATE_PIPENV_FILENAME)
        targetPackageFolder = self._getTargetPackageFolder()
        fd = open(createPipEnvFile, 'w')
        fd.write("#!/bin/sh\n")
        fd.write("cd {}\n".format(targetPackageFolder))
        #If the user does not want the .venv folder outside the install path
        if not self._options.venv_oip:
            fd.write("export PIPENV_VENV_IN_PROJECT=enabled\n")
        fd.write("pipenv --three install\n")
        fd.close()
        self._setExecutable(createPipEnvFile)

    def _copyFiles(self):
        """@brief Copy Files into the local build area
           @return None"""
        self._createLocalRebuildPipenvScript()

        # If the .venv folder is to be included in the output deb file
        if self._options.venv:
            # For the .venv folder we just check it exists
            vEnvFolder = os.path.join(os.getcwd(), DebBuilder.VENV_FOLDER)
            if not os.path.isdir(vEnvFolder):
                raise DebBuilderError("{} (virtual environment) folder not found.".format(vEnvFolder))

        if not os.path.isdir(DebBuilder.OUTPUT_FOLDER):
            os.makedirs(DebBuilder.OUTPUT_FOLDER)
            self._uio.info("Created %s" % (DebBuilder.OUTPUT_FOLDER))

        # If a local root-fs files exists copy these files and folders include
        # these in the files to be packaged.
        if os.path.isdir(DebBuilder.ROOT_FS_FOLDER):
            srcFolder = DebBuilder.ROOT_FS_FOLDER
            destFolder = DebBuilder.BUILD_FOLDER
            shutil.copytree(srcFolder, destFolder)
            self._uio.info("Copied %s to %s" % (srcFolder, destFolder))

        shutil.copytree(DebBuilder.DEBIAN_FOLDER, DebBuilder.BUILD_DEBIAN_FOLDER)
        self._uio.info("Created %s" % (DebBuilder.BUILD_DEBIAN_FOLDER))

        packageFolder = self._getPackageFolder()
        if not os.path.isdir(packageFolder):
            os.makedirs(packageFolder)
            self._uio.info("Created %s" % (packageFolder))

        # Copy any folders that are not part of the build system to the dest
        # packaging folder.
        packageFolderList = self._getPackageFolderList()
        for _packageFolder in packageFolderList:
            destFolder = os.path.join(packageFolder, os.path.basename(_packageFolder))
            shutil.copytree(_packageFolder, destFolder)
            self._uio.info("Copied {} to {}".format(_packageFolder, destFolder))

        if os.path.isdir(DebBuilder.INITD_FOLDER):
            shutil.copytree(DebBuilder.INITD_FOLDER, DebBuilder.BUILD_INITD_FOLDER)
            self._uio.info("Copied init.d folder to {}".format(DebBuilder.BUILD_INITD_FOLDER))
            self._setExecutableFiles(DebBuilder.BUILD_INITD_FOLDER)

        # The Pipfile must be present for the pipenv to work
        shutil.copy(DebBuilder.PIP_FILE, packageFolder)
        self._uio.info("Copied %s to %s" % (DebBuilder.PIP_FILE, packageFolder))
        shutil.copy(DebBuilder.PIP_LOCK_FILE, packageFolder)
        self._uio.info("Copied %s to %s" % (DebBuilder.PIP_LOCK_FILE, packageFolder))

        self._createTargetRebuildPipenvScript(packageFolder)

        for pythonFile in self._pythonFiles:
            if os.path.isfile(pythonFile):
                shutil.copy(pythonFile, packageFolder)
                self._uio.info("Copied %s to %s" % (pythonFile, packageFolder))

        # If the .venv folder is not to be included in the output deb file
        if self._options.venv:
            # Copy the .venv folder to the build folder
            destFolder = os.path.join(packageFolder, DebBuilder.VENV_FOLDER)
            shutil.copytree(DebBuilder.VENV_FOLDER, destFolder)
            self._uio.info("Copied virtual environment to {}".format(destFolder))
        else:
            self._updatePostInstallScript()

        # It's not nessasary for the control file to be executable but the other
        # script files that maybe present (postinst etc) must be.
        self._setExecutableFiles(DebBuilder.BUILD_DEBIAN_FOLDER)

    def _setExecutable(self, exeFile):
        """@brief Set a file as executable.
           @param  exeFile The file to be mde executablke."""
        os.chmod(exeFile, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        self._uio.info("Set executable attribute: {}".format(exeFile))

    def _setExecutableFiles(self, folder):
        """@brief Set all files in a foilder as executable."""
        entryList = os.listdir(folder)
        for entry in entryList:
            _file = os.path.join(folder, entry)
            self._setExecutable(_file)

    def _createStartupFilepythonFile(self, pythonFile):
        """@brief Create a startup file for the python file.
           @param pythonFile The python file to startup."""
        startupScriptFilename = pythonFile.replace(".py", "")
        startupScriptFile = os.path.join(DebBuilder.BUILD_BIN_FOLDER, startupScriptFilename)
        targetPackageFolder = self._getTargetPackageFolder()
        pipFile = os.path.join(targetPackageFolder, DebBuilder.PIP_FILE)
        targetStartupFile = os.path.join(targetPackageFolder, pythonFile)
        fd = open(startupScriptFile, 'w')
        fd.write("#!/bin/sh\n")
        #Run the command providing the location of the Pipfile
        fd.write("PIPENV_PIPFILE={} pipenv run {} $@\n".format(pipFile, targetStartupFile))

        fd.close()
        self._uio.info("Created: {}".format(startupScriptFile))
        self._setExecutable(startupScriptFile)

    def _createStartupFiles(self):
        """@brief Create startup files for each of the python files in the current working directory (where pipenv2deb is executed)."""
        for pythonFile in self._pythonFiles:
            self._createStartupFilepythonFile(os.path.basename(pythonFile))

    def _updatePostInstallScript(self):
        """@brief Ensure that the .venv folder is built when the package is installed."""
        self._uio.info("Creating %s" % (DebBuilder.BUILD_POST_INST_FILE))
        if os.path.isfile(DebBuilder.BUILD_POST_INST_FILE):
            fd = open(DebBuilder.BUILD_POST_INST_FILE, 'r')
            lines = fd.readlines()
            fd.close()
            if len(lines) > 0:
                if not lines[0].startswith("#!"):
                    # Note the DebBuilder.BUILD_POST_INST_FILE file is copied to DebBuilder.DEBIAN_POST_INST_FILE
                    raise Exception(
                        "The first line in the {} file must start with #!".format(DebBuilder.DEBIAN_POST_INST_FILE))
            else:
                lines.append("#!/bin/sh\n")

        else:
            lines = []
            lines.append("#!/bin/sh\n")

        targetPackageFolder = self._getTargetPackageFolder()
        #If the user wants the .venv folder outside the install path
        if self._options.venv_oip:
            orgUser = os.environ['SUDO_USER']
            if orgUser and len(orgUser) > 0:
                #We need to create the virtual env as non root user so that the out of install path
                #virtual environment folder is created with and ownership of the install user.
                #This folder will typically be under ~/.local/share/virtualenvs
                postInstCmd = 'cd {} && /usr/bin/sudo -u {} pipenv install\n'.format(targetPackageFolder, orgUser)

            else:
                raise Exception("Install failed: SUDO_USER environmental variable not found.")

        else:
            postInstCmd = "cd {} && ./{}\n".format(targetPackageFolder, DebBuilder.CREATE_PIPENV_FILENAME)

        # We insert the post install command at the start of the script file so that if
        # a postinst file used any commands are shown at the end of the installation process.
        lines.insert(1, postInstCmd)

        fd = open(DebBuilder.BUILD_POST_INST_FILE, 'w')
        for line in lines:
            fd.write(line)
        fd.close()
        self._setExecutable(DebBuilder.BUILD_POST_INST_FILE)

    def _getDebFilename(self):
        """@brief Get the name of the deb output file."""
        return '{}-{}-{}.deb'.format(self._packageName, self._version, self._architecture)

    def _build(self):
        """@brief Build the deb, rpm and tgz packages"""
        debFile = self._getDebFilename()
        debBuildCmd = "dpkg-deb -Zgzip -b {} {}".format(DebBuilder.BUILD_FOLDER,
                                                        os.path.join(DebBuilder.OUTPUT_FOLDER, debFile))
        self._uio.info("Executing: {}".format(debBuildCmd))
        try:
            check_call(debBuildCmd.split())
        except OSError:
            raise DebBuilderError("Failed to build deb file.")

    def _createPackagesFromDeb(self):
        """@brief Create other packages from the deb file which must be built prior to calling this method."""
        debFile = self._getDebFilename()
        debPackage = os.path.join(DebBuilder.OUTPUT_FOLDER, debFile)
        if os.path.isfile(debPackage):
            cwd = os.getcwd()

            if self._options.rpm:
                os.chdir(DebBuilder.OUTPUT_FOLDER)
                buildCmd = "sudo alien --to-rpm --scripts %s" % (debFile)
                self._uio.info("Executing: {}".format(buildCmd))
                try:
                    check_call(buildCmd.split())
                except OSError:
                    raise DebBuilderError("Failed to build rpm from deb file.")
                self._uio.info("Created rpm file from deb")

            if self._options.tgz:
                buildCmd = "sudo alien --to-tgz --scripts %s" % (debFile)
                self._uio.info("Executing: {}".format(buildCmd))
                try:
                    check_call(buildCmd.split())
                except OSError:
                    raise DebBuilderError("Failed to build tgz from deb file.")
                self._uio.info("Created tgz file from deb")

            os.chdir(cwd)

    def _addExcludedFolders(self):
        """@brief Add to the list of excluded folders"""
        if os.path.isfile(DebBuilder.USER_EXCLUDE_LIST):
            fd = open(DebBuilder.USER_EXCLUDE_LIST)
            lines = fd.readlines()
            fd.close()
            for line in lines:
                line=line.rstrip("\r\n")
                #Add top the list of folders to be excluded
                DebBuilder.EXCLUDE_FOLDER_LIST.append(line)

    def run(self):
        """@brief Run the build process."""

        self._ensureRootUser()

        if self._options.clean:

            self._clean(True)

        else:
            self._addExcludedFolders()
            if self._options.check:
                self._checkPipenvInstalled()
            self._checkFS()
            self._loadPackageAttr()
            self._clean(False)
            self._copyFiles()
            self._createStartupFiles()
            self._build()
            if self._options.rpm or self._options.tgz:
                self._createPackagesFromDeb()

            if not self._options.lbp:
                self._clean(False)


def main():
    uio = UIO()

    opts = OptionParser(usage='usage: %prog [options]\n'
                              '\nBuild deb Linux install packages from a python pipenv environment.\n\n'
                              'This command must be executed in a folder containing.\n'
                              'Pipfile       The pipenv Pilefile (required).\n'
                              '<python file> At least one python file with a main entry point (required).\n'
                              'debian:       A folder containing the debian build files as detailed below (required).\n'
                              '              control:  The debian config file (required).\n'
                              '              preinst:  Script executed before installation (optional).\n'
                              '              postinst: Script executed after installation (optional).\n'
                              '              prerm:    Script executed before removal (optional).\n'
                              '              postrm:   Script executed after removal (optional).\n\n'
                              ' root-fs:    Contains files/folders to be copied into the root of the destination file\n'
                              '              system (optional).\n'
                              ' init.d:     Contains startup script file/s to be installed into /etc/init.d (optional).\n'
                              '              To auto start these on install the postinst script must start the service.\n'
                              '\n'
                              '              Any other folder name (optional) that is not {}, {}, {}\n'
                              '              or {} is copied to the package folder unless\n'
                              '              an {} file exists. If this file exists then each line should\n'
                              '              detail folder that is to be excluded. This folder list is in addition to those detailed above.\n'
                              '\n'
                              '              Folders that are installed will typically be python modules that are required\n'
                              '              by your application.\n\n'
                              'The output *.deb package file is placed in the local {} folder.'.format(
        DebBuilder.EXCLUDE_FOLDER_LIST[0],
        DebBuilder.EXCLUDE_FOLDER_LIST[1],
        DebBuilder.EXCLUDE_FOLDER_LIST[2],
        DebBuilder.EXCLUDE_FOLDER_LIST[3],
        DebBuilder.USER_EXCLUDE_LIST,
        DebBuilder.OUTPUT_FOLDER)

                        )
    opts.add_option("--debug", help="Enable debugging.", action="store_true", default=False)
    opts.add_option("--venv",
                    help="Include the .venv folder from the output deb file. This increases the size output deb file but ensures the virtual environment is copied rather than rebuilt on the target machine.",
                    action="store_true", default=False)
    opts.add_option("--clean", help="Remove the %s output folder containing the deb installer files." % (DebBuilder.OUTPUT_FOLDER), action="store_true",
                    default=False)
    opts.add_option("--lbp",
                    help="Leave build path. A debugging option to allow the 'build' folder to be examined after the build has completed. This 'build' folder is normally removed when the build is complete.",
                    action="store_true", default=False)
    opts.add_option("--rpm", help="Produce an RPM installer as well as the debian installer.", action="store_true",
                    default=False)
    opts.add_option("--tgz", help="Produce a TGZ installer as well as the debian installer.", action="store_true",
                    default=False)
    opts.add_option("--check", help="Perform a 'pipenv check' before building the installer.", action="store_true", default=False)
    opts.add_option("--venv_oip", help="If this option is used the .venv folder is not placed in the install path. The default is for the .venv foldler to be placed in the install path under /usr/local/bin/<app folder name>. If this option is used then the default pipenv location is used which is typically under ~/.local/share/virtualenvs", action="store_true", default=False)

    try:
        (options, args) = opts.parse_args()

        debBuilder = DebBuilder(uio, options)
        debBuilder.run()

    # If the program throws a system exit exception
    except SystemExit:
        pass
    # Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        if options.debug:
            raise

        else:
            uio.error(str(ex))


if __name__ == '__main__':
    main()
