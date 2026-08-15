# FORENSIC_MEDIA_CONTEXT.md

> **Document de transmission — projet Forensic Media**
>
> Date de consolidation : 15 août 2026  
> Statut : **source de continuité pour reprendre le projet dans Antigravity sans recommencer la conception**  
> Langue produit principale : français  
> Alias utilisé dans les échanges : **Forensic Media**  
> Nom de travail produit : **Plateforme africaine de vérification numérique**
>
> **Important pour l’agent qui reprend le projet :**
> 1. Lire ce document intégralement avant de créer du code.
> 2. Considérer les décisions marquées **FIGÉ** comme acquises.
> 3. Ne pas redessiner le produit depuis zéro.
> 4. Ne pas ajouter des dizaines de fonctionnalités non demandées.
> 5. Protéger strictement le périmètre du MVP V1.
> 6. Signaler une faiblesse importante si elle rend une décision techniquement impossible ou dangereuse, mais ne pas modifier silencieusement une décision figée.
> 7. Le prochain travail attendu n’est plus la conception fonctionnelle générale : **c’est la mise en œuvre concrète du MVP** à partir des spécifications ci-dessous.

---

# 0. ÉTAT EXACT DU PROJET AU MOMENT DE LA TRANSMISSION

La conception du MVP V1 a déjà franchi les étapes suivantes :

- positionnement produit défini ;
- utilisateurs cibles définis ;
- périmètre du MVP figé ;
- moteurs d’analyse définis ;
- logique de résultat définie ;
- principes de preuve et d’explicabilité définis ;
- six écrans du MVP conçus fonctionnellement ;
- cahier des charges fonctionnel et technique du MVP figé ;
- modèle PostgreSQL définitif conçu ;
- API REST V1 conçue ;
- architecture applicative figée ;
- stack technologique figée ;
- architecture de déploiement figée.

## Point d’arrêt exact

**Architecture de déploiement définitive figée : Vercel + Render + Supabase, avec environnements staging et production séparés.**

## Prochaine étape

**Commencer la mise en œuvre concrète du MVP.**

Ne pas revenir à une phase de brainstorming produit générale.  
Ne pas recommencer les écrans.  
Ne pas refaire le choix de la stack.  
Ne pas remplacer l’architecture sans raison technique majeure.

---

# 1. IDENTITÉ ET POSITIONNEMENT DU PRODUIT

## 1.1 Nom

Le nom commercial définitif n’a pas encore été choisi.

Utiliser pour l’instant :

**Plateforme africaine de vérification numérique**

Le terme **Forensic Media** est utilisé comme nom de projet/conversation et peut servir de nom de dossier de développement, mais **ne pas le considérer automatiquement comme le nom commercial final**.

## 1.2 Positionnement retenu

**Plateforme africaine d’analyse de provenance et de vérification des médias numériques.**

Promesse principale :

**« Analysez l’origine, l’intégrité et le contexte d’un média avant de lui faire confiance. »**

Autre formulation stratégique :

**« Nous ne vous disons pas seulement si un contenu semble faux. Nous vous montrons ce que nous pouvons prouver sur son origine, ses modifications et son contexte. »**

## 1.3 Philosophie fondamentale

La plateforme suit la logique :

**preuve → sources → explication → conclusion prudente**

Elle ne doit jamais prétendre qu’un algorithme « détecte la vérité ».

La solution n’est pas :

- un simple détecteur d’images IA ;
- un détecteur magique de fake news ;
- un système de certification absolue du vrai et du faux.

Elle doit expliquer **ce qui est connu, déclaré, retrouvé, estimé ou inconnu**.

---

# 2. PROBLÈME TRAITÉ

Question centrale :

**Comment permettre aux citoyens, journalistes, fact-checkers, médias, institutions et professionnels de vérifier l’origine, l’intégrité et le contexte d’un contenu numérique avant de lui faire confiance ou de le diffuser ?**

Constat essentiel :

- un contenu problématique n’est pas nécessairement généré par IA ;
- une vraie photographie peut être sortie de son contexte ;
- une image peut être accompagnée d’une fausse date, d’un faux lieu ou d’une fausse légende ;
- une image générée par IA peut également être utilisée de manière honnête.

Donc :

**détection d’IA ≠ détection de désinformation.**

---

# 3. UTILISATEURS CIBLES

Utilisateurs identifiés :

- grand public ;
- journalistes ;
- fact-checkers ;
- médias ;
- cellules de communication ;
- chercheurs ;
- organisations de la société civile ;
- administrations publiques ;
- institutions ;
- équipes de cybersécurité ;
- professionnels de l’investigation numérique ;
- éventuellement certaines structures d’analyse et de renseignement, dans un cadre légal.

À terme, deux niveaux de produit sont envisagés :

## Version publique

Très simple, adaptée notamment à une personne qui reçoit une image douteuse sur WhatsApp et souhaite la vérifier.

## Version professionnelle / institutionnelle

À terme :

- historique ;
- davantage d’analyses ;
- rapports ;
- archivage ;
- équipes ;
- audit ;
- preuves techniques ;
- API ;
- fonctionnalités avancées.

**Le modèle économique et les prix ne sont pas figés.**

---

# 4. PÉRIMÈTRE DU MVP V1 — FIGÉ

## 4.1 Type de média

**Images uniquement.**

Formats autorisés :

- JPG ;
- JPEG ;
- PNG ;
- WEBP.

Limite maximale figée pour l’API :

**20 MiB par image.**

L’upload doit contrôler :

- MIME déclaré ;
- signature réelle du fichier ;
- cohérence format/contenu ;
- capacité réelle à décoder l’image.

## 4.2 Hors périmètre V1

Ne pas ajouter maintenant :

- vidéo ;
- audio ;
- deepfake vocal ;
- bot WhatsApp ;
- application Android native ;
- blockchain ;
- reconnaissance faciale ;
- surveillance de comptes sociaux ;
- géolocalisation forensic avancée ;
- attribution d’auteur ;
- analyse politique ;
- score global de vérité ;
- certificat de vérité ;
- moteur IA propriétaire massif ;
- collaboration avancée ;
- collections ;
- tags ;
- dossiers/cases ;
- favoris ;
- partage en équipe ;
- SSO ;
- API publique pour clients externes ;
- facturation avancée ;
- fonctionnalités gouvernementales complexes.

La roadmap envisagée à long terme était :

- V1 : images ;
- V2 : vidéos ;
- V3 : audio / deepfake vocal ;
- V4 : WhatsApp ;
- V5 : API et fonctions institutionnelles avancées.

Cette roadmap n’oblige pas à développer ces éléments maintenant.

---

# 5. LES QUATRE QUESTIONS AUXQUELLES LE PRODUIT DOIT RÉPONDRE

La plateforme sépare quatre dimensions.

## 5.1 Provenance

Questions :

- D’où vient ce média ?
- Existe-t-il un manifeste C2PA ?
- Existe-t-il des Content Credentials ?
- La chaîne de provenance est-elle valide ?
- Une utilisation d’IA est-elle déclarée ?

