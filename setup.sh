#!/bin/sh

# Check for Zsh or sh
if [ -x "$(command -v zsh)" ]; then
    # Use Zsh if it is available
    SHELL="zsh"
else
    # Fall back to sh if Zsh is not found
    SHELL="sh"
fi

# Check for required commands
# for cmd in sudo grep read; do
#     if ! [ -x "$(command -v $cmd)" ]; then
#         echo "Error: Required command '$cmd' not found." >&2
#         exit 1
#     fi
# done

# Check for OPENAI_API_KEY environment variable
if [ -z "${OPENAI_API_KEY}" ]; then
    echo 'Warning: OPENAI_API_KEY environment variable not found.' >&2
    read -p 'Please enter your OpenAI API key: ' OPENAI_API_KEY
    export OPENAI_API_KEY
fi

echo $OPENAI_API_KEY

# Check for poetry
if ! [ -x "$(command -v poetry)" ]; then
    echo 'Error: poetry is not installed.' >&2
    echo 'Visit https://python-poetry.org/docs/#installation for instructions on how to install poetry.' >&2
    exit 1
fi

# Set desired Python version (default to 3.11.3 if not specified)
PYTHON_VERSION="${PYTHON_VERSION:-3.11.3}"

# Check for pyenv
if [ -x "$(command -v pyenv)" ]; then
    # Check if desired Python version is installed
    if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
        pyenv install "$PYTHON_VERSION"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install Python $PYTHON_VERSION using pyenv." >&2
            exit 1
        fi
    fi

    # Set local Python version to desired version
    pyenv local "$PYTHON_VERSION"
else
    echo 'Warning: pyenv is not installed. This may cause issues.' >&2
    echo 'Visit https://github.com/pyenv/pyenv#installation for instructions on how to install pyenv.' >&2
fi

python --version

# Install portaudio package on Linux or macOS
if [ -x "$(command -v apt-get)" ]; then
    # Debian/Ubuntu-based systems
    sudo apt-get update && sudo apt-get install portaudio19-dev || {
        echo "Error: Failed to install portaudio using apt-get." >&2;
        exit 1;
    }
elif [ -x "$(command -v dnf)" ]; then
    # Fedora-based systems or systems that support both yum and dnf (dnf preferred) 
    sudo dnf install portaudio-devel || {
        echo "Error: Failed to install portaudio using dnf." >&2;
        exit 1;
    }
elif [ -x "$(command -v yum)" ]; then
    # CentOS/RHEL-based systems 
    sudo yum install portaudio-devel || {
        echo "Error: Failed to install portaudio using yum." >&2;
        exit 1;
    }
elif [ -x "$(command -v pacman)" ]; then
    # Arch Linux-based systems 
    sudo pacman -Syu portaudio || {
        echo "Error: Failed to install portaudio using pacman." >&2;
        exit 1;
    }
elif [ -x "$(command -v brew)" ]; then
    # Homebrew on Linux or macOS
    brew install portaudio || {
        echo "Error: Failed to install portaudio using brew." >&2;
        exit 1;
    }
fi

# Run pip commands within a poetry environment using Zsh or sh as appropriate.
$SHELL <<EOF
poetry install
poetry run pip install wheel setuptools pip --upgrade
poetry run python -m pip install playsound
EOF