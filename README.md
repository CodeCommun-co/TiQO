# Qonto-to-Odoo
Qonto Connect to Odoo


## Requirements :

Poetry : https://python-poetry.org/docs/  

```shell
curl -sSL https://install.python-poetry.org | python3 -
```


## Installation

### Docker

```shell
# Build et run
docker compose up -d
# Create super user
docker compose run tiqo poetry run ./manage.py createsuperuser
```

Go to http://localhost:8005/admin

### From SCRATCH : 

```shell
git clone git@github.com:CodeCommun-co/Qonto-to-Odoo
cd Qonto-to-Odoo.git
poetry install
poetry shell
cd QontoOdooDJango
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver_plus
```


# Qonto X Odoo : TiQO ? 

## En deux mots : 

Créer un outil pour simplifier le budget et la gestion comptable à la Raffinerie dans un monde transparent et multi pôle.

Nom de code : TiQO (peut être changé hein ^-^)

## Idées générales

Discussion préliminaire : <https://chat.communecter.org/channel/lesOutilsNumeriquesDeLaRaffinerie?msg=PX2xtwQEa53hQqFBf>


## CE QUI EST OK :

* Récupère tous les labels Qonto et les lie avec : 
  * Article
  * Compte
  * Journal
  * Compte Analytique
* Récupère toutes les transactions, les membres et bénéficiaires Qonto
  * Génère une facture en brouillon sur Odoo avec : 
    * Articles =  Article lié au label Qonto
    * Client = Contact lié à la transaction
    * Comptes ( si non renseigné, compte Article par defaut )
    * Journal = Facture Client 
    * Libéllé = Qonto Label
    * Qty = 1
    * Taxes = Tva Collectée (vente) renseigné sur Qonto

      

## UTILISATION 

### Odoo : 

* Installer le module TiBillet pour Odoo : 
  * <https://github.com/TiBillet/TiBillet-Odoo-module>
* Activer le mode développeur et générer une clé API

### Qonto : 

* Créer une clé API Qonto

### TiQO

Suivre les instructions d’installation sur <https://github.com/CodeCommun-co/Qonto-to-Odoo>

* Aller sur localhost:8000/admin
* Dans “Configuration”, remplir les clé api Odoo et Qonto
* Dans “Contacts Qonto”, mettre a jour les contacts Qonto et Odoo à l’aide des boutons “Refresh”
  * Lier les utilisateurs. Deux façon de faire : 
    * Soit Selectionner dans la liste des Odoo Contact ( l’email sera rempli automatiquement une fois sauvegardé )
    * Soit remplir l’email manquant, selectionner les lignes, puis dans “Action” → “Envoyer dans Odoo” : Cela créera et liera le contact dans Odoo
* Dans “Labels Qonto”, cliquez sur tout les refresh un par un ( je ferais un bouton pour tous a l’avenir, les séparer est trés utile en phase de dev ^^ )
  * Au dernier bouton, les labels Qonto apparaissent ! Vous pouvez alors les lier avec les articles Odoo. Seul l'article est obligatoire. Renseignez les autres comptes si vous souhaitez remplacer la valeur par defaut de l'article.
* Dans “Transaction Qonto”, lancez la procédure de refresh. Si la transaction n’a pas déja été renseignée, elle est ajoutée. Vous pouvez classer les entrées avec les filtres à droite.
  * Pour modifier les informations, vous pouvez cliquer sur le libéllé.
  * Les initiateurs / bénéficiaires sont entré uniquement si l’info existe sur Qonto. Il le sont presque systématique pour les débit. Rarement pour les crédits ( aucunes informations a collecter via l’API )
* Pour créer une facture avec les information de transactions, vous pouvez selectionner une ou plusieurs ligne et choisir l’action “Create Draft Invoice” → go.  S’il manque des information, le système vous renseignera.


La pièce jointe Qonto est alors associée à la facture Odoo. Cliquez sur le petit trombone dans Odoo pour la voir.



Enjoy !


## ROADMAP

* Sur la banque Qonto :
  * Encourager la gestion multi utilisateur et les cartes virtuelles pour la gestion financière des poles/groupes de la Raff’
  * Via l’API Qonto : 
    * ==OK==: Récolter les “tag” associables à chaque transactions réalisées par les poles/groupes
    * ==OK==: Récupérer les informations et les documents justificatif (Facture, tickets, PDF) liés à chaque transaction

      \
