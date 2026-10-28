# ATI_Instaleur

Un installeur d'applications de création pour Windows, avec une interface PySide6. La liste des logiciels et la façon de les installer sont décrites dans des fichiers YAML, pas dans le code : ajouter un logiciel ou une version, c'est ajouter quelques lignes.

## Comment ça marche

Chaque logiciel a son fichier dans `app/config/`, rangé par catégorie :

- **CGI** : Blender, Houdini, Maya, Mari, Nuke, MotionBuilder, Unity, Unreal Engine 5
- **Développement** : Git, TortoiseGit, VS Code, Visual Studio
- **Graphisme** : Adobe, PureRef
- **Communication** et **Utilitaires** : Discord, DJV, FileZilla, PowerToys, SyncTrazor

Un fichier donne le nom, la description, les versions proposées, et pour chaque version la méthode d'installation (MSI ou EXE), l'adresse de téléchargement et les options d'installation silencieuse. Le code lit ces fichiers, télécharge, installe et affiche la progression.

## Pile technique

Python 3.11, PySide6, PyYAML, PyInstaller pour fabriquer l'exécutable (`ATI_Instaleur.spec`).

## État

En cours de développement, utilisable pour les logiciels déjà décrits. Les adresses de téléchargement sont à jour au moment de l'écriture et peuvent changer chez les éditeurs.

## Licence

MIT. Voir `LICENSE` et `NOTICE`.
