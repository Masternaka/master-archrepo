# Installer master-archrepo sur CachyOS

## 1. Transférer les fichiers

Copier l’archive d’installation sur CachyOS, l’extraire et ouvrir un terminal dans le dossier `master-archrepo-cachyos`. Elle contient le catalogue, les scripts et les deux paquets dans `paquets/`.

| Application | Version Arch | Construction vérifiée |
| --- | --- | --- |
| SambaPilot | `0.1.0.dev0-7` | [CI et artefacts](https://github.com/Masternaka/Sambapilot/actions/runs/43452582608) |
| DotfilePilot | `0.1.0.dev0-5` | [CI et artefacts](https://github.com/Masternaka/Dotfilepilot/actions/runs/43431439343) |

Pour récupérer les paquets séparément, télécharger les artefacts Arch des exécutions ci-dessus, extraire chaque ZIP dans son propre dossier et exécuter `sha256sum -c SHA256SUMS` dans chacun. Copier les deux fichiers `.pkg.tar.zst` dans `paquets/`. L’assemblage vérifie leurs empreintes et leurs métadonnées contre le catalogue.

## 2. Créer le dépôt local

Exécuter ces commandes comme utilisateur habituel, sauf les lignes commençant par `sudo`. Si Python ou GnuPG manque, installer les outils depuis les dépôts CachyOS avec `sudo pacman -Syu --needed python gnupg`.

```sh
sudo install -d -m 0755 -o "$(id -un)" -g "$(id -gn)" /srv/master-archrepo
export GNUPGHOME="${XDG_DATA_HOME:-$HOME/.local/share}/master-archrepo/gnupg"
install -d -m 0700 "$GNUPGHOME"
gpg --quick-generate-key 'master-archrepo (signature locale)' rsa3072 sign 0
bash scripts/update-local.sh
```

Choisir une phrase secrète quand GnuPG la demande. Créer cette clé une seule fois. La clé privée reste dans le dossier GnuPG sous ton compte. Conserver une sauvegarde privée si tu veux réutiliser le dépôt après une réinstallation de CachyOS.

## 3. Ajouter le dépôt à pacman

La commande suivante affiche l’empreinte de la clé que tu viens de créer. Comparer cette empreinte à celle du fichier public avant de l’importer.

```sh
gpg --list-secret-keys --with-fingerprint
gpg --show-keys --with-fingerprint /srv/master-archrepo/current/master-archrepo.asc
```

Remplacer `EMPREINTE_COMPLETE_VERIFIEE` par la vraie empreinte, sans espaces.

```sh
sudo pacman-key --add /srv/master-archrepo/current/master-archrepo.asc
sudo pacman-key --lsign-key EMPREINTE_COMPLETE_VERIFIEE
sudo cp -a /etc/pacman.conf "/etc/pacman.conf.before-master-archrepo-$(date +%Y%m%d-%H%M%S)"
sudoedit /etc/pacman.conf
```

Ajouter une fois ce bloc à la fin du fichier, après les dépôts système.

```ini
[master-archrepo]
SigLevel = Required TrustedOnly
Server = file:///srv/master-archrepo/current/x86_64
```

```sh
sudo pacman -Syu master-archrepo/sambapilot master-archrepo/dotfilepilot
pacman -Sl master-archrepo
```

Pacman met aussi à jour le système pendant l’installation. Vérifier ensuite les deux lanceurs dans le menu. Pour essayer le déploiement de DotfilePilot, utiliser un dossier cible temporaire et des configurations fictives.

## 4. Ajouter ou mettre à jour tes applications

1. Construire le paquet dans le dépôt source, avec sa recette `PKGBUILD` et `makepkg` lancé comme utilisateur habituel. Copier le fichier `.pkg.tar.zst` dans `paquets/`.
2. Dans `catalogue.json`, ajouter ou actualiser le nom du paquet, son dépôt source, sa version complète `pkgver-pkgrel`, son architecture et son SHA-256 calculé avec `sha256sum`. Pour une mise à jour, vérifier que `vercmp NOUVELLE_VERSION VERSION_INSTALLÉE` renvoie un nombre positif. Garder dans `paquets/` tous les fichiers référencés par le catalogue.
3. Relancer `bash scripts/update-local.sh`, puis `sudo pacman -Syu`. Pour une application ajoutée, demander explicitement son installation avec `sudo pacman -Syu master-archrepo/NOM_DU_PAQUET`.

Chaque assemblage vérifié est conservé dans `/srv/master-archrepo/versions/`. Le lien `current` bascule vers le nouvel assemblage seulement après vérification de la base et des signatures. Garder la même clé et la même section pacman pour les mises à jour. Pour retirer le dépôt, retirer la section `[master-archrepo]` de `/etc/pacman.conf`.

## Références

- [Configuration et signatures pacman](https://man.archlinux.org/man/pacman.conf.5)
- [Gestion du trousseau pacman](https://man.archlinux.org/man/pacman-key.8)
- [Construction de la base pacman](https://man.archlinux.org/man/repo-add.8)