* Sur Odoo : 
  * Enregistrer chaque transactions et factures venant de Qonto : 

    1)  ==OK==: get_or_create le partner : res.partner

    \
    2) Créer une facture (account.move) avec les champs suivants : 
    * ==OK==:partner_id (nom du partenaire) 
      * ==QUESTION==: Qui est le partner_id lors d’un paiement par carte bancaire ? Nous n’avons qu’un bête string dans Qonto, du genre “SAS LEROY MERLIN”. Pas de mail, on créé quand même un partner id ?
        * ==REPONSE== il faut créer un partner-id si il n’existe pas déjà sur odoo, car sinon ça risque de créer plusieurs fournisseurs avec le même nom `Ok, ça sera une action manuelle alors. Je rajoute ça.`

          \
    * ref (numéro de facture fournisseur)
    * ==OK==: PDF attachement de Qonto lié à la facture en pièce jointe (ir.attachment)
    * payment_reference (référence du paiement - c’est le numéro de la facture fournisseur ~~facultatif je pense dans le cas d’un paiement Qonto - utile pour un paiement par chèque)~~
    * ==OK==: invoice_date (date de facturation)
    * ==OK==: journal_id = “Factures fournisseurs” (nom du journal tel que paramètré dans compta.laraffinerie.re)
    * ==OK==: product_id (article)
      * ==QUESTION:== Pas d’articles dans la ligne Qonto. On a parfois une description, si la personne l’a mise. Sinon juste “SAS LEROY MERLIN”
        * ==REPONSE== l’article est assez important car il conditionne sur odoo le code comptable associé à l’achat et permettra par la suite de classer les achats par type. Par contre je sais pas si qonto à quelque chose d’équivalent. `Ok, on va lier l’article à la transaction Qonto. J’ai peur qu’il faille le faire à la main, du coup. Si tu vois une façon de l’automatiser, tu me diras.`  

          \
    * ==OK==: analytic_account_id (compte analytique) ( <https://nuage.tierslieux.re/apps/onlyoffice/1694407?filePath=%2FLa%20Raffinerie%20(2)%2FGroupe%20Les%20Communs%2Finter-admin%2Fcomptes%20analytiques%20fev%2023.xlsx> )

      \
    * ==OK==: quantity = 1 (par défaut)
    * ==OK==: price_unit (montant)
    * le suivi des étapes de facturation
      * le nom de la personne qui a validé la dépense **(engagement)**
      * le nom de la personne qui a validé que l'achat ou la prestation a bien été faite **(liquidation)**
      * le nom de la personne qui saisi la facture **(enregistrement)** 
      * le nom de la personnes qui paye la facture **(paiement)**

      \

  3) Enregistrer un paiement Qonto
  * Lister : 
    * ==OK==: Les journaux (account.journal) (Ici un seul journal = Qonto)
    * ==OK==:Les articles 
    * ==OK==: Les comptes analytiques

      \


* Sur l’interface TiQO
  * ==OK==: Liaison entre les tag Qonto et les journaux / comptes analytiques Odoo
  * ==OK:== Lier les contacts Odoo et les bénéficiaires Qonto
  * Classer les dépenses dans un tableau par groupe/pole/articles
  * Ajouter input “Prévisionnel” pour une vision de la progression des dépenses par articles / pôles / groupes
  * ==OK==:Chaque transactions Qonto doit être validée par un admin pour être poussée vers Odoo


## Dépôt GIT :

<https://github.com/CodeCommun-co/Qonto-to-Odoo> 

Sous licence libre GPLv3

## Stack technique : 

* Api Qonto V2
* Odoo 15
  * Api xmlrpc
* Django 4
* Docker et compose


## Futur : 

* Rentrer les factures directement depuis TiQO → remplissage auto vers Qonto et Odoo
* Aller vers [Schema Julien : Gestion de projet](https://notes.laraffinerie.re/doc/schema-julien-gestion-de-projet-CsYEysK8RW)
* Remplacer : <https://nuage.tierslieux.re/apps/onlyoffice/1709798?filePath=%2FLa%20Raffinerie%20(2)%2FGroupe%20Micro-Recylerie%2FTableau%20de%20bord%20groupe%20micro-recylerie%20.xlsx>



## Financements : 

Raffinerie : 1 000 € (5 Jours de co-rem : Budget Outils numérique )

Coopérative TiBillet : 1 000 € (5 Jours de dev)
