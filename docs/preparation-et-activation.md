# Préparer et activer master-archrepo sur Omarchy

## État de départ

Le dépôt cible est `Masternaka/master-archrepo`. Son rôle sera de distribuer les paquets des applications personnelles de Masternaka, avec leurs signatures et une base pacman.

Au 9 novembre 2026, le dépôt local examiné ne contient aucun script ni workflow de publication. Les réglages GitHub, la clé, l’hébergement et l’ordinateur Omarchy ne sont pas inspectés. **Le dépôt n’est donc pas déclaré prêt à installer.**

Les commandes ci-dessous constituent une procédure future. Elles ne sont pas exécutées lors de la rédaction. Toute création de clé, installation d’outil ou modification de la machine doit être effectuée dans un environnement choisi et explicitement autorisé.

## 1. Développer la chaîne de publication

Avant de pouvoir activer le dépôt, il faut ajouter les composants suivants :

| Composant à créer | Comportement attendu |
| --- | --- |
| Catalogue des applications | Dépôt GitHub d’origine, nom du paquet, version, architecture, source exacte et empreinte SHA-256. |
| Collecte des paquets | Récupérer uniquement les versions retenues ; vérifier provenance, empreinte et métadonnées Arch. |
| Signature | Signer les paquets et la base avec la clé dédiée, sans exposer la clé privée ou sa phrase secrète. |
| Construction de la base | Utiliser `repo-add` pour produire `master-archrepo.db` et les métadonnées associées. |
| Préparation des fichiers publiés | Réunir paquets, signatures, base et clé publique ; vérifier leur cohérence avant publication. |
| Tests | Refuser les sources inconnues, les paquets incomplets, les signatures invalides, les doublons et les retours de version involontaires. |
| Workflow GitHub | Tester à chaque changement et publier seulement depuis la branche retenue, avec une activation explicite. |

Le catalogue ne doit pas pointer durablement vers des artefacts Actions qui expirent. Pour une version distribuée, conserver le paquet dans une source durable et identifiable, par exemple un asset de release de l’application, puis le copier dans les fichiers publiés du dépôt pacman.

Le workflow de chaque application construit son paquet. Le workflow de `master-archrepo` sélectionne, vérifie, signe et publie les versions retenues. Un push de développement ne devient pas automatiquement une version stable.

### Arborescence de publication proposée

Cette arborescence est une convention à implémenter, pas le contenu actuel :

```text
site/
├── master-archrepo.asc
├── index.html
└── x86_64/
    ├── master-archrepo.db
    ├── master-archrepo.db.sig
    ├── master-archrepo.db.tar.gz
    ├── master-archrepo.db.tar.gz.sig
    ├── sambapilot-<version>-<revision>-any.pkg.tar.zst
    └── sambapilot-<version>-<revision>-any.pkg.tar.zst.sig
```

Le dossier `x86_64/` peut contenir des paquets `any` comme SambaPilot, ainsi que de futurs paquets spécifiques à cette architecture. Cela ne prouve pas la prise en charge d’autres architectures.

La base doit référencer les noms exacts des paquets présents dans le même répertoire. `repo-add` peut produire des alias sous forme de liens symboliques ; pour GitHub Pages, les convertir en fichiers ordinaires avant de créer l’artefact Pages, avec une signature correspondant exactement aux octets servis sous `master-archrepo.db`. Les artefacts Pages n’acceptent pas les liens symboliques ou physiques.

Publier un ensemble complet et cohérent. Conserver les paquets encore référencés par une base récente afin de ne pas casser un téléchargement pendant une mise à jour. Les contrôles et la signature de la base ne remplacent pas les tests d’installation des applications.

## 2. Préparer la clé de signature

Prévoir une clé OpenPGP dédiée à `master-archrepo`, avec une date d’expiration et une sauvegarde sécurisée hors du dépôt. Choisir un environnement d’administration autorisé pour la créer ; ne pas générer ou remplacer une clé existante implicitement.

La clé publique sera distribuée dans `master-archrepo.asc`. Son empreinte complète devra être publiée dans le README et vérifiée depuis une source de confiance distincte de la seule URL de téléchargement, par exemple la copie conservée lors de la création de la clé.

La clé privée et sa phrase secrète restent hors de Git. Ne jamais les transmettre dans le chat, les logs, les artefacts téléchargeables ou le site publié. L’export destiné à un secret GitHub doit être réalisé dans un emplacement temporaire protégé, puis supprimé de façon contrôlée après configuration.

Avant la première publication, tester qu’une signature de paquet et une signature de base sont vérifiables avec la seule clé publique. Prévoir aussi la rotation et le renouvellement de la clé avant son expiration.

## 3. Préparer GitHub

Les noms ci-dessous sont des **conventions proposées pour le futur workflow**. Aucun code actuel ne les lit. Les créer dans GitHub ne publiera donc rien tant que le workflow n’est pas développé et publié.

Dans `Masternaka/master-archrepo`, ouvrir **Settings → Secrets and variables → Actions**.

### Secrets proposés

