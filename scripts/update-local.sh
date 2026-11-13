#!/usr/bin/env bash
set -euo pipefail
umask 022

project="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
packages="${1:-$project/paquets}"
repository="${2:-/srv/master-archrepo}"
export GNUPGHOME="${GNUPGHOME:-${XDG_DATA_HOME:-$HOME/.local/share}/master-archrepo/gnupg}"
if [[ ! -d "$GNUPGHOME" ]]; then
    printf 'Créer la clé de signature dans %s avant de continuer.\n' "$GNUPGHOME" >&2
    exit 1
fi

if [[ -t 0 ]]; then
    export GPG_TTY
    GPG_TTY="$(tty)"
fi

if [[ -z "${ARCH_SIGNING_KEY_FINGERPRINT:-}" ]]; then
    key="$(gpg --batch --with-colons --list-secret-keys)"
    ARCH_SIGNING_KEY_FINGERPRINT="$(awk -F: '
        $1 == "fpr" && previous == "sec" { print $10 }
        { previous = $1 }
    ' <<<"$key")"
fi
if [[ ! "$ARCH_SIGNING_KEY_FINGERPRINT" =~ ^([A-F0-9]{40}|[A-F0-9]{64})$ ]]; then
    printf 'Choisir une clé unique ou fournir son empreinte dans ARCH_SIGNING_KEY_FINGERPRINT.\n' >&2
    exit 1
fi
export ARCH_SIGNING_KEY_FINGERPRINT

mkdir -p -- "$repository/versions"
exec 9>"$repository/.lock"
flock 9
generation="$(mktemp -d "$repository/versions/depot.XXXXXXXX")"
trap 'rm -rf -- "$generation"' EXIT
python3 "$project/scripts/assemble.py" --catalogue "$project/catalogue.json" \
    --local-packages "$packages" --output "$generation/site"
chmod 755 "$generation"
ln -s -- "versions/${generation##*/}/site" "$generation/current"
mv -Tf -- "$generation/current" "$repository/current"
trap - EXIT

printf 'Dépôt prêt : %s/current/x86_64\n' "$repository"
