#!/bin/sh

echo "The pypi server must be running before running this."
export PIPENV_VENV_IN_PROJECT=enabled
pipenv install