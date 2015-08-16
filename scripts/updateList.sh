#! /bin/bash -e

# Update the resolver list
export WORKING_DIR=$(mktemp -d)
UPDATE_SUMMARY=$(mktemp)
RUN_THREADS=500

"$(readlink -f "$(dirname $0)/helpers/tmpRepo.sh")"

ENV/bin/dnsyo --update --threads="${RUN_THREADS}" --resolverfile=./resolver-list-source.yml --updateSummary="${UPDATE_SUMMARY}" --updateDestination=./resolver-list.yml

EMAIL_TARGET="sam@codesam.co.uk"
EMAIL_SUBJECT="[DNSYO] $(head -n 1 ${UPDATE_SUMMARY})"

cat "${UPDATE_SUMMARY}" | mail -s "${EMAIL_SUBJECT}" "${EMAIL_TARGET}"

git commit -a --author="DNSYO List Updater <dnsyo@$(hostname -f)>" -F "${UPDATE_SUMMARY}"
git push origin master

cd
rm -Rf "${WORKING_DIR}"