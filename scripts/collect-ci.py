"""Sélectionner les derniers paquets Arch issus de la CI GitHub."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from zipfile import ZipFile

from assemble import read_catalogue


def api(token, path):
    return subprocess.check_output(
        ["gh", "api", path], env={**os.environ, "GH_TOKEN": token}
    )


def latest_package(token, entry, previous, packages):
    repo, name = entry["repository"], entry["name"]
    runs = json.loads(api(token, f"repos/{repo}/actions/workflows/ci.yml/runs?"
                         "branch=main&event=push&status=success&per_page=1"))["workflow_runs"]
    if not runs:
        raise ValueError(f"Aucune CI réussie sur main pour {repo}.")
    run = runs[0]
    commit, attempt = run["head_sha"], run["run_attempt"]
    if previous and previous.get("commit") == commit and previous.get("attempt") == attempt:
        return previous
    artifacts = json.loads(api(token, f"repos/{repo}/actions/runs/{run['id']}/artifacts?"
                               f"name={name}-arch-{commit}-{attempt}"))["artifacts"]
    if len(artifacts) != 1 or artifacts[0]["expired"]:
        raise ValueError(f"Artefact Arch indisponible pour {repo}, exécution {run['id']}.")
    artifact = artifacts[0]
    data = api(token, f"repos/{repo}/actions/artifacts/{artifact['id']}/zip")
    if artifact["digest"] != "sha256:" + hashlib.sha256(data).hexdigest():
        raise ValueError(f"Empreinte de l’artefact incorrecte pour {repo}.")
    with ZipFile(io.BytesIO(data)) as archive:
        if archive.read("COMMIT.txt").decode().strip() != commit:
            raise ValueError(f"Le paquet de {repo} provient d’un autre commit.")
        pattern = re.compile(
            rf"{re.escape(name)}-([A-Za-z0-9][A-Za-z0-9._+]*-[0-9]+(?:\.[0-9]+)?)"
            rf"-{re.escape(entry['arch'])}\.pkg\.tar\.zst"
        )
        filenames = [filename for filename in archive.namelist() if pattern.fullmatch(filename)]
        if len(filenames) != 1:
            raise ValueError(f"Paquet Arch manquant ou ambigu dans l’artefact de {repo}.")
        filename = filenames[0]
        version = pattern.fullmatch(filename).group(1)
        contents = archive.read(filename)
        digest = hashlib.sha256(contents).hexdigest()
        if f"{digest}  {filename}" not in archive.read("SHA256SUMS").decode().splitlines():
            raise ValueError(f"Empreinte du paquet incorrecte pour {repo}.")
    if previous:
        order = int(subprocess.check_output(["vercmp", version, previous["version"]]))
        if order < 0 or (order == 0 and digest != previous["sha256"]):
            raise ValueError(f"{repo} doit augmenter pkgver ou pkgrel avant publication.")
    (packages / filename).write_bytes(contents)
    return {**entry, "version": version, "sha256": digest,
            "commit": commit, "attempt": attempt}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("previous", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    token = os.environ["ARCH_CI_READ_TOKEN"]
    previous = {}
    if (args.previous / "catalogue.json").is_file():
        previous = {entry["name"]: entry for entry in read_catalogue(args.previous / "catalogue.json")}
    with tempfile.TemporaryDirectory(dir=args.destination.parent) as stage:
        root = Path(stage) / "collecte"
        packages = root / "paquets"
        packages.mkdir(parents=True)
        entries = []
        for entry in read_catalogue(args.catalogue):
            old = previous.get(entry["name"])
            if old and old["repository"] != entry["repository"]:
                raise ValueError(f"Le dépôt source a changé pour {entry['name']}.")
            if old:
                filename = "{name}-{version}-{arch}.pkg.tar.zst".format(**old)
                shutil.copyfile(args.previous / "x86_64" / filename, packages / filename)
            entries.append(latest_package(token, entry, old, packages))
        (root / "catalogue.json").write_text(json.dumps(entries, indent=2) + "\n")
        root.rename(args.destination)


if __name__ == "__main__":
    main()