## 5.2 Intégrité

Questions :

- Le fichier présente-t-il des informations techniques cohérentes ?
- Y a-t-il des anomalies à examiner ?
- Les métadonnées disponibles sont-elles cohérentes ?

## 5.3 IA / manipulation

Questions :

- Existe-t-il une utilisation d’IA explicitement déclarée ?
- Existe-t-il des indices estimés de génération ou de manipulation IA ?

Le moteur IA n’est qu’un **module d’estimation**.

## 5.4 Contexte

Questions :

- L’image a-t-elle déjà circulé ?
- Existe-t-il une version antérieure ?
- Dans quel pays / site / contexte a-t-elle été publiée ?
- La date retrouvée contredit-elle une affirmation actuelle ?
- Existe-t-il déjà un fact-check ?

---

# 6. LES SIX MOTEURS DU MVP V1

# 6.1 Moteur C2PA / Content Credentials

Analyse notamment :

- présence/absence d’un manifeste ;
- validité du manifeste ;
- signature cryptographique ;
- confiance possible dans la signature ;
- signataire ;
- logiciel/claim generator déclaré ;
- actions ;
- ingrédients ;
- `digitalSourceType` ;
- utilisation déclarée d’IA ;
- historique disponible.

Technologie figée :

**c2pa-python 0.37.7**  
ou mécanismes officiels compatibles C2PA derrière l’adaptateur dédié.

Règle absolue :

**absence de C2PA ≠ absence d’IA.**

Message attendu en cas d’absence de provenance C2PA :

**« Aucune preuve de provenance C2PA détectée. Origine indéterminée. »**

Ne jamais afficher :

**« Cette image n’a pas été générée par IA »** uniquement parce qu’aucun manifeste C2PA n’a été trouvé.

---

# 6.2 Moteur Métadonnées

Technologie figée :

**ExifTool 13.59**

Informations possibles :

- EXIF ;
- XMP ;
- IPTC ;
- appareil ;
- modèle ;
- logiciel ;
- date ;
- dimensions ;
- GPS éventuel ;
- auteur ;
- copyright ;
- autres métadonnées utiles.

Règle :

**absence d’EXIF ≠ image générée par IA.**

---

# 6.3 Moteur Empreintes numériques

## SHA-256

But :

identifier exactement le fichier.

Règle :

**le SHA-256 doit être calculé avant toute transformation du fichier original.**

## pHash

But :

reconnaître des versions proches après certaines transformations :

- compression ;
- redimensionnement ;
- réexportation ;
- modifications légères ;
- certains recadrages.

Stack figée :

- Python `hashlib` pour SHA-256 ;
- `ImageHash 4.3.2` ;
- `Pillow`.

---

# 6.4 Moteur IA

Nature :

**estimation, jamais preuve absolue.**

Le fournisseur doit être remplaçable.

Fournisseur prévu dans la stack au moment du gel technique :

**Hive AI API**, derrière une interface/adaptateur `AIProvider`.

Il faut pouvoir changer de fournisseur sans réécrire le reste du domaine.

Ne pas présenter un simple chiffre comme verdict final.

Exemple à éviter :

**« Image générée par IA : 87 % »**

Catégories produit retenues :

- `indeterminate` → Indéterminé ;
- `low` → Faibles indices ;
- `moderate` → Indices modérés ;
- `high` → Indices élevés ;
- `declared` → Utilisation d’IA déclarée.

Une estimation du détecteur IA seule ne doit jamais produire la conclusion finale.

---

# 6.5 Moteur Contexte Web / correspondances

Objectifs :

- retrouver des images identiques ;
- retrouver des versions proches ;
- retrouver des pages antérieures ;
- retrouver des dates antérieures ;
- identifier des contextes différents.

Technologie figée :

**Google Cloud Vision Web Detection**

Exemple métier :

L’utilisateur affirme :

**« Cette photo aurait été prise aujourd’hui à Ouagadougou. »**

Si une version proche est retrouvée au Mali en 2024, la plateforme doit pouvoir signaler :

**« Contexte potentiellement trompeur. Une version antérieure a été retrouvée. »**

---

# 6.6 Moteur Fact-checks

Technologie figée :

**Google Fact Check Tools API**

Objectif :

retrouver des vérifications déjà publiées.

Sources à envisager progressivement, sans les considérer automatiquement disponibles via une API :

- FasoCheck ;
- Africa Check ;
- AFP Factuel ;
- autres organismes fiables.

Règle :

**absence de fact-check ≠ affirmation vraie.**

---

# 7. TYPOLOGIE DE PREUVE — FIGÉE

Chaque élément affiché doit pouvoir appartenir à une catégorie conceptuelle claire.

## PREUVE TECHNIQUE

Exemple :

signature C2PA valide.

## INFORMATION DÉCLARÉE

Exemple :

date EXIF ou donnée déclarée dans un manifeste.

## CORRESPONDANCE EXTERNE

Exemple :

version antérieure de l’image retrouvée sur le Web.

## ESTIMATION

Exemple :

résultat d’un détecteur IA.

Cette distinction est centrale et doit être conservée dans :

- le modèle de données ;
- les réponses API ;
- l’écran de résultat ;
- le rapport ;
- les explications.

---

# 8. SYSTÈME DE RÉSULTAT — FIGÉ

## 8.1 Aucun score global de vérité

Interdit :

- score « vérité 82/100 » ;
- pourcentage unique « fiable à 87 % » ;
- verdict algorithmique absolu ;
- certificat « vrai/faux ».

## 8.2 Indicateurs indépendants

### Provenance

Valeurs domaine figées :

- `verified` → Vérifiée ;
- `partial` → Partielle ;
- `unknown` → Inconnue ;
- `inconsistent` → Incohérente.

### Intégrité

Valeurs domaine figées :

- `clear` → Aucun problème identifié ;
- `review` → Éléments à examiner ;
- `major_anomaly` → Anomalie importante.

### IA

Valeurs domaine figées :

- `indeterminate` → Indéterminé ;
- `low` → Faibles ;
- `moderate` → Modérés ;
- `high` → Élevés ;
- `declared` → Utilisation d’IA déclarée.

### Contexte

Valeurs domaine figées :

- `coherent` → Cohérent ;
- `review` → À vérifier ;
- `potential_decontextualization` → Décontextualisation potentielle.

## 8.3 Niveau de conclusion synthétique

Le modèle de données définitif a séparé la conclusion globale prudente des quatre indicateurs.

Valeurs figées :

- `no_major_alert` ;
- `review_recommended` ;
- `important_attention`.

Exemple d’affichage :

**⚠️ Vérification supplémentaire recommandée**

Cette conclusion doit être expliquée par la section :

**« Pourquoi cette conclusion ? »**

---

# 9. ÉCRAN 1 — ANALYSER UNE IMAGE — FIGÉ

Objectif :

