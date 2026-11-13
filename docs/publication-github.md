# Publier master-archrepo sur GitHub Pages

Après un push sur `main` dans SambaPilot ou DotfilePilot, la CI teste et construit le paquet Arch. Le workflow **Publier les paquets Arch** consulte deux fois par heure les exécutions réussies, collecte les artefacts correspondants, vérifie les empreintes, signe les paquets et déploie la base sur GitHub Pages. Les exécutions planifiées peuvent être retardées par GitHub. Un push dont les tests échouent laisse la version publiée disponible.

## Activer la publication

1. Confirmer la licence de chaque application destinée à la distribution publique. Les recettes actuelles de SambaPilot et DotfilePilot indiquent qu’il reste à la définir. Une fois ce choix appliqué aux projets, laisser leur CI construire les paquets qui seront distribués.
2. Créer un jeton GitHub à permissions fines pour les dépôts SambaPilot et DotfilePilot, avec **Actions → Read-only**. Le déposer dans les secrets Actions de `Masternaka/master-archrepo` sous `ARCH_CI_READ_TOKEN`. Il permet de télécharger les archives produites par les autres dépôts.
3. Créer ou réutiliser une clé OpenPGP dédiée à ce dépôt. Dans **Settings → Secrets and variables → Actions**, ajouter l’export privé ASCII armuré sous `ARCH_SIGNING_PRIVATE_KEY`, la phrase secrète sous `ARCH_SIGNING_PASSPHRASE` et, en dernier, l’empreinte primaire complète en majuscules sous la variable `ARCH_SIGNING_KEY_FINGERPRINT`. Conserver l’empreinte et une sauvegarde privée de la clé hors de Git.
4. Dans **Settings → Pages → Build and deployment**, sélectionner **GitHub Actions** comme source. Lancer **Publier les paquets Arch** sur `main` pour la première publication. Le premier lancement nécessite un artefact Arch disponible pour chaque application. La branche `paquets` conserve les fichiers signés et le dernier catalogue publié pour les exécutions suivantes.
5. Vérifier que GitHub Pages sert la base et sa signature avant l’installation sur CachyOS.

## Installer sur CachyOS

```sh
curl -fL -o master-archrepo.asc https://masternaka.github.io/master-archrepo/master-archrepo.asc
gpg --show-keys --with-fingerprint master-archrepo.asc
```

Comparer l’empreinte à la valeur enregistrée lors de la création de la clé. Remplacer `EMPREINTE_VERIFIEE` par cette valeur, puis importer et approuver la clé dans pacman.

```sh
sudo pacman-key --add master-archrepo.asc
sudo pacman-key --lsign-key EMPREINTE_VERIFIEE
sudoedit /etc/pacman.conf
```

Ajouter le bloc à la fin de `/etc/pacman.conf`, après les dépôts système. Si la section existe déjà, modifier sa ligne `Server`.

```ini
[master-archrepo]
SigLevel = Required TrustedOnly
Server = https://masternaka.github.io/master-archrepo/x86_64
```

```sh
sudo pacman -Syu master-archrepo/sambapilot master-archrepo/dotfilepilot
```

Les prochaines versions installées seront mises à jour lors de `sudo pacman -Syu`.

## Ajouter une autre application

Préparer un workflow `ci.yml` qui se termine par un artefact `NOM-arch-COMMIT-TENTATIVE` contenant un paquet `.pkg.tar.zst`, son empreinte dans `SHA256SUMS` et le commit dans `COMMIT.txt`. Ajouter l’application à `catalogue.json` et étendre l’accès du jeton à son dépôt. Les deux applications actuelles utilisent déjà le numéro d’exécution GitHub comme `pkgrel`.

- [Déploiement GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [API GitHub des artefacts Actions](https://docs.github.com/en/rest/actions/artifacts)
- [Configuration de pacman](https://man.archlinux.org/man/pacman.conf.5)
