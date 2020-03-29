#!/usr/bin/env python3

#This shows how libs that can't be installed using pip3
#may be included in the package.
from non_pip_python_libs import getHelloWorld

def main():
    msg = getHelloWorld()
    print(msg)

if __name__ == '__main__':
    main()