permettre à un utilisateur non technique de lancer une analyse rapidement.

## Éléments

Titre possible :

**« Vérifiez une image avant de lui faire confiance »**

ou :

**« Vérifiez une image avant de la partager »**

Zone :

- drag & drop ;
- bouton **Sélectionner une image**.

Après sélection :

- aperçu ;
- nom ;
- format ;
- taille ;
- dimensions.

Bouton principal :

**Analyser cette image**

## Affirmation facultative

Question :

**« Avez-vous reçu cette image avec une affirmation particulière ? »**

Exemple :

**« Cette manifestation aurait eu lieu aujourd’hui à Ouagadougou. »**

Cette affirmation doit être transmise au moteur contextuel.

## Analyses activées

- C2PA/provenance ;
- métadonnées ;
- empreintes ;
- IA ;
- contexte Web ;
- fact-checks ;
- synthèse.

## Vie privée

Le fichier original n’a pas vocation à être conservé systématiquement.

La politique V1 privilégie la suppression du média original après traitement selon les préférences/règles de rétention.

---

# 10. ÉCRAN 2 — ANALYSE EN COURS — FIGÉ

Route applicative prévue :

`/analyse/{analysis_id}/progress`

Puis redirection vers :

`/analyse/{analysis_id}/resultat`

Ce n’est pas un simple loader.

Étapes visibles possibles :

- fichier reçu ;
- empreinte numérique calculée ;
- métadonnées analysées ;
- Content Credentials vérifiés ;
- analyse IA ;
- recherche de versions similaires ;
- recherche de fact-checks ;
- synthèse.

## Règle UX importante

Ne jamais révéler une conclusion avant la fin de la synthèse.

On peut afficher :

**« Analyse IA terminée »**

mais pas immédiatement :

**« IA détectée »**

avant synthèse finale.

## Architecture temps réel

Décision figée :

**polling HTTP**, pas WebSocket pour le MVP.

Endpoint API de référence :

`GET /api/v1/analyses/{id}/progress`

---

# 11. ÉCRAN 3 — RÉSULTAT D’ANALYSE — FIGÉ

Route :

`/analyse/{analysis_id}/resultat`

Trois niveaux de lecture :

1. conclusion immédiatement compréhensible ;
2. résultats des différents moteurs ;
3. preuves et informations techniques détaillées.

## Bloc supérieur

- conclusion prudente ;
- quatre indicateurs indépendants.

Exemple :

- Provenance : partiellement vérifiable ;
- Intégrité : aucun problème majeur ;
- IA : indices modérés ;
- Contexte : correspondance antérieure trouvée.

## Cartes détaillées

1. Provenance / C2PA ;
2. Métadonnées ;
3. Analyse IA ;
4. Présence antérieure / contexte Web ;
5. Fact-checks ;
6. Informations techniques.

## Section centrale

**Pourquoi cette conclusion ?**

Exemples d’éléments explicatifs :

- correspondance Web antérieure retrouvée ;
- date antérieure à l’affirmation ;
- origine non confirmée ;
- métadonnées insuffisantes ;
- indices IA modérés.

L’utilisateur doit pouvoir comprendre **pourquoi** le système arrive à sa synthèse.

---

# 12. ÉCRAN 4 — HISTORIQUE DES ANALYSES — FIGÉ

Route :

`/historique`

Routes depuis une entrée :

- résultat : `/analyse/{analysis_id}/resultat`
- rapport : `/analyse/{analysis_id}/rapport`

## En-tête

- titre de page ;
- sous-titre ;
- recherche ;
- filtres ;
- bouton **+ Nouvelle analyse**.

## Affichage

Desktop :

liste structurée / cartes hybrides.

Mobile :

cartes verticales.

## Chaque entrée montre

- miniature si le média est encore conservé ;
- sinon icône neutre + texte **« Fichier original supprimé »** ;
- nom du fichier ;
- date/heure ;
- affirmation facultative raccourcie ;
- conclusion prudente ;
- quatre indicateurs indépendants ;
- état technique de l’analyse ;
- actions.

## Badges

### Provenance

- Vérifiée ;
- Partielle ;
- Inconnue ;
- Incohérente.

### Intégrité

- Aucun problème identifié ;
- Éléments à examiner ;
- Anomalie importante.

### IA

- Indéterminé ;
- Faibles ;
- Modérés ;
- Élevés ;
- Utilisation d’IA déclarée.

### Contexte

- Cohérent ;
- À vérifier ;
- Décontextualisation potentielle.

## Recherche

Doit couvrir au minimum :

- nom de fichier ;
- identifiant d’analyse ;
- éventuellement texte de l’affirmation.

## Filtres V1 retenus

- date ;
- conclusion ;
- provenance ;
- IA ;
- contexte.

## Tri

Au minimum :

- plus récent ;
- plus ancien.

## Pagination

Prévoir pagination ou mécanisme **charger plus**, sans charger l’intégralité de l’historique.

## Actions d’une entrée

- **Voir l’analyse** ;
- ouvrir/générer le rapport ;
- menu `…` ;
- suppression, avec confirmation lorsque applicable.

## États particuliers

L’historique doit distinguer :

- analyse en attente/en cours ;
- analyse terminée ;
- analyse échouée.

Le **statut technique** de traitement est séparé du **niveau de conclusion**.

---

# 13. ÉCRAN 5 — RAPPORT D’ANALYSE — FIGÉ

Nom retenu :

**Rapport d’analyse de média numérique**

Ne jamais l’appeler :

**certificat de vérité**.

Route applicative :

`/analyse/{analysis_id}/rapport`

## UX retenue

Le rapport est d’abord un **rapport Web structuré**, pas seulement un bouton PDF.

L’utilisateur peut consulter un aperçu puis :

**Télécharger en PDF**

## Contenu obligatoire

### Identification

- identifiant d’analyse ;
- fichier ;
- date/heure ;
- dimensions ;
- SHA-256 ;
- pHash ;
- affirmation fournie par l’utilisateur si elle existe.

### Synthèse

- conclusion prudente ;
- quatre indicateurs indépendants.

### Explication

Section :

**Pourquoi cette conclusion ?**

### Sections techniques

- provenance / C2PA ;
- intégrité ;
- métadonnées ;
- IA ;
- contexte Web ;
- fact-checks.

### Sources et méthodes

Indiquer :

- sources externes ;
- moteurs/fournisseurs utilisés ;
- type de chaque élément : preuve / déclaration / correspondance / estimation ;
- limites connues.

### Limites

Le rapport doit rappeler notamment :

- absence de C2PA ≠ absence d’IA ;
- absence d’EXIF ≠ image IA ;
- absence de fact-check ≠ affirmation vraie ;
- un détecteur IA fournit une estimation ;
- la plateforme ne certifie pas la vérité.

### Métadonnées du rapport

- version ;
- date/heure de génération ;
- éléments nécessaires à la traçabilité.

## Immutabilité

Décision figée :

