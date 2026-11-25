# Mettre master-archrepo en service sur CachyOS

Le dépôt GitHub reste public. Le workflow de publication est sur `main` depuis le [commit `7fe81d8`](https://github.com/Masternaka/master-archrepo/commit/7fe81d894f225ec571bd86a9c12ba194b9813737). La dernière vérification HTTP confirmée le 13 novembre 2026 a renvoyé une 404 pour la clé publique, la base pacman et sa signature. La première publication et l’installation sur CachyOS restent à valider.

## 1. Préparer SambaPilot et DotfilePilot

- [ ] Confirmer le choix de garder les droits sur le code, sans licence open source pour l’instant. C’est une option compatible avec la publication de tes propres paquets. Vérifier les droits de redistribution sur les fichiers de tiers effectivement inclus dans les paquets, notamment les icônes et tout code repris.
- [ ] Si tu retiens ce choix, actualiser les mentions de licence dans les deux projets et dans le [guide de publication](publication-github.md), qui présente actuellement le choix d’une licence comme un préalable. Si tu préfères accorder des droits de réutilisation sous MIT, ajouter le texte de licence dans les projets et l’inclure dans leurs paquets. [Licences sur GitHub](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [ ] Pousser les changements retenus sur `main` des deux projets. Vérifier que le dernier workflow `ci.yml` réussi provient d’un push sur `main` et fournit encore un artefact Arch pour chaque application. Le workflow de publication récupère automatiquement ces artefacts. [Actions SambaPilot](https://github.com/Masternaka/Sambapilot/actions) · [Actions DotfilePilot](https://github.com/Masternaka/Dotfilepilot/actions)

## 2. Configurer et publier le dépôt

- [ ] Créer un jeton GitHub à permissions fines limité à `Sambapilot` et `Dotfilepilot`, avec la permission **Actions → Read-only**. Enregistrer le jeton dans le dépôt `master-archrepo` sous le secret `ARCH_CI_READ_TOKEN`. [Créer le jeton](https://github.com/settings/personal-access-tokens/new) · [Secrets Actions](https://github.com/Masternaka/master-archrepo/settings/secrets/actions)
- [ ] Créer ou réutiliser une clé OpenPGP dédiée. Conserver une sauvegarde privée et noter son empreinte primaire complète. Enregistrer l’export privé ASCII armuré sous `ARCH_SIGNING_PRIVATE_KEY` et, si la clé est protégée, sa phrase secrète sous `ARCH_SIGNING_PASSPHRASE`. Saisir ces valeurs directement dans les secrets GitHub.
- [ ] Dans **Settings → Pages → Build and deployment**, choisir **GitHub Actions**. [Réglages Pages](https://github.com/Masternaka/master-archrepo/settings/pages) · [Documentation GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [ ] Ajouter en dernier la variable Actions `ARCH_SIGNING_KEY_FINGERPRINT`, avec l’empreinte primaire en majuscules et sans espaces. Sa présence active le workflow planifié.
- [ ] Lancer **Publier les paquets Arch** sur `main`. Vérifier que la collecte, la signature et le déploiement réussissent. Confirmer que Pages sert la clé publique, la base et sa signature, et que les deux paquets du catalogue sont accessibles. [Workflow](https://github.com/Masternaka/master-archrepo/actions/workflows/publication.yml) · [Clé publique](https://masternaka.github.io/master-archrepo/master-archrepo.asc) · [Base](https://masternaka.github.io/master-archrepo/x86_64/master-archrepo.db) · [Signature](https://masternaka.github.io/master-archrepo/x86_64/master-archrepo.db.sig)

## 3. Installer et vérifier sur CachyOS

- [ ] Transférer le script d’installation sur CachyOS. Dans la copie locale du projet `CachyOS` vérifiée le 13 novembre 2026, il se trouve à la racine sous le nom `10 - install-master-archrepo.sh` et il n’est pas encore suivi par Git.
- [ ] Après le premier déploiement, exécuter les commandes depuis le dossier `CachyOS`. Remplacer `EMPREINTE_VERIFIEE` par l’empreinte notée lors de la création de la clé. Si un ancien bloc local `[master-archrepo]` existe, sauvegarder la configuration et retirer ce bloc avant de relancer le script.

```bash
sudo bash "10 - install-master-archrepo.sh" EMPREINTE_VERIFIEE
sudo pacman -Syu master-archrepo/sambapilot master-archrepo/dotfilepilot
pacman -Q sambapilot dotfilepilot
```

- [ ] Lancer les deux applications depuis le menu de CachyOS. Pour essayer DotfilePilot, utiliser des configurations fictives dans un dossier cible temporaire.
- [ ] Noter les versions installées. Pousser une modification sur `main` d’une application et attendre la réussite de sa CI, puis **une exécution planifiée** réussie de `master-archrepo`. Le workflow vérifie les builds deux fois par heure, avec des délais possibles côté GitHub.
- [ ] Exécuter `sudo pacman -Syu` et vérifier avec `pacman -Q` que la nouvelle version s’installe. Répéter pour l’autre application pour confirmer que les deux projets alimentent le dépôt.
