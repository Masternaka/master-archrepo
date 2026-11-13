"""Conserver les paquets de l’index précédent pendant une transition Pages."""

from pathlib import Path
import shutil
import sys

from assemble import read_catalogue


previous, site = map(Path, sys.argv[1:])
catalogue = previous / "catalogue.json"
if catalogue.is_file():
    for entry in read_catalogue(catalogue):
        filename = "{name}-{version}-{arch}.pkg.tar.zst".format(**entry)
        target = site / "x86_64" / filename
        if not target.exists():
            for name in (filename, filename + ".sig"):
                shutil.copyfile(previous / "x86_64" / name, site / "x86_64" / name)