**un rapport généré est un snapshot horodaté et immuable.**

Une nouvelle vérification doit créer :

- une nouvelle analyse ;
- ou une nouvelle version logique distincte ;

mais ne doit pas réécrire silencieusement un rapport déjà produit.

## PDF

Le PDF exact généré doit être conservé comme objet.

Le serveur doit calculer et enregistrer le :

**SHA-256 du PDF généré.**

Le modèle comporte une table `analysis_reports` destinée notamment à stocker :

- version ;
- snapshot des données ;
- version de template ;
- référence de stockage ;
- hash du PDF ;
- informations de génération.

---

# 14. ÉCRAN 6 — CONNEXION / COMPTE — FIGÉ

Routes applicatives :

- `/connexion`
- `/inscription`
- `/compte`
- `/mot-de-passe-oublie`

## 14.1 Usage sans compte

**L’analyse anonyme est autorisée.**

Un compte n’est pas obligatoire pour essayer la vérification d’une image.

Un compte devient utile/nécessaire principalement pour :

- historique durable ;
- rapports conservés ;
- préférences ;
- gestion des données ;
- services professionnels futurs.

## 14.2 Authentification V1

V1 :

- e-mail ;
- mot de passe ;
- vérification e-mail ;
- mot de passe oublié ;
- réinitialisation ;
- déconnexion.

**Pas de social login en V1.**

Le compte de base est standard.

Le champ `account_type` doit préparer les évolutions :

- standard/public ;
- professional ;
- institutional.

Ne pas développer maintenant toute la logique commerciale des comptes pro/institutionnels.

## 14.3 Analyse anonyme

En base :

`user_id = null`

Le `public_id` de type :

`AN-2026-xxxxx`

est uniquement :

- une référence ;
- un identifiant d’affichage.

**Il ne constitue jamais un secret d’accès.**

L’autorisation pour une analyse anonyme repose sur :

- identifiant interne non devinable (UUID) ;
- + token secret d’accès.

Le token secret est retourné au client, mais la base ne conserve que son **hash**.

Prévoir expiration et révocation.

## 14.4 Préférences de confidentialité

Préférences figées :

- `retain_analysis_history`
- `retain_original_files`

Principe :

**suppression du fichier original par défaut / privacy-first.**

Les résultats et rapports peuvent être conservés sans conserver l’original.

Lorsque le média original est supprimé :

- supprimer également les miniatures ;
- supprimer les copies/derivés inutiles ;
- ne pas laisser un duplicata oublié dans le stockage.

Les analyses anonymes ne doivent pas conserver durablement le média original par défaut.

## 14.5 Suppressions

Les suppressions sensibles doivent demander une confirmation.

Une suppression physique peut être asynchrone.

Le compte doit permettre la gestion des données personnelles et des analyses appartenant à l’utilisateur.

---

# 15. MODÈLE DE DONNÉES POSTGRESQL — FIGÉ

## 15.1 Principes

Base :

**PostgreSQL 17**

ORM/migrations :

- SQLAlchemy 2.x ;
- psycopg 3 ;
- Alembic.

Identifiants internes :

**UUID**

Identifiant public/humain :

`public_id`

Règle :

**`public_id` sert à l’affichage/référence, jamais à l’autorisation.**

JSONB :

réservé aux données réellement variables ou spécifiques à un fournisseur.

Ne pas remplacer les colonnes domaine importantes par un énorme blob JSON.

Les rapports utilisent un **snapshot JSONB immuable** afin de figer exactement l’état qui a servi à leur génération.

## 15.2 Entités définitives

La conception finale contient les entités suivantes :

1. `users`
2. `user_preferences`
3. `analyses`
4. `analysis_access_tokens`
5. `stored_objects`
6. `analysis_engine_runs`
7. `c2pa_results`
8. `metadata_results`
9. `ai_results`
10. `web_matches`
11. `fact_check_matches`
12. `synthesis_results`
13. `synthesis_evidence`
14. `analysis_reports`
15. `analysis_events`

> Une ancienne synthèse parlait par erreur de « 13 tables » tout en listant ces 15 entités. **La liste de référence à conserver est celle des 15 entités ci-dessus.**

## 15.3 Relations principales

- `analyses.user_id` → `users.id`, nullable pour analyse anonyme ;
- une analyse possède 0..N tokens d’accès anonymes ;
- une analyse possède 0..N objets stockés ;
- une analyse possède 0..N événements ;
- une analyse possède plusieurs exécutions moteur dans `analysis_engine_runs` ;
- C2PA / metadata / AI sont essentiellement des résultats 0..1 par run/moteur pertinent ;
- correspondances Web : 0..N ;
- fact-checks : 0..N ;
- synthèse : résultat 0..1 ;
- `synthesis_evidence` relie la synthèse aux éléments qui justifient la conclusion ;
- une analyse peut produire plusieurs rapports immuables/versionnés.

---

# 16. TABLE `analyses` — CONTRATS DOMAINE

Champs de base attendus au minimum :

- `id` UUID ;
- `public_id` ;
- `user_id` nullable ;
- `original_filename` ;
- `mime_type` ;
- `file_size` ;
- `sha256` ;
- `phash` ;
- affirmation utilisateur/`claim` facultative ;
- dates ;
- état de traitement ;
- préférences/références nécessaires à la conservation ;
- champs de synthèse ou relations correspondantes.

## Statut technique principal

Valeurs figées :

- `pending`
- `running`
- `completed`
- `failed`

Ne pas confondre ce statut avec :

- le niveau de conclusion ;
- les statuts des moteurs individuels.

## Conclusion

`conclusion_level` :

- `no_major_alert`
- `review_recommended`
- `important_attention`

## Indicateurs

`provenance` :

- `verified`
- `partial`
- `unknown`
- `inconsistent`

`integrity` :

- `clear`
- `review`
- `major_anomaly`

`ai` :

- `indeterminate`
- `low`
- `moderate`
- `high`
- `declared`

`context` :

- `coherent`
- `review`
- `potential_decontextualization`

---

# 17. TABLE `analysis_engine_runs` — COLONNES FIGÉES

Liste exacte récupérée de la conception définitive :

1. `id`
2. `analysis_id`
3. `engine_code`
4. `status`
5. `attempt_no`
6. `provider`
7. `engine_version`
8. `provider_version`
9. `started_at`
10. `completed_at`
11. `duration_ms`
12. `error_code`
13. `public_error_message`
14. `private_error_details`
15. `created_at`

## `status` moteur

Valeurs figées :

- `pending`
- `running`
- `completed`
- `unavailable`
- `failed`
- `not_applicable`

`attempt_no` est un numéro de tentative.

But de cette table :

- auditabilité ;
- observabilité ;
- distinction entre un échec global et un fournisseur indisponible ;
- versionnement des moteurs/fournisseurs ;
- support des nouvelles tentatives sans écraser l’historique.

`private_error_details` ne doit jamais être exposé brut à l’utilisateur.

---

# 18. TABLES DE RÉSULTATS

