#!/usr/bin/env bash
# bootstrap.sh: customize python-chrisapp-template with project details

# ========================================
# CONFIGURATION
# ========================================

# Step 1. Change these values to your liking.

PLUGIN_NAME="$(basename $(dirname $(realpath $0)))"
PLUGIN_TITLE='My ChRIS Plugin'
SCRIPT_NAME='commandname'
DESCRIPTION='A ChRIS plugin to do something awesome'
ORGANIZATION='FNNDSC'
EMAIL='dev@babyMRI.org'

# automatic testing, building, and release
# https://github.com/FNNDSC/cookiecutter-chrisapp/wiki/Automatic-Builds
ENABLE_CI=yes

# Step 2. Uncomment the line below.

#READY=yes

# Step 3. Run: ./bootstrap.sh

if ! [ "$READY" = 'yes' ]; then
  >&2 echo "error: you are not READY."
  exit 1
fi

cd $(dirname "$0")


# ========================================
# VALIDATE INPUT
# ========================================

function contains_invalid_characters () {
  [[ "$1" = *"/"* ]]
}

# given a variable name, exit if the variable's value contains invalid characters.
function check_variable_value_valid () {
  local varname="$1"
  local varvalue="${!varname}"
  if contains_invalid_characters "$varvalue"; then
    >&2 echo "error: invalid characters in $varname=$varvalue"
    exit 1
  fi
}

# may not contain '/'
check_variable_value_valid PLUGIN_NAME
check_variable_value_valid SCRIPT_NAME
check_variable_value_valid ORGANIZATION
check_variable_value_valid EMAIL


# ========================================
# COMMIT THE USER-SET CONFIG
# ========================================

# print command to run before running it
function verb () {
  set -x
  "$@"
  { set +x; } 2> /dev/null
}

# fail on error
set -e
set -o pipefail

verb git commit -m 'Configure python-chrisapp-template/bootstrap.sh' -- "$0"


# ========================================
# REPLACE VALUES
# ========================================

# execute sed on all files in project, excluding hidden paths and venv/
function replace_in_all () {
  if [ -z "$2" ]; then
    return
  fi
  find . -type f \
    -not -path '*/\.*/*' -not -path '*/\venv/*' -not -name 'bootstrap.sh' \
    -exec sed -i -e "s/$1/$2/g" '{}' \;
}

replace_in_all commandname "$SCRIPT_NAME"
replace_in_all pl-appname "$PLUGIN_NAME"
replace_in_all 'dev@babyMRI.org' "$EMAIL"
replace_in_all FNNDSC "$ORGANIZATION"

# .github/
sed -i -e '/CI disabled by default, delete this line/d' .github/workflows/ci.yml

# replace "/" with "\/" in string
function escape_slashes () {
  sed 's/\//\\&/g' <<< "$@"
}

escaped_description="$(escape_slashes "$DESCRIPTION")"
escaped_title="$(escape_slashes "$PLUGIN_TITLE")"

# README.md
temp_file=$(mktemp)
sed -e'/^# ChRIS Plugin Title$/'\{ -e:1 -en\;b1 -e\} -ed README.md \
  | sed "s/^# ChRIS Plugin Title\$/# $escaped_title/" \
  | sed '/^END README TEMPLATE -->$/d' \
  | sed "s/fnndsc/${ORGANIZATION,,}/g" \
  | sed "s/app\\.py/$SCRIPT_NAME.py/g" \
  > $temp_file
mv $temp_file README.md

# Dockerfile
sed "s#WORKDIR /usr/local/src/app#WORKDIR /usr/local/src/$PLUGIN_NAME#" Dockerfile \
  | sed "s/org\.opencontainers\.image\.title=\"ChRIS Plugin Title\"/org.opencontainers.image.title=\"$escaped_title\"/" \
  | sed "s/org\.opencontainers\.image\.description=\"A ChRIS plugin that\.\.\.\"/org.opencontainers.image.description=\"$escaped_description\"/" \
  > $temp_file
mv $temp_file Dockerfile

# setup.py

function guess_https_url () {
  local origin="$(git remote get-url origin)"
  local https_url="$origin"
  if [[ "$https_url" = "git@"* ]]; then
    # convert SSH url to HTTPS url by
    # 1. change last ':' to '/'
    # 2. replace leading 'git@' with 'https://'
    https_url="$(
      echo "$https_url" \
        | sed 's#\(.*\):#\1/#' \
        | sed 's#^git@#https://#'
    )"
  fi
  echo "${https_url:0:-4}"  # remove trailing ".git"
}

appname_without_prefix="$(sed -E 's/(pl|dbg|ep)-//' <<< "$PLUGIN_NAME")"
sed "s/name='.*'/name='$appname_without_prefix'/" setup.py \
  | sed "s/description='.*'/description='$escaped_description'/" \
  | sed "s/py_modules=\['app'\]/py_modules=['$SCRIPT_NAME']/" \
  | sed "s/app:main/$SCRIPT_NAME:main/" \
  | sed "s#url='.*'#url='$(guess_https_url)'#" \
  > $temp_file
mv $temp_file setup.py

# app.py

# FIGlet over HTTPS, since it's probably not installed locally
function figlet_wrapper () {
  curl -fsSG 'https://figlet.moc.chrisproject.org/' --data-urlencode "message=$*" \
    | grep -v '^[[:space:]]*$'
}

function inject_figleted_title () {
  python << EOF
for line in open('app.py'):
    if line == 'ChRIS Plugin Template Title\n':
        print(r"""$1""")
    else:
        print(line, end='')
EOF
}

figleted_title="$(figlet_wrapper "$PLUGIN_NAME")"
echo "$figleted_title"
inject_figleted_title "$figleted_title" \
  | sed "s/title='My ChRIS plugin'/title='$escaped_title'/" \
  | sed "s/description='cli description'/description='$escaped_description'/" \
  > "$SCRIPT_NAME.py"
rm app.py


# ========================================
# SETUP
# ========================================

if ! [ -e venv ]; then
  verb python -m venv venv
fi

>&2 echo + source venv/bin/activate
source venv/bin/activate
verb pip install -r requirements.txt
verb pip install -e .
verb pip install pytest

tput bold
>&2 printf '\n%s\n\n' '✨Done!✨'
tput sgr0

tput setaf 3
>&2 echo 'To undo these actions and start over, run:'
>&2 printf '\n\t%s\n\t%s\n\t%s\n\t%s\n\n' \
    'git reset --hard' \
    'git clean -df' \
    'rm -rf venv *.egg-info' \
    "git reset 'HEAD^'"
tput setaf 6
>&2 echo 'Activate the Python virtual environment by running:'
>&2 printf '\n\t%s\n\n' 'source venv/bin/activate'
>&2 echo 'Save these changes by running:'
>&2 printf '\n\t%s\n\n' 'git add -A && git commit -m "Run bootstrap.sh"'
tput setaf 2
echo 'For more information on how to get started, see README.md'
tput sgr0

verb rm -v "$0"

# Note to self: consider rewriting this in Python?
