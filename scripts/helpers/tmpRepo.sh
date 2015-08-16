#! /bin/bash

cd "${WORKING_DIR}"

git init .
git remote add origin git@github.com:samarudge/dnsyo.git
git fetch
git checkout master

virtualenv ENV/
ENV/bin/python setup.py install