## `c2pa_results`

Conserver notamment :

- analyse/run ;
- présence manifeste ;
- validité ;
- confiance/signature ;
- signataire ;
- claim generator ;
- `digital_source_type` ;
- IA déclarée ;
- actions ;
- données variables nécessaires.

## `metadata_results`

Conserver notamment :

- appareil ;
- modèle ;
- logiciel ;
- date originale ;
- disponibilité GPS ;
- largeur ;
- hauteur ;
- métadonnées brutes utiles.

## `ai_results`

Conserver :

- fournisseur/modèle ;
- score brut fournisseur si nécessaire pour audit ;
- classification produit ;
- confiance/valeurs utiles ;
- version du moteur via `analysis_engine_runs`.

**Le score brut n’est pas le verdict utilisateur.**

## `web_matches`

0..N correspondances :

- URL ;
- domaine ;
- type de correspondance ;
- score de correspondance ;
- date trouvée/publication lorsque disponible ;
- données fournisseur nécessaires.

## `fact_check_matches`

0..N :

- publisher ;
- claim ;
- rating ;
- URL ;
- review date ;
- autres champs fournisseur utiles.

## `synthesis_results`

Contient la synthèse prudente :

- niveau de conclusion ;
- quatre indicateurs ;
- résumé/explication ;
- version du moteur de synthèse si applicable ;
- dates.

## `synthesis_evidence`

Relie explicitement la conclusion aux éléments de preuve.

But :

permettre à **« Pourquoi cette conclusion ? »** d’être généré à partir d’éléments identifiables et traçables, au lieu d’un texte opaque.

---

# 19. TABLES D’ACCÈS, STOCKAGE, RAPPORTS ET ÉVÉNEMENTS

## `analysis_access_tokens`

Pour accès anonyme :

- ne jamais stocker le token en clair ;
- stocker `token_hash` ;
- expiration ;
- possibilité de révocation ;
- association à l’analyse ;
- informations temporelles nécessaires.

## `stored_objects`

Représente les objets privés :

- original ;
- preview/thumbnail ;
- PDF de rapport ;
- autres copies de travail strictement nécessaires.

Le stockage réel est dans Supabase Storage.

La base conserve la référence et les métadonnées nécessaires.

## `analysis_reports`

Rapports :

- immuables ;
- versionnés ;
- snapshot des données ;
- version du template ;
- référence de l’objet PDF ;
- SHA-256 du PDF ;
- date de génération.

La génération d’un même rapport doit être **idempotente** lorsque la même version/snapshot est demandée.

## `analysis_events`

Journal métier / traçabilité.

Événements importants à journaliser :

- analyse créée ;
- upload validé ;
- hash calculé ;
- moteur lancé/terminé/indisponible/échoué ;
- synthèse terminée ;
- rapport généré ;
- suppression demandée/effectuée ;
- autres événements métier pertinents.

Ne pas confondre journal métier avec les logs techniques d’infrastructure.

---

# 20. API REST V1 — FIGÉE

Préfixe :

`/api/v1`

Style :

REST.

Identifiants dans les URLs :

**UUID internes**, pas `public_id`.

## 20.1 Auth

Contrat prévu :

- register ;
- login ;
- logout ;
- verify email ;
- resend verification ;
- forgot password ;
- reset password.

Ressources :

- `GET /me`
- `PATCH /me`
- `DELETE /me`
- `GET /me/preferences`
- `PATCH /me/preferences`

Authentification utilisateur :

**Bearer access token** côté API.

Implémentation auth figée :

**Supabase Auth**

La validation d’autorisation reste contrôlée côté serveur/API.

## 20.2 Analyse

Création :

`POST /api/v1/analyses`

Content-Type :

`multipart/form-data`

Champs :

- `file`
- `claim` facultatif

Réponse :

**HTTP 202 Accepted**

car l’analyse complète est asynchrone.

Formats/MIME :

- `image/jpeg`
- `image/png`
- `image/webp`

Extensions :

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`

Max :

**20 MiB**

## 20.3 Polling

`GET /api/v1/analyses/{id}/progress`

Le frontend poll cet endpoint.

Ne pas utiliser Redis comme source du statut public.

La source durable du statut est PostgreSQL.

Ne pas renvoyer de verdict intermédiaire susceptible de contredire la synthèse finale.

## 20.4 Lecture résultat

Famille d’endpoints figée :

- analyse/détail ;
- progress ;
- result ;
- evidence ;
- c2pa ;
- metadata ;
- ai ;
- web-matches ;
- fact-checks ;
- preview.

Routes connues explicitement :

- `GET /api/v1/analyses/{id}/progress`
- `GET /api/v1/analyses/{id}/result`
- `GET /api/v1/analyses/{id}/evidence`
- `GET /api/v1/analyses/{id}/c2pa`
- `GET /api/v1/analyses/{id}/metadata`
- `GET /api/v1/analyses/{id}/ai`
- `GET /api/v1/analyses/{id}/web-matches`
- `GET /api/v1/analyses/{id}/fact-checks`
- `GET /api/v1/analyses/{id}/preview`

La ressource d’analyse possède également son endpoint de détail.

## 20.5 Historique

`GET /api/v1/analyses`

Doit supporter :

- pagination ;
- recherche ;
- filtres de l’écran Historique ;
- tri récent/ancien.

Filtres produit V1 :

- date ;
- conclusion ;
- provenance ;
- IA ;
- contexte.

## 20.6 Reanalyse

Une action de réanalyse existe :

`POST` sur la ressource d’analyse/reanalyse.

Règle :

ne pas écraser silencieusement un ancien rapport immuable.

## 20.7 Suppression

`DELETE` sur la ressource d’analyse.

Doit :

- vérifier propriétaire/token d’accès ;
- déclencher la suppression des objets associés selon la politique ;
- supprimer thumbnails/copies inutiles ;
- être compatible avec une suppression asynchrone ;
- tracer l’événement.

## 20.8 Rapports

Le contrat V1 comprend :

- création d’un rapport ;
- liste des rapports d’une analyse ;
- détail d’un rapport ;
- téléchargement du PDF.

Règles :

- immuable ;
- versionné ;
- idempotent ;
- hash SHA-256 ;
- snapshot exact des résultats.

> Les intitulés exacts de tous les sous-chemins `reports` n’ont pas pu être récupérés mot pour mot dans l’historique disponible. Ne pas redessiner le comportement ; conserver le modèle REST naturel autour de `/analyses/{analysis_id}/reports` et `/reports/{report_id}` si aucun autre fichier de contrat API n’est présent dans le dépôt.

## 20.9 Santé

Endpoints d’exploitation prévus :

- `/health`
- `/ready`

---

# 21. ACCÈS ANONYME API — FIGÉ

Lors de la création d’une analyse anonyme :

- `user_id = null` ;
- le serveur crée un token secret ;
- le client reçoit le secret ;
- la base conserve uniquement le hash.

Header d’accès anonyme retenu :

`X-Analysis-Token`

`public_id` n’est jamais suffisant.

L’API doit vérifier :

- hash ;
- expiration ;
- révocation ;
- analyse correspondante.

Ne jamais journaliser le token secret en clair.

---

# 22. ARCHITECTURE APPLICATIVE — FIGÉE

Style :

**monolithe modulaire + worker(s) asynchrones.**

Ce n’est pas une architecture microservices complexe.

## Flux principal

```text
Utilisateur
   ↓
