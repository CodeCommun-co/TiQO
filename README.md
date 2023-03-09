# Qonto-to-Odoo
Qonto Connect to Odoo


## Requirements :

Poetry : https://python-poetry.org/docs/  

```shell
curl -sSL https://install.python-poetry.org | python3 -
```


## Installation

```shell
git clone git@github.com:CodeCommun-co/Qonto-to-Odoo.git
cd Qonto-to-Odoo.git
poetry install
poetry shell
cd QontoOdooDJango
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver_plus
```
