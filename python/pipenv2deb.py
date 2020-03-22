#!/usr/bin/env python3

import  os
import  shutil
import  getpass
import  stat
from    optparse import OptionParser
from    subprocess import check_call

class DebBuilderError(Exception):
    pass

class UIO(object):
    """@brief Responsible for user output"""
    def info(self, line):
        """@breif Show an info level message
           @param line The line of text."""
        print( 'INFO:  %s' % (line) )

    def error(self, line):
        """@breif Show an error level message
           @param line The line of text."""
        print( 'ERROR: %s' % (line) )

class DebBuilder(object):
    """@brief Responsible for building debian files using distutils and python-stdeb packages"""

    PIP_FILE                        = "Pipfile"
    DEBIAN_FOLDER                   = "debian"
    BUILD_FOLDER                    = "build"
    INITD_FOLDER                    = "init.d"
    ROOT_FS_FOLDER                  = "root_fs"
    DEBIAN_CONTROL_FILE             = os.path.join(DEBIAN_FOLDER, "control")
    OUTPUT_FOLDER                   = "packages"
    PIPENV2DEB_PY                   = "pipenv2deb.py"
    VENV_FOLDER                     = ".venv"
    TARGET_BIN_FOLDER               = "/usr/local/bin"
    BUILD_DEBIAN_FOLDER             = os.path.join(BUILD_FOLDER, "DEBIAN")
    BUILD_INITD_FOLDER              = os.path.join(BUILD_FOLDER, os.path.join("etc", INITD_FOLDER) )
    BUILD_BIN_FOLDER                = "{}{}".format(BUILD_FOLDER, TARGET_BIN_FOLDER)
    VALID_DEBIAN_FOLDER_FILE_LIST   = ["control", "preinst", "postinst", "prerm", "postrm"]
    EXCLUDE_FOLDER_LIST             = ["debian","packages", "build", ".venv"]

    def __init__(self, uio, options):
        """@brief Constructor
           @param uio A UIO instance
           @param options The command line options instance"""

        self._uio = uio
        self._options = options
        self._packageName = None
        self._version     = None

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
            self._uio.info("Removed %s path" % (localDir) )

        if os.path.isdir(DebBuilder.OUTPUT_FOLDER) and removeOutputFolder:
            shutil.rmtree(DebBuilder.OUTPUT_FOLDER)
            self._uio.info("Removed %s path" % (DebBuilder.OUTPUT_FOLDER) )

    def _checkPipenvInstalled(self):
        """@brief Check pipenv is installed."""
        try:
            check_call(["pipenv","check"])
        except OSError:
            raise DebBuilderError("pipenv not installed. Run 'pip3 install pipenv'")

    def _checkFS(self):
        """@brief Check the required files and folders exist."""

        if not os.path.isfile(DebBuilder.PIP_FILE):
            raise DebBuilderError("%s file not found in local path." % (DebBuilder.PIP_FILE) )

        if not os.path.isfile(DebBuilder.DEBIAN_CONTROL_FILE):
            raise DebBuilderError("%s required file not found." % (DebBuilder.DEBIAN_CONTROL_FILE) )

        #Ensure only valid filenames exist in the debian folder
        entryList = os.listdir(DebBuilder.DEBIAN_FOLDER)
        for entry in entryList:
            if entry not in DebBuilder.VALID_DEBIAN_FOLDER_FILE_LIST:
                raise DebBuilderError("{} is an invalid {} folder file.".format(entry, DebBuilder.VALID_DEBIAN_FOLDER_FILE_LIST))

        self._pythonFiles = self._getPythonFiles()
        if len(self._pythonFiles) == 0:
            raise DebBuilderError("No python files found to install. These should be in the local python folder.")

        #For the .venv folder we just check it exists
        vEnvFolder = os.path.join(os.getcwd(), DebBuilder.VENV_FOLDER)
        if not os.path.isdir(vEnvFolder):
            raise DebBuilderError("{} (virutal environment) folder not found.".format(vEnvFolder))

    def _loadPackageAttr(self):
        """@brief Get the name of the package to be built.
            _getDebianFiles() must have been called previously."""
        packageName=None
        #Existance of DebBuilder.DEBIAN_CONTROL_FILE is checked in _checkFS()
        if os.path.isfile(DebBuilder.DEBIAN_CONTROL_FILE):
            fd = open(DebBuilder.DEBIAN_CONTROL_FILE)
            lines = fd.readlines()
            fd.close()
            for line in lines:
                line=line.strip()
                if line.startswith("Package: "):
                    packageName = line[8:]
                    self._packageName=packageName.strip()
                if line.startswith("Version: "):
                    version = line[8:]
                    self._version=version.strip()

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
            pythonFileList.append(os.path.join(pythonFolder, entry) )

        self._checkPythonFiles(pythonFileList)

        return pythonFileList

    def _checkPythonFiles(self, pythonFileList):
        """@brief Check that we have a valid python files list"""
        #As long as one python file exists thats ok.
        #Note _getPythonFiles() only loads the pythonFileList with files ending
        #*.py
        if len(pythonFileList) == 0:
            raise DebBuilderError("No python files found to install in current folder.")

    def _getFileList(self, folder):
        """@brief Get the debian files."""
        fileList = []
        cwd = os.getcwd()
        folder = os.path.join(cwd, folder)

        if os.path.isdir(folder):
            entryList = os.listdir(folder)

            for entry in entryList:
                fileList.append(os.path.join(folder, entry) )

        return fileList

    def _getPackageFolderList(self):
        """@brief Get a list of the folder that should sit next to the Pipfile and .venv folders when installed.
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

    def _copyFiles(self):
        """@brief Copy Files into the local build area
           @return None"""

        if not os.path.isdir(DebBuilder.OUTPUT_FOLDER):
            os.makedirs(DebBuilder.OUTPUT_FOLDER)
            self._uio.info("Created %s" % (DebBuilder.OUTPUT_FOLDER))

        shutil.copytree(DebBuilder.DEBIAN_FOLDER, DebBuilder.BUILD_DEBIAN_FOLDER)
        self._uio.info("Created %s" % (DebBuilder.BUILD_DEBIAN_FOLDER))
        #It's not nessasary for the control file to be executable but the other
        #script files that maybe present (postinst etc) must be.
        self._setExecutableFiles(DebBuilder.BUILD_DEBIAN_FOLDER)

        packageFolder = self._getPackageFolder()
        if not os.path.isdir(packageFolder):
            os.makedirs(packageFolder)
            self._uio.info("Created %s" % (packageFolder))

        #Copy any folders that are not part of the build system to the dest
        #packaging folder.
        packageFolderList = self._getPackageFolderList()
        for _packageFolder in packageFolderList:
            destFolder = os.path.join(packageFolder, os.path.basename(_packageFolder))
            shutil.copytree(_packageFolder, destFolder)
            self._uio.info("Copied {} to {}".format(_packageFolder, destFolder))

        if os.path.isdir(DebBuilder.INITD_FOLDER):
            shutil.copytree(DebBuilder.INITD_FOLDER, DebBuilder.BUILD_INITD_FOLDER)
            self._uio.info("Copied init.d folder to {}".format(DebBuilder.BUILD_INITD_FOLDER))
            self._setExecutableFiles(DebBuilder.BUILD_INITD_FOLDER)

        destFolder = os.path.join(packageFolder, DebBuilder.VENV_FOLDER)
        shutil.copytree(DebBuilder.VENV_FOLDER, destFolder)
        self._uio.info("Copied virtual environment to {}".format(destFolder))

        #If a local root_fs files exists copy these files and folders include
        #these in the files to be packaged.
        self._rootFSFiles = self._getFileList(DebBuilder.ROOT_FS_FOLDER)
        for rootFSFile in self._rootFSFiles:
            if os.path.isfile(rootFSFile):
                shutil.copy(rootFSFile, DebBuilder.BUILD_FOLDER)
                self._uio.info("Copied %s to %s" % (rootFSFile, DebBuilder.BUILD_FOLDER))
            else:
                destFolder = os.path.join(DebBuilder.BUILD_FOLDER, os.path.basename(rootFSFile))
                shutil.copytree(rootFSFile, destFolder)
                self._uio.info("Copied %s to %s" % (rootFSFile, destFolder))

        #The Pipfile must be present for the pipenv to work
        shutil.copy(DebBuilder.PIP_FILE, packageFolder)
        self._uio.info("Copied %s to %s" % (DebBuilder.PIP_FILE, packageFolder))

        for pythonFile in self._pythonFiles:
            if os.path.isfile(pythonFile):
                shutil.copy(pythonFile, packageFolder)
                self._uio.info("Copied %s to %s" % (pythonFile, packageFolder))

    def _setExecutable(self, exeFile):
        """@brief Set a file as executable.
           @param  exeFile The file to be mde executablke."""
        os.chmod(exeFile, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH )
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
        targetStartupFile=os.path.join(targetPackageFolder, pythonFile)
        fd = open(startupScriptFile, 'w')
        fd.write("#!/bin/sh\n")
        fd.write("export PIPENV_PIPFILE={}\n".format(pipFile))
        fd.write("pipenv run {}\n".format(targetStartupFile))
        fd.close()
        self._uio.info("Created: {}".format(startupScriptFile))
        self._setExecutable(startupScriptFile)

    def _createStartupFiles(self):
        """@brief Create startup files for each of the python files in the current working directory (where pipenv2deb is executed)."""
        for pythonFile in self._pythonFiles:
            self._createStartupFilepythonFile(os.path.basename(pythonFile))

    def _build(self):
        """@brief Build the deb, rpm and tgz packages"""
        debBuildCmd = "dpkg-deb -Zgzip -b %s %s/%s-%s-all.deb" % (DebBuilder.BUILD_FOLDER, DebBuilder.OUTPUT_FOLDER, self._packageName, self._version)
        self._uio.info("Executing: {}".format(debBuildCmd))
        try:
            check_call(debBuildCmd.split())
        except OSError:
            raise DebBuilderError("Failed to build deb file.")

    def run(self):
        """@brief Run the build process."""

        self._ensureRootUser()

        if self._options.clean:

            self._clean(self._options.clean)

        else:
            self._checkPipenvInstalled()
            self._checkFS()
            self._loadPackageAttr()
            self._clean()
            self._copyFiles()
            self._createStartupFiles()
            self._build()

            if not self._options.lbp:
                self._clean()

def main():
    uio = UIO()
    cwd = os.getcwd()
    uio.info("PJA: CWD = {}".format(cwd))
    opts = OptionParser(usage='\nBuild deb Linux install packages from a python pipenv environment.\n\n'
                                'This command must be executed in a folder containing.\n'
                                'Pipfile       The pipenv Pilefile (required).\n'
                                '.venv         The pipenv .venv (virtual environment) folder (required).\n'
                                '<python file> At least one python file wih a main entry point (required).\n'
                                'debian:       A folder containing the debian build files as detailed below (required).\n'
                                '              control:  The debian config file (required).\n'
                                '              preinst:  Script executed before installation (optional).\n'
                                '              postinst: Script executed after installation (optional).\n'
                                '              prerm:    Script executed before removal (optional).\n'
                                '              postrm:   Script executed after removal (optional).\n\n'
                                '- root_fs:    Contains files/folders to be copied into the root of the destination file system (optional).\n'
                                '- init.d:     Contains startup script file/s to be installed into /etc/init.d (optional).\n'
                                '              To auto start these on install the postinst script must install them.\n'
                                '- ******      Any other folder name (optional) that is not in the follwing list will be copied to\n'
                                '              the package folder: {}, {}, {}, {}\n\n'
                                'The output *.deb package file is placed in the local {} folder.\n'.format(DebBuilder.EXCLUDE_FOLDER_LIST[0],
                                                                                                                       DebBuilder.EXCLUDE_FOLDER_LIST[1],
                                                                                                                       DebBuilder.EXCLUDE_FOLDER_LIST[2],
                                                                                                                       DebBuilder.EXCLUDE_FOLDER_LIST[3],
                                                                                                                       DebBuilder.OUTPUT_FOLDER)
                        )
    opts.add_option("--debug", help="Enable debugging.", action="store_true", default=False)
    opts.add_option("--clean", help="Remove the %s folder." % (DebBuilder.OUTPUT_FOLDER), action="store_true", default=False)
    opts.add_option("--lbp",   help="Leave build path. A debugging option to allow the 'build' folder to be examined after the build has completed. This 'build' folder is normally removed when the build is complete.", action="store_true", default=False)

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
            uio.error( str(ex) )

if __name__ == '__main__':
    main()
