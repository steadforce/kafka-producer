#!/usr/bin/env bash

deactivate_venv() {
  echo "Deactivating virtual env ..."
  deactivate
}

if [ -z "${VIRTUAL_ENV}" ]; then
  if [ ! -d venv ]; then
    echo "No venv detected, e.g. create one ..."
    python3 -m venv venv
  fi
  echo "Did not detect an active virtual env - activating ..."
  . venv/bin/activate
fi

pip install -U pip wheel setuptools pip-tools
if [ -e requirements.in ]; then
  #  create requirements.txt file from dependency spec requirements.in
  pip-compile --output-file requirements.txt requirements.in
  #	sync dependencies (remove obsolete and install missing)
  pip-sync requirements.txt

  deactivate_venv
  exit 0
else
  echo "No requirements.in found! Exiting ..."
  deactivate_venv
  exit 1
fi
