#!/usr/bin/env sh
# Check Python version and create a virtual environment
# ./install.sh <TARGET_DIR>

TARGET_DIR="${1}"
BUILD_ENV=false
# https://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
SCRIPT_PATH="$( cd "$(dirname $0)" ; pwd -P )"

function exit_with_error {
    echo "${1}"
    exit 1
}

function check_version {
    # Validate the provided Python path's version
    # Requires path to python executable to validate
    # version follows format: "Python 3.6.0"
    PY_VERSION=`${PYTHON_PATH} -V | cut -d' ' -f2`
    # probably a better way to do this parsing, but whatever
    PY_MAJOR=`echo ${PY_VERSION} | cut -d'.' -f1`
    PY_MINOR=`echo ${PY_VERSION} | cut -d'.' -f2`

    if [ ${PY_MAJOR} -eq "3" ] && [ ${PY_MINOR} -ge "6" ]
    then
        echo "${PYTHON_PATH} version verified. Building virtual environment"
        BUILD_ENV=true
    else
        exit_with_error "${PYTHON_PATH} version must be at least 3.6.0 to complete installation"
    fi
}

function build_venv {
    # Build a virtual environment with the necessary packages with the provided Python path
    # Requires path to python executable to validate
    ENV_PATH="${TARGET_DIR}/env"
    echo "Building virtual environment in ${ENV_PATH}"
    last_error=`${PYTHON_PATH} -m venv ${ENV_PATH} 2>&1`
    ENV_PYTHON="${ENV_PATH}/bin/python"
    ENV_PIP="${ENV_PATH}/bin/pip"
    if [ -x ${ENV_PYTHON} ]
    then
        echo "Virtual environment creation successful"
        echo "Using ${ENV_PIP} to install yarals package and dependencies"
        ${ENV_PIP} install wheel --disable-pip-version-check
        ${ENV_PIP} wheel "${SCRIPT_PATH}/../server" --disable-pip-version-check --no-deps --wheel-dir "${ENV_PATH}"
        WHEEL=`find ${ENV_PATH}/yarals-*.whl`
        ${ENV_PIP} install ${WHEEL} --disable-pip-version-check
    else
        echo "Virtual environment creation failed. ${last_error}"
    fi
}

PYTHON_PATH=`which python3` || exit_with_error "Couldn't find python3. Please check if it's installed"
echo "Found python3. Checking version..."
check_version
if [ $BUILD_ENV ]
then
    build_venv
fi
