#! /bin/bash

# Update the resolver list
export WORKING_DIR=$(mktemp -d)
TARGET_FILE="$1"

"$(readlink -f "$(dirname $0)/helpers/tmpRepo.sh")"

# Get info about the last commit to the resolver _source_ file
LAST_COMMIT_ID=$(git log -n 1 --pretty=format:%H -- ./resolver-list-source.yml)
LAST_COMMIT_BY=$(git log -n 1 --pretty="format:%an <%ae>" -- ./resolver-list-source.yml)
LAST_COMMIT_DATE=$(git log -n 1 --pretty="format:%aD" -- ./resolver-list-source.yml)

cat > "${TARGET_FILE}" <<FILEHEADER
# DNSYO List File
# Last updated ${LAST_COMMIT_DATE} by ${LAST_COMMIT_BY}
# (From hash ${LAST_COMMIT_ID})

# Downloaded $(date)

FILEHEADER

cat "./resolver-list.yml" >> "${TARGET_FILE}"

cd
rm -Rf "${WORKING_DIR}"