# master-archrepo

Dépôt pacman personnel pour **CachyOS x86_64**. Le workflow GitHub Actions suit les pushes validés par la CI et publie les paquets signés sur GitHub Pages. Une fois le dépôt activé, CachyOS peut les installer et les mettre à jour directement avec pacman.

Le catalogue initial contient **SambaPilot** et **DotfilePilot**. Les deux paquets `any` proviennent de builds vérifiés dans des conteneurs Arch. Le [guide d’activation du dépôt public](docs/publication-github.md) décrit la configuration et l’installation. Le [guide local](docs/preparation-et-activation.md) documente aussi l’assemblage sur une seule machine.

Une fois le dépôt activé, les deux applications s’installent avec cette commande.

```sh
sudo pacman -Syu master-archrepo/sambapilot master-archrepo/dotfilepilot
```
