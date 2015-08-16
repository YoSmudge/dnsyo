#! /bin/bash -e

# Update the resolver list

WORKING_DIR=$(mktemp -d)
UPDATE_SUMMARY=$(mktemp)
RUN_THREADS=500

cd "${WORKING_DIR}"

git init .
git remote add origin git@github.com:samarudge/dnsyo.git
git fetch
git checkout master

virtualenv ENV/
ENV/bin/python setup.py install

ENV/bin/dnsyo --update --threads="${RUN_THREADS}" --resolverfile=./resolver-list-source.yml --updateSummary="${UPDATE_SUMMARY}" --updateDestination=./resolver-list.yml

EMAIL_TARGET="sam@codesam.co.uk"
EMAIL_SUBJECT="[DNSYO] $(head -n 1 ${UPDATE_SUMMARY})"

cat "${UPDATE_SUMMARY}" | mail -s "${EMAIL_SUBJECT}" "${EMAIL_TARGET}"

git commit -a --author="DNSYO List Updater <dnsyo@$(hostname -f)>" -F "${UPDATE_SUMMARY}"
git push origin master