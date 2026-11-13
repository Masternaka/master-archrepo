"""Assembler un dépôt pacman signé à partir des paquets épinglés."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def read_catalogue(path):
    entries = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries:
        raise ValueError("Le catalogue doit contenir au moins un paquet.")
    names = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Entrée du catalogue invalide.")
        for field, pattern in {
            "name": r"[a-z0-9][a-z0-9@._+-]*",
            "repository": r"Masternaka/[A-Za-z0-9_-][A-Za-z0-9_.-]*",
            "version": r"[A-Za-z0-9][A-Za-z0-9._+]*-[0-9]+(?:\.[0-9]+)?",
            "arch": r"any|x86_64",
            "sha256": r"[a-f0-9]{64}",
        }.items():
            value = entry.get(field)
            if not isinstance(value, str) or not re.fullmatch(pattern, value):
                raise ValueError(f"Champ du catalogue invalide : {field}")
        if entry["name"] in names:
            raise ValueError(f"Paquet en double : {entry['name']}")
        names.add(entry["name"])
    return entries


def collect(entry, directory, local_packages):
    name, version, arch = (entry[key] for key in ("name", "version", "arch"))
    path = directory / f"{name}-{version}-{arch}.pkg.tar.zst"
    shutil.copyfile(local_packages / path.name, path)
    digest = hashlib.sha256()
    with path.open("rb") as package:
        for chunk in iter(lambda: package.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != entry["sha256"]:
        raise ValueError(f"Empreinte incorrecte : {path.name}")
    info = subprocess.check_output(["bsdtar", "-xOf", path, ".PKGINFO"], text=True)
    for key, expected in {"pkgname": name, "pkgver": version, "arch": arch}.items():
        values = [line.partition(" = ")[2] for line in info.splitlines()
                  if line.startswith(f"{key} = ")]
        if values != [expected]:
            raise ValueError(f"Métadonnée {key} incorrecte : {path.name}")
    return path


def assemble(entries, site, local_packages, fingerprint, passphrase):
    if not re.fullmatch(r"[A-F0-9]{40}|[A-F0-9]{64}", fingerprint):
        raise ValueError("Indiquer l’empreinte complète de la clé primaire.")
    if site.exists() or site.is_symlink():
        raise ValueError(f"Le dossier de sortie existe déjà : {site}")
    site = site.absolute()
    with tempfile.TemporaryDirectory(prefix=".archrepo-", dir=site.parent) as stage:
        root = Path(stage) / "site"
        packages_dir = root / "x86_64"
        packages_dir.mkdir(parents=True)
        packages = [collect(entry, packages_dir, local_packages) for entry in entries]

        gpg = ["gpg", "--batch", "--no-tty"]
        key = subprocess.check_output(
            gpg + ["--with-colons", "--list-secret-keys", fingerprint], text=True
        ).splitlines()
        primary_fingerprints = [
            line.split(":")[9] for previous, line in zip(key, key[1:])
            if previous.startswith("sec:") and line.startswith("fpr:")
        ]
        if primary_fingerprints != [fingerprint]:
            raise ValueError("La clé privée ne correspond pas à l’empreinte primaire.")

        with (root / "master-archrepo.asc").open("wb") as public_key:
            subprocess.run(gpg + ["--armor", "--export", fingerprint], stdout=public_key, check=True)
        if not (root / "master-archrepo.asc").stat().st_size:
            raise ValueError("Clé publique vide.")

        def sign(path):
            command = ["gpg", "--local-user", fingerprint, "--no-armor", "--detach-sign", path]
            if passphrase is None:
                subprocess.run(command, check=True)
            else:
                subprocess.run(
                    gpg + ["--pinentry-mode", "loopback", "--passphrase-fd", "0", *command[1:]],
                    input=passphrase + "\n", text=True, check=True,
                )

        for package in packages:
            sign(package)
        database = packages_dir / "master-archrepo.db.tar.gz"
        subprocess.run(["repo-add", "--include-sigs", database, *packages], check=True)
        for suffix in ("db", "files"):
            alias = packages_dir / f"master-archrepo.{suffix}"
            (packages_dir / f"master-archrepo.{suffix}.tar.gz").replace(alias)
            sign(alias)

        verify_home = Path(stage) / "verify"
        verify_home.mkdir(mode=0o700)
        keyring = verify_home / "trustedkeys.gpg"
        subprocess.run(gpg + ["--homedir", verify_home, "--no-autostart",
                              "--output", keyring, "--dearmor", root / "master-archrepo.asc"],
                       check=True)
        for path in [*packages, packages_dir / "master-archrepo.db",
                     packages_dir / "master-archrepo.files"]:
            subprocess.run(["gpgv", "--homedir", verify_home, "--keyring", keyring,
                            f"{path}.sig", path], check=True)

        root.rename(site)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=Path("catalogue.json"))
    parser.add_argument("--local-packages", type=Path,
                        help="Dossier contenant les fichiers .pkg.tar.zst.")
    parser.add_argument("--output", type=Path, default=Path("site"))
    parser.add_argument("--validate-catalogue", action="store_true")
    args = parser.parse_args()
    try:
        entries = read_catalogue(args.catalogue)
        if not args.validate_catalogue:
            if args.local_packages is None:
                parser.error("--local-packages est requis pour assembler le dépôt.")
            assemble(entries, args.output, args.local_packages,
                     os.environ.get("ARCH_SIGNING_KEY_FINGERPRINT", ""),
                     os.environ.pop("ARCH_SIGNING_PASSPHRASE", None))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Assemblage impossible : {error}\n")


if __name__ == "__main__":
    main()
