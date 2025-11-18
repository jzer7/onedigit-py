#!/bin/sh

set -e

# ----------------------------------------------------------
# post-create.sh
# ----------------------------------------------------------
# To work effectively, uv needs the package cache and the
# virtual environment to be on the same filesystem. (So it
# can use hard links.)
#
# This script is run once after the container is created.
# It prepares the development environment:
# - Sets up uv cache in a volume
# - Sets up a virtual environment in the same volume, with
#   a name that won't collide with other projects or while
#   doing local development.
# - Installs packages from uv.lock
# ----------------------------------------------------------

# ----------------------------------------------------------
# Configuration
# ----------------------------------------------------------
USERNAME="vscode"
VOLUME="/python"
PROJ_NAME="$(basename $PWD)"
VENV_DIR="$VOLUME/venvs/$PROJ_NAME"
VENV_LINK_NAME=".venv-container"

# ----------------------------------------------------------
# Utility functions
# ----------------------------------------------------------


error() {
  echo "[ERROR] $* (line:${BASH_LINENO[0]})" 1>&2
}

die() {
  echo "[FATAL] $* (line:${BASH_LINENO[0]})" 1>&2
  exit 1 # failure
}

# Remove a sym link (not file or directory), verify nothing is left
remove_sym_link() {
  SYMLINK="$1"

  if [ -L "$SYMLINK" ]; then
    rm -f "$SYMLINK"
  fi
  if [ -e "$SYMLINK" ]; then
    return 1 # failure
  fi
}

# Create sym link, or change target of a sym link
update_or_create_sym_link() {
  SRC="$1"
  SYMLINK="$2"

  if ! remove_sym_link "$SYMLINK" ; then
    error "update_or_create_sym_link $SRC $SYMLINK (removing SYMLINK)"
    ls -lad "$SRC"
    ls -lad "$SYMLINK"
    return 1 # failure
  fi

  ln -s "$SRC" "$SYMLINK"
  if [ ! -L "$SYMLINK" ]; then
    error "update_or_create_sym_link $SRC $SYMLINK (linking)"
    return 1 # failure
  fi
}

# Remove whatever is there, and force a sym link
force_sym_link() {
  SRC="$1"
  SYMLINK="$2"

  rm -rf "$SYMLINK"

  if ! update_or_create_sym_link "$SRC" "$SYMLINK" ; then
    error "force_sym_link $SRC $SYMLINK"
    return 1 # failure
  fi
}

# ----------------------------------------------------------
# Prepare system
# ----------------------------------------------------------

# 1. uv shell completions
uv generate-shell-completion bash | sudo tee /usr/share/bash-completion/completions/uv > /dev/null

# 2. Prepare cache and venv directories in the volume
sudo chown "$USERNAME" "$VOLUME"
mkdir -p "$VOLUME/cache/uv"
mkdir -p "$VENV_DIR"

# 3. Enable the cache
force_sym_link "$VOLUME/cache/uv" "$HOME/.cache/uv" || die "Could not change uv cache"

# 4. Enable the venv
update_or_create_sym_link "$VENV_DIR" "$VENV_LINK_NAME" || die "Could not create sym link for \"$VENV_LINK_NAME\."

export UV_PROJECT_ENVIRONMENT="$VENV_DIR"
echo "export UV_PROJECT_ENVIRONMENT=$VENV_DIR" >> "$HOME/.profile"

## Build the environment, if it doesn't exist
uv venv --allow-existing "$VENV_DIR"

# 5. Install packages, without chaning the lockfile
if [ -e uv.lock ]; then
  uv sync --locked
  uv sync --locked --all-groups
fi
