#!/usr/bin/env bash
set -euo pipefail

assembler="$(pwd)/scripts/assemble.py"
work="$(mktemp -d)"
trap 'gpgconf --kill gpg-agent; gpgconf --homedir "$work/pacman-gnupg" --kill gpg-agent; rm -rf -- "$work"' EXIT
export GNUPGHOME="$work/gnupg"
install -dm700 "$GNUPGHOME"
gpg --batch --passphrase '' --quick-generate-key 'Test master-archrepo' rsa2048 sign 1d
export ARCH_SIGNING_KEY_FINGERPRINT
ARCH_SIGNING_KEY_FINGERPRINT="$(gpg --batch --with-colons --list-keys | awk -F: '$1 == "fpr" { print $10 }')"
export ARCH_SIGNING_PASSPHRASE=''

cd "$work"
mkdir packages payload cache db root
package='archrepo-test-1.0-1-any.pkg.tar.zst'
cat >payload/.PKGINFO <<'EOF'
pkgname = archrepo-test
pkgbase = archrepo-test
pkgver = 1.0-1
pkgdesc = Paquet de test
size = 0
arch = any
EOF
mkdir -p payload/usr/share/archrepo-test
printf 'test\n' >payload/usr/share/archrepo-test/fixture.txt
bsdtar --zstd -cf "packages/$package" -C payload .PKGINFO usr
read -r sha256 _ < <(sha256sum "packages/$package")
cat >catalogue.json <<EOF
[
  {
    "name": "archrepo-test",
    "repository": "Masternaka/master-archrepo",
    "version": "1.0-1",
    "arch": "any",
    "sha256": "$sha256"
  }
]
EOF
python "$assembler" --local-packages packages
test -z "$(find site -type l)"

pacman-key --gpgdir "$work/pacman-gnupg" --init
pacman-key --gpgdir "$work/pacman-gnupg" --add site/master-archrepo.asc
pacman-key --gpgdir "$work/pacman-gnupg" --lsign-key "$ARCH_SIGNING_KEY_FINGERPRINT"
cat >pacman.conf <<EOF
[options]
Architecture = x86_64
SigLevel = Required TrustedOnly
GPGDir = $work/pacman-gnupg
DBPath = $work/db
CacheDir = $work/cache
LogFile = $work/pacman.log
RootDir = $work/root
[master-archrepo]
Server = file://$work/site/x86_64
EOF
pacman --config pacman.conf -Sy
pacman --config pacman.conf -S --noconfirm master-archrepo/archrepo-test
pacman --config pacman.conf -Q archrepo-test
test -s root/usr/share/archrepo-test/fixture.txt
cmp "packages/$package" "cache/$package"

printf 'altéré\n' >>"packages/$package"
if python "$assembler" --local-packages packages --output site-invalide; then
    echo "Un paquet dont l’empreinte a changé a été accepté." >&2
    exit 1
fi
test ! -e site-invalide
