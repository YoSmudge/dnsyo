#! /bin/bash

# Generate documentation to target directory

TARGET="$1"

if [ ! -d "${TARGET}" ]; then
  echo "Target directory ${TARGET} does not exist!" >&2
  exit 1
fi

WORKING_DIRECTORY=$(readlink -f "$(dirname $0)/../")

echo "Working in ${WORKING_DIRECTORY} and generating to ${TARGET}..."

echo "Setting up virtualenv for docco and epydoc..."

VENV_PATH="${TARGET}/ENV"
virtualenv "${VENV_PATH}"

"${VENV_PATH}/bin/pip" install pycco epydoc
"${VENV_PATH}/bin/pip" install -r "${WORKING_DIRECTORY}/requirements.txt"

# Generate both epydoc and docco

for TYPE in $(echo "epydoc docco"); do
  echo "Generating ${TYPE} documentation..."
  
  OUTPUT="${TARGET}/${TYPE}"
  mkdir "${OUTPUT}"
  
  if [ "${TYPE}" == "docco" ]; then
    "${VENV_PATH}/bin/pycco" "${WORKING_DIRECTORY}/dnsyo/"*.py -d "${OUTPUT}/"
  elif [ "${TYPE}" == "epydoc" ]; then
    "${VENV_PATH}/bin/epydoc" -v --config="${WORKING_DIRECTORY}/epydoc.ini" -o "${OUTPUT}/"
  fi
done

chmod +x "${TARGET}"
rm -Rf "${VENV_PATH}"