Next.js
   ↓ HTTPS
FastAPI
   ↓
PostgreSQL + Supabase Storage
   ↓
Création job Celery
   ↓
Redis broker
   ↓
Worker Celery
   ↓
Orchestrateur d’analyse
   ├── C2PA
   ├── ExifTool
   ├── SHA-256 / pHash
   ├── AIProvider
   ├── WebContextProvider
   └── FactCheckProvider
   ↓
PostgreSQL + Storage
   ↓
Synthèse
   ↓
Résultat / rapport
```

## Règle Celery

Le job envoyé dans la file contient surtout :

`analysis_id`

**Ne pas transporter l’image dans Redis.**

## Redis

Redis sert de :

**broker/file de jobs**

Il n’est pas :

- la base de résultats ;
- le stockage image ;
- la source durable du statut ;
- un cache contenant les médias.

## Worker

Le worker :

- récupère l’analyse via PostgreSQL/Storage ;
- orchestre les moteurs ;
- persiste chaque état ;
- persiste les résultats ;
- gère les erreurs par moteur ;
- produit la synthèse lorsque les conditions sont réunies.

## Adaptateurs

Les services externes doivent être derrière des interfaces remplaçables.

Au minimum conceptuellement :

- `AIProvider`
- `WebContextProvider`
- `FactCheckProvider`

Objectif :

pouvoir changer un fournisseur sans réécrire le domaine, la base ou les écrans.

---

# 23. STACK TECHNOLOGIQUE — FIGÉE

## Frontend

- **Next.js 16**
- **TypeScript**
- **Node.js 24 LTS**
- **Tailwind CSS 4**

## Backend

- **Python 3.12**
- **FastAPI**
- **Pydantic v2**
- **SQLAlchemy 2.x**
- **psycopg 3**
- **Alembic**

## Base / Auth / Storage

- **PostgreSQL 17**
- **Supabase Auth**
- **Supabase Storage privé, compatible objet/S3**

## Jobs

- **Celery 5.6**
- **Redis**

## Analyse média

- **c2pa-python 0.37.7**
- **ExifTool 13.59**
- `hashlib` SHA-256
- **ImageHash 4.3.2**
- **Pillow**

## Services externes

- **Google Cloud Vision Web Detection**
- **Google Fact Check Tools API**
- **Hive AI API** derrière `AIProvider`

## HTTP

- **HTTPX**

## Rapports

- **Jinja2**
- **WeasyPrint 69**

## Environnement

- **Docker**
- **Docker Compose**

---

# 24. STOCKAGE — FIGÉ

Service :

**Supabase Storage privé**

Buckets de référence :

- `media-originals`
- `media-previews`
- `analysis-reports`

Tous doivent être privés.

Le navigateur ne doit pas disposer d’un accès permanent public au bucket.

Préférer :

- autorisation API ;
- URLs signées de courte durée lorsque nécessaire.

## Principe d’intégrité

Le fichier original ne doit jamais être modifié par l’analyse.

Flux :

```text
fichier original
→ validation
→ SHA-256
→ horodatage/enregistrement
→ stockage privé
→ copie de travail si nécessaire
→ moteurs
```

---

# 25. RAPPORT PDF — ARCHITECTURE

Pipeline :

1. charger snapshot ;
2. rendre template Jinja2 ;
3. générer PDF via WeasyPrint ;
4. calculer SHA-256 du PDF ;
5. stocker PDF dans `analysis-reports` ;
6. enregistrer référence + hash + version dans `analysis_reports`.

Ne pas générer un PDF depuis un état mutable puis écraser l’ancien fichier.

---

# 26. DÉPLOIEMENT — FIGÉ

## Production

### Frontend

**Vercel**

Héberge :

- Next.js 16.

### Backend

**Render — région Frankfurt**

Héberge :

- FastAPI API ;
- worker Celery ;
- Redis / Key Value.

### Données

**Supabase — Frankfurt**

Fournit :

- PostgreSQL 17 ;
- Auth ;
- Storage privé.

## Flux réseau

```text
Navigateur
  ↓ HTTPS
Vercel
  ↓ HTTPS
Render FastAPI
  ↓ TLS
Supabase PostgreSQL / Auth / Storage

Render FastAPI
  ↓
Redis

Redis
  ↓
Celery Worker

Celery Worker
  ↓ HTTPS