| Nom exact | Contenu prévu |
| --- | --- |
| `ARCH_SIGNING_PRIVATE_KEY` | Export privé de la clé dédiée, au format ASCII armuré ; sa valeur ne doit jamais être affichée. |
| `ARCH_SIGNING_PASSPHRASE` | Phrase secrète de la clé, si elle en utilise une. |

### Variables proposées

| Nom exact | Valeur prévue |
| --- | --- |
| `ARCH_REPOSITORY_ENABLED` | `false` pendant toute la préparation ; `true` seulement pour une publication explicitement décidée. |
| `ARCH_SIGNING_KEY_FINGERPRINT` | Empreinte complète de la clé primaire retenue, sans espaces ; vérifiée contre la clé importée. |

Le workflow devra refuser la publication si la clé importée ne correspond pas à l’empreinte attendue. Ne pas exposer ces secrets aux jobs exécutant le code de pull requests. Ne pas utiliser `pull_request_target` pour exécuter des scripts non approuvés avec les secrets.

### Hébergement proposé : GitHub Pages

Dans **Settings → Pages → Build and deployment → Source**, sélectionner **GitHub Actions** lorsque le workflow de publication est prêt. Vérifier auparavant que GitHub Pages est disponible pour la visibilité et l’offre GitHub utilisées.

Le futur job de déploiement devra utiliser l’environnement `github-pages` et les permissions nécessaires `pages: write` et `id-token: write`, limitées au job concerné. Les jobs de test n’ont besoin que de lire les sources.

Sans domaine personnalisé, l’adresse envisagée est :

```text
https://masternaka.github.io/master-archrepo/
```

Cette adresse est une cible prévue, **pas une URL actuellement validée**. La remplacer dans les instructions si GitHub fournit une autre adresse. Vérifier les limites de stockage et de trafic de l’hébergement avant d’y ajouter des applications volumineuses.

## 4. Réaliser la première publication

Garder `ARCH_REPOSITORY_ENABLED=false` jusqu’à ce que les étapes suivantes soient terminées :

1. Une application, par exemple SambaPilot, possède un paquet Arch effectivement construit et testé.
2. Le catalogue identifie sa version, sa provenance et son empreinte ; le choix de licence du projet est réglé avant une distribution publique.
3. Les tests du dépôt passent et un assemblage sans déploiement contient tous les fichiers requis.
4. Les signatures des paquets et de la base sont vérifiables avec la clé publique publiée.
5. Les secrets et variables correspondent aux noms réellement utilisés dans le workflow développé.
6. Pages et le job de déploiement sont configurés ; le contenu à publier ne contient aucun secret ni lien symbolique.

Après autorisation de publication, passer la variable à `true` et lancer manuellement le futur workflow de publication sur la branche retenue. Son nom devra être documenté lorsqu’il existera ; il n’y a aucun workflow à lancer dans l’état actuel.

Un succès des tests avec un déploiement ignoré ne signifie pas que le dépôt est publié. Après déploiement, vérifier par HTTPS :

- la disponibilité de la clé publique, de `x86_64/master-archrepo.db` et de sa signature ;
- la validité de la signature de la base téléchargée ;
- la présence de chaque paquet référencé et de sa signature ;
- la cohérence de version, nom et architecture avec les métadonnées du paquet.

Faire ensuite une première installation dans un environnement Arch/Omarchy de test autorisé, avec une configuration et un trousseau séparés de l’ordinateur personnel. Tester également une mise à jour réelle entre deux versions et le refus d’une signature invalide avant de déclarer le canal utilisable.

## 5. Activer le dépôt sur l’ordinateur Omarchy

N’effectuer cette partie qu’après validation de la publication et accord pour les modifications de la machine. Elle ajoute une clé de confiance à pacman et une source de paquets à `/etc/pacman.conf`. La machine doit disposer d’un trousseau pacman fonctionnel ; ne pas le réinitialiser automatiquement.

### Télécharger et vérifier la clé publique

Avec l’adresse réellement publiée, télécharger la clé dans un dossier de travail utilisateur. Si l’adresse prévue ci-dessus est confirmée, la commande sera :

```sh
curl --fail --location --output master-archrepo.asc https://masternaka.github.io/master-archrepo/master-archrepo.asc
gpg --show-keys --with-fingerprint master-archrepo.asc
```

Comparer l’empreinte complète à celle conservée depuis une source de confiance. Ne pas poursuivre si elle diffère, si plusieurs clés inattendues sont présentes ou si l’identité de la clé est incertaine.

Après cette vérification, importer la clé, contrôler son empreinte dans pacman et signer localement uniquement la clé retenue. Remplacer `EMPREINTE_COMPLETE_VERIFIEE` par la vraie empreinte :

```sh
sudo pacman-key --add master-archrepo.asc
sudo pacman-key --finger EMPREINTE_COMPLETE_VERIFIEE
sudo pacman-key --lsign-key EMPREINTE_COMPLETE_VERIFIEE
```

La signature locale marque cette clé comme approuvée pour pacman. Ce n’est pas une vérification à déléguer à une commande téléchargée et exécutée sans examen.

### Sauvegarder puis modifier la configuration

Créer une copie datée avant toute édition :

