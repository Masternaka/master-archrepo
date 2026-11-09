# master-archrepo

Dépôt personnel Arch Linux destiné à installer et mettre à jour les applications de **Masternaka** sur Omarchy avec pacman.

Chaque application conserve son dépôt de code et sa chaîne de construction. `master-archrepo` centralisera les paquets sélectionnés, leurs signatures et la base de données utilisée par pacman.

## État actuel

Le dépôt contient la documentation de préparation. **Il n’est pas encore un dépôt pacman utilisable** : les scripts de collecte, la génération de la base, la signature et le workflow de publication restent à développer. Aucun réglage GitHub, déploiement Pages ou accès depuis Omarchy n’a été validé dans cette revue locale du 9 novembre 2026.

SambaPilot dispose, dans son propre dépôt, d’une préparation de construction de paquet Arch via GitHub Actions. Une première construction réussie reste à confirmer. Ces artefacts temporaires ne constituent pas encore une publication dans `master-archrepo`.

## Marche à suivre

Le [guide de préparation et d’activation](docs/preparation-et-activation.md) décrit :

1. Les fichiers et mécanismes à développer avant activation.
2. La clé de signature et les réglages GitHub à préparer.
3. La première publication et les contrôles nécessaires.
4. L’ajout du dépôt sur Omarchy, l’installation et les mises à jour.
5. L’ajout d’autres applications et le retrait du dépôt.

La configuration prévue sur Omarchy utilisera la section `[master-archrepo]`. Une fois le dépôt réellement publié et sa clé vérifiée, le parcours cible sera :

```sh
sudo pacman -Syu master-archrepo/sambapilot
sudo pacman -Syu
```

Ces commandes sont des exemples pour une installation future. La seconde met à jour tout le système, y compris les applications personnelles installées. Aucun script de cette documentation n’est exécuté automatiquement, et aucune installation ou modification de machine n’a été réalisée.