C2PA/local tools + fournisseurs externes
```

Redis n’est jamais exposé au navigateur.

---

# 27. ENVIRONNEMENTS — FIGÉ

## DEV local

Prévu :

- Next.js local ;
- FastAPI local ;
- Celery local ;
- Redis Docker ;
- Supabase local ou environnement de dev ;
- Docker Compose.

## STAGING

Séparé de production :

- Vercel Preview/staging ;
- Render API staging ;
- Render worker staging ;
- Redis staging ;
- projet Supabase staging distinct.

Branche :

`develop` → staging.

## PRODUCTION

- Vercel Production ;
- Render Production ;
- Supabase Production distinct.

Branche :

`main` → production.

## Isolation

Staging et production doivent avoir séparément :

- secrets ;
- Redis ;
- base ;
- buckets ;
- données ;
- variables d’environnement.

Ne jamais utiliser la base production comme base de test.

---

# 28. SÉCURITÉ ET CONFIDENTIALITÉ — PRINCIPES FIGÉS

- HTTPS partout ;
- Storage privé ;
- tokens anonymes hashés ;
- secrets uniquement côté serveur ;
- aucun média dans Redis ;
- original jamais modifié ;
- calcul SHA-256 immédiatement ;
- contrôles MIME/signature ;
- séparation erreurs publiques / détails privés ;
- suppression du média originale privacy-first ;
- thumbnails/copies supprimés avec l’original ;
- `public_id` non autorisant ;
- historique associé au propriétaire ;
- journalisation métier ;
- rapports immuables/hashés ;
- limiter les données sensibles renvoyées au client.

## Erreurs

Le contrat API doit utiliser des **codes d’erreur stables**.

Ne pas faire dépendre le frontend du texte humain exact d’une erreur.

Exemple d’architecture de réponse :

```json
{
  "error": {
    "code": "STABLE_MACHINE_CODE",
    "message": "Message compréhensible par l'utilisateur"
  }
}
```

Le détail fournisseur/stack trace reste serveur.

---

# 29. GESTION DES PANNES MOTEURS

Une indisponibilité d’un moteur externe ne doit pas automatiquement transformer toute l’analyse en « faux » ou « vrai ».

Chaque moteur possède son propre statut dans `analysis_engine_runs` :

- pending ;
- running ;
- completed ;
- unavailable ;
- failed ;
- not_applicable.

Le moteur de synthèse doit savoir distinguer :

- résultat obtenu ;
- moteur indisponible ;
- donnée absente ;
- moteur non applicable ;
- véritable erreur.

L’interface doit afficher une limite ou indisponibilité plutôt que fabriquer une valeur.

---

# 30. RÈGLES DE SYNTHÈSE

La synthèse ne doit pas être un simple calcul opaque de score.

Elle doit s’appuyer sur :

- données C2PA ;
- métadonnées ;
- empreintes ;
- estimation IA ;
- correspondances Web ;
- fact-checks ;
- affirmation utilisateur ;
- éléments de preuve enregistrés.

Chaque raison importante doit pouvoir être liée à `synthesis_evidence`.

Exemple :

Conclusion :

**Vérification supplémentaire recommandée**

Raisons :

- version Web antérieure trouvée ;
- date de publication antérieure à l’affirmation ;
- provenance C2PA inconnue ;
- métadonnées insuffisantes ;
- indices IA modérés.

---

# 31. DESIGN MOBILE ET SIMPLICITÉ

Le produit doit :

- fonctionner correctement sur mobile ;
- rester compréhensible pour un non-technicien ;
- montrer d’abord la synthèse ;
- permettre ensuite d’ouvrir les preuves ;
- ne pas noyer l’utilisateur dans les données brutes ;
- conserver un niveau avancé pour journalistes/professionnels.

La complexité technique doit être cachée derrière une UI lisible.

---

# 32. PRINCIPES NON NÉGOCIABLES

Toujours :

- distinguer preuve, déclaration, correspondance et estimation ;
- éviter les affirmations absolues non prouvées ;
- expliquer les résultats ;
- afficher les limites ;
- conserver la traçabilité ;
- privilégier les sources fiables ;
- être utilisable par un non-technicien ;
- tenir compte des réalités africaines ;
- fonctionner sur mobile ;
- ne pas prétendre qu’absence de C2PA = absence d’IA ;
- ne pas prétendre qu’absence d’EXIF = image IA ;
- ne pas confondre IA et désinformation ;
- ne pas créer de score unique de vérité ;
- ne pas transformer un rapport en « certificat de vérité ».

---

# 33. CONCURRENCE ET POSITIONNEMENT — CONTEXTE, PAS CODE MVP

Une première veille avait identifié notamment :

Burkina Faso :

- FasoCheck ;
- Fakipedia.

Afrique :

- Vérif’All ;
- MyAIFactChecker / FactCheckAfrica ;
- SafAI.

Europe / international :

- InVID / WeVerify ;
- vera.ai ;
- AI4TRUST ;
- C2PA / Content Credentials.

Conclusion stratégique :

**Ne jamais présenter le produit comme « le premier détecteur de fake news africain » sans preuve.**

La différenciation recherchée est :

**forensic média + provenance + contexte + explicabilité + adaptation aux réalités africaines.**

Cette veille est temporelle et devra être réactualisée avant communication publique.

---

# 34. PREMIER PLANNING HISTORIQUE

Un premier planning avait été envisagé avant la fin de la conception :

- S1 : architecture, UI, authentification, upload ;
- S2 : SHA-256, pHash, ExifTool ;
- S3 : C2PA ;
- S4 : recherche Web + Fact Check API ;
- S5 : moteur IA + synthèse ;
- S6 : rapports, dashboard, tests.

**Attention : ce planning était déclaré provisoire avant le cahier des charges final.**

Il peut servir d’indication, mais ne doit pas être considéré plus important que les dépendances techniques définitives décrites dans ce document.

---

# 35. ORDRE RECOMMANDÉ DE REPRISE DANS ANTIGRAVITY

Le projet n’ayant encore aucun code local, reprendre comme suit sans réouvrir la conception fonctionnelle.

## Étape 1 — Initialiser le monorepo / dépôt

Créer une structure claire, par exemple :

```text
forensic-media/
├── apps/
│   ├── web/
│   └── api/
├── workers/
│   └── analysis/
├── packages/
│   └── shared-contracts/
├── infra/
│   ├── docker/
│   └── scripts/
├── docs/
├── .env.example
├── docker-compose.yml
└── README.md
```

Cette arborescence est une proposition d’implémentation cohérente avec l’architecture figée ; elle n’est pas une nouvelle fonctionnalité.

## Étape 2 — Mettre en place les environnements

- Next.js 16 ;
- FastAPI ;
- PostgreSQL/Supabase ;
- Redis ;
- Celery ;
- Alembic ;
- Docker Compose ;
- `.env.example`.

## Étape 3 — Implémenter le modèle de données

Créer les migrations pour les 15 entités.

Ne pas coder les moteurs avant d’avoir :

- migrations reproductibles ;
- clés/contraintes ;
- enums ;
- relations ;
- indexes essentiels ;
- stratégie de suppression.

## Étape 4 — Auth et accès anonyme

- Supabase Auth ;
- compte utilisateur ;
- préférences ;
- token anonyme hashé ;
- contrôle d’accès centralisé.

## Étape 5 — Upload sécurisé

- validation 20 MiB ;
- MIME/signature ;
- SHA-256 immédiat ;
- pHash ;
- Storage privé ;
- `stored_objects`.

## Étape 6 — Pipeline async

- création analyse ;
- `202 Accepted` ;
- création `analysis_engine_runs` ;
- job Celery avec `analysis_id` ;
- polling `/progress`.

## Étape 7 — Moteurs locaux

D’abord :

- SHA-256 ;
- pHash ;
- ExifTool ;
- C2PA.

## Étape 8 — Adaptateurs externes

- Google Vision ;
- Fact Check API ;
- Hive AI derrière `AIProvider`.

Prévoir mocks/fakes pour tests.

## Étape 9 — Synthèse explicable

- `synthesis_results` ;
- `synthesis_evidence` ;
- mapping vers quatre indicateurs ;
- conclusion prudente.

## Étape 10 — Frontend écrans 1 à 3

- upload ;
- progress ;
- result.

## Étape 11 — Historique / compte

- historique ;
- filtres ;
- suppression ;
- préférences.

## Étape 12 — Rapports

- snapshot ;
- Jinja2 ;
- WeasyPrint ;
- SHA-256 ;
- téléchargement.

## Étape 13 — Tests et staging

- tests unitaires ;
- intégration ;
- migrations ;
- upload malformé ;
- token anonyme ;
- panne fournisseur ;
- suppression ;
- immutabilité rapport ;
- staging séparé.

---

# 36. CRITÈRES D’ACCEPTATION MVP

Le MVP n’est pas considéré fonctionnel uniquement parce qu’une page s’affiche.

## Analyse

- une image valide est acceptée ;
- une image invalide ou trop lourde est rejetée proprement ;
- SHA-256 calculé sur l’original ;
- original non modifié ;
- analyse asynchrone ;
- progression consultable ;
- aucun verdict prématuré.

## Résultat

- quatre indicateurs séparés ;
- conclusion prudente ;
- section « Pourquoi cette conclusion ? » ;
- preuves identifiables ;
- limites affichées.

## Moteurs

- panne d’un fournisseur n’efface pas les autres résultats ;
- statuts par moteur ;
- version fournisseur/moteur tracée.

## Compte

- usage anonyme possible ;
- token secret réellement requis ;
- public_id seul inutile pour l’accès ;
- compte authentifié voit uniquement ses données.

## Confidentialité

- média original supprimable ;
- miniatures/copies supprimées avec lui ;
- rapports/résultats peuvent rester sans original selon politique.

## Rapport

- snapshot immuable ;
- PDF hashé ;
- version enregistrée ;
- ancien rapport non écrasé.

## Déploiement

- staging isolé de production ;
- Redis non public ;
- Storage privé ;
- secrets absents du frontend.

---

# 37. PREMIERS TESTS À ÉCRIRE

## Upload

- JPG valide ;
- JPEG valide ;
- PNG valide ;
- WEBP valide ;
- >20 MiB ;
- extension JPG avec contenu non-image ;
- MIME mensonger ;
- image corrompue.

## Accès

- propriétaire autorisé ;
- autre utilisateur refusé ;
- token anonyme valide ;
- token invalide ;
- token expiré ;
- token révoqué ;
- public_id seul refusé.

## Pipeline

- analyse complète ;
- moteur indisponible ;
- moteur failed ;
- retry moteur ;
- synthèse avec données partielles ;
- progression sans fuite de verdict.

## Privacy

- suppression original ;
- suppression preview ;
- résultat toujours consultable si politique le permet ;
- rapport toujours vérifiable si conservé.

## Rapport

- génération ;
- hash stable pour le même artefact ;
- snapshot immuable ;
- nouvelle version ne remplace pas ancienne.

---

# 38. CONTRATS DE CODE À PRÉSERVER

Recommandation forte pour éviter le couplage :

```python
class AIProvider:
    async def analyze(self, image_ref, context): ...