```sh
sudo cp -a /etc/pacman.conf "/etc/pacman.conf.before-master-archrepo-$(date +%Y%m%d-%H%M%S)"
sudoedit /etc/pacman.conf
```

Vérifier que la section n’existe pas déjà, puis ajouter ce bloc après les dépôts système existants, en utilisant l’URL réellement validée :

```ini
[master-archrepo]
SigLevel = Required TrustedOnly
Server = https://masternaka.github.io/master-archrepo/$arch
```

`$arch` doit rester littéral dans ce fichier ; pacman le remplace par l’architecture configurée. La section du dépôt doit être hors de `[options]`. Le nom `master-archrepo` doit correspondre à celui de la base publiée.

Ne pas remplacer la configuration entière ni modifier les autres dépôts. Garder les contrôles de signatures actifs ; ne pas ajouter `SigLevel = Never` pour contourner une erreur.

### Synchroniser et installer

La commande suivante synchronise les dépôts et met à jour tout le système. Examiner la transaction avant de la confirmer :

```sh
sudo pacman -Syu
```

Une fois la synchronisation réussie, consulter le catalogue et installer SambaPilot si ce paquet y est réellement présent :

```sh
pacman -Sl master-archrepo
pacman -Si master-archrepo/sambapilot
sudo pacman -Syu master-archrepo/sambapilot
```

L’installation écrit les fichiers du paquet et installe ses dépendances. Pour SambaPilot, le lanceur graphique actuel ouvre le mode démonstration ; l’installation ne configure ni Samba ni les partages.

## 6. Recevoir les mises à jour et ajouter des applications

Quand une nouvelle version signée est publiée dans `master-archrepo`, elle devient candidate à la prochaine mise à jour avec :

```sh
sudo pacman -Syu
```

Cette commande met à jour les paquets installés selon tous les dépôts configurés. Éviter une synchronisation isolée avec `pacman -Sy` suivie d’installations partielles. Ne pas promettre que toutes les interfaces de mise à jour d’Omarchy utiliseront ce dépôt sans vérifier leur comportement sur la version installée.

L’ajout du dépôt ne crée pas de tâche automatique : les mises à jour se font quand l’utilisateur déclenche son parcours habituel. Les nouveaux paquets ajoutés au catalogue ne sont pas installés automatiquement.

Pour chaque nouvelle application : préparer et tester le paquet dans son dépôt source, l’ajouter au catalogue autorisé, publier une version signée dans `master-archrepo`, puis installer explicitement son nom sur Omarchy. Réutiliser la même clé et la même section pacman tant qu’elles restent valides ; aucune nouvelle activation complète n’est nécessaire pour chaque application.

## 7. Dépannage et retrait

| Symptôme | Vérification à effectuer |
| --- | --- |
| Erreur 404 sur la base | URL Pages, sous-dossier d’architecture, nom de la base et présence effective du déploiement. |
| Clé inconnue ou signature non approuvée | Empreinte complète, import et confiance locale ; ne pas désactiver la vérification. |
| Signature invalide ou clé expirée | Comparer le fichier réellement servi à sa signature et contrôler la validité de la clé ; corriger la publication. |
| Paquet introuvable | Synchronisation réussie, nom exact et présence dans la base publiée. |
| Mise à jour non proposée | Version et révision installées comparées à celles du dépôt, règles d’ignorance et éventuel dépôt concurrent. |
| Test réussi mais site absent | Distinguer les résultats des tests, de l’assemblage et du déploiement. |

Pour retirer le dépôt, examiner les paquets personnels installés, puis retirer uniquement la section `[master-archrepo]` de `/etc/pacman.conf` avec une nouvelle sauvegarde préalable. Comparer les modifications à la sauvegarde d’origine ; ne pas restaurer aveuglément tout le fichier si d’autres réglages ont changé depuis.

Les applications déjà installées restent présentes, mais ce dépôt ne leur fournira plus de mises à jour. Leur désinstallation est une opération séparée. La clé peut rester dans le trousseau ; ne la supprimer que si elle n’est utilisée par aucun autre dépôt et après accord explicite.

## Critères pour déclarer le dépôt prêt

Le dépôt sera prêt à utiliser après publication réelle de fichiers cohérents, vérification des signatures téléchargées, installation et mise à jour réussies sur un environnement autorisé, et documentation de l’empreinte, de l’URL finale et du retrait. Aucun de ces résultats n’est déduit de la seule présence de ce guide.

**Prochaine action :** développer le catalogue, les scripts, les tests et le workflow décrits à l’étape 1, avec publication désactivée. Les réglages et l’activation de la machine viendront ensuite.

## Références officielles

- [Configuration des dépôts et des signatures pacman](https://man.archlinux.org/man/pacman.conf.5.en).
- [Gestion des clés avec pacman-key](https://man.archlinux.org/man/pacman-key.8.en).
- [Construction et signature de la base avec repo-add](https://man.archlinux.org/man/repo-add.8.en).
- [Installation et mises à jour avec pacman](https://man.archlinux.org/man/pacman.8.en).
- [Publication GitHub Pages avec un workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