class WebContextProvider:
    async def search(self, image_ref, phash, claim): ...

class FactCheckProvider:
    async def search(self, claim, web_context): ...
```

Les implémentations externes ne doivent pas contaminer les modèles domaine avec leur format brut.

Conserver les réponses brutes utiles en JSONB si nécessaire pour audit, mais convertir vers un contrat interne stable.

---

# 39. CE QU’ANTIGRAVITY NE DOIT PAS FAIRE AU DÉMARRAGE

Ne pas :

- renommer le produit définitivement ;
- choisir une autre stack juste par préférence ;
- transformer le monolithe modulaire en microservices ;
- remplacer le polling par WebSocket sans nécessité ;
- stocker les images dans Redis ;
- rendre les buckets publics ;
- ajouter vidéo/audio ;
- ajouter blockchain ;
- ajouter reconnaissance faciale ;
- ajouter une notation vérité/100 ;
- ajouter un dashboard institutionnel massif ;
- créer une API publique commerciale ;
- construire un moteur IA maison ;
- supprimer l’usage anonyme ;
- conserver l’original indéfiniment par défaut ;
- donner un verdict « vrai/faux » ;
- présenter le PDF comme une certification.

---

# 40. CONSIGNE DE DÉMARRAGE À ANTIGRAVITY

Après lecture de ce fichier, répondre d’abord avec :

1. une confirmation que le périmètre et les décisions figées sont compris ;
2. la proposition d’arborescence du dépôt ;
3. le plan des premières migrations ;
4. les variables d’environnement nécessaires ;
5. l’ordre des premiers commits.

Puis commencer l’implémentation.

Ne pas demander au porteur de projet de réexpliquer le produit.

---

# 41. PROMPT RECOMMANDÉ À ENVOYER À ANTIGRAVITY

Copier ce texte après avoir lancé `agy` dans le dossier du projet :

> Lis intégralement `FORENSIC_MEDIA_CONTEXT.md`.
>
> Ce document contient les décisions fonctionnelles et techniques déjà validées pour le projet Forensic Media / Plateforme africaine de vérification numérique.
>
> Considère toutes les décisions marquées FIGÉ comme la source de vérité du MVP.
>
> Nous avons terminé la conception fonctionnelle, le modèle de données, l’API, le choix de la stack et l’architecture de déploiement. Le point d’arrêt exact est l’architecture de déploiement Vercel + Render + Supabase avec staging et production séparés. La prochaine étape est donc l’implémentation concrète.
>
> Ne recommence pas la conception du produit. Ne change pas la stack. Ne rajoute pas de fonctionnalités hors V1.
>
> Commence par :
> 1. me confirmer ta compréhension ;
> 2. proposer l’arborescence du dépôt ;
> 3. préparer le squelette Next.js/FastAPI/Celery/Redis/Supabase ;
> 4. créer le modèle de données et les migrations ;
> 5. préparer les tests de base.
>
> Avant toute modification majeure d’une décision figée, explique clairement le problème et demande validation.

---

# 42. NOTE SUR LES ÉLÉMENTS NON RÉCUPÉRÉS MOT POUR MOT

Ce fichier consolide les décisions fonctionnelles et techniques récupérées des travaux antérieurs.

Quelques micro-détails purement syntaxiques du contrat API (notamment le chemin exact de certains endpoints de rapport) n’ont pas été récupérés mot pour mot dans l’historique disponible.

Cela **ne remet pas en cause les comportements figés** :

- rapports rattachés à une analyse ;
- création/listing/détail/téléchargement ;
- snapshot immuable ;
- idempotence ;
- hash SHA-256 ;
- autorisation propriétaire/token.

Lorsqu’un détail de chemin non explicitement écrit ici doit être choisi, appliquer une convention REST cohérente **sans modifier le comportement fonctionnel**.

---

# 43. RÉSUMÉ EXÉCUTIF ULTRA-COURT

Forensic Media est un MVP Web d’analyse d’images destiné à aider à vérifier :

1. provenance ;
2. intégrité ;
3. indices IA ;
4. contexte.

Il combine :

- C2PA ;
- ExifTool ;
- SHA-256/pHash ;
- détecteur IA remplaçable ;
- Google Vision Web Detection ;
- Google Fact Check Tools API.

Il ne donne aucun score de vérité global.

Stack :

- Next.js 16 + TypeScript + Tailwind 4 ;
- Python 3.12 + FastAPI ;
- PostgreSQL 17 / Supabase ;
- Celery 5.6 + Redis ;
- Jinja2 + WeasyPrint.

Déploiement :

- Vercel frontend ;
- Render Frankfurt API/worker/Redis ;
- Supabase Frankfurt DB/Auth/Storage ;
- staging et production séparés.

Point d’arrêt :

**tout est conçu ; il faut maintenant implémenter le MVP.**
