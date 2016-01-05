===============================
Civil Service Digital Prototype
===============================

[![Build Status](https://travis-ci.org/crossgovernmentservices/csdigital-prototype.svg)](https://travis-ci.org/crossgovernmentservices/csdigital-prototype)

Requirements
------------
- python 3
- mongodb
- sass (for flask assets)
- virtualenv and virtualenvwrapper (not a hard requirement but steps below assume you are using them)

Quickstart
----------

Checkout this repo.

Install the requirements above if you don't already have them installed.

Then run the following commands to bootstrap your environment.

```
mkvirtualenv --python=/path/to/python3 [appname]
```
Change to the directory you checked out and install python requirements.

```
pip install -r requirements.txt
```

The base environment variables for running application locally are in environment.sh. See below for any private environment variables.

Once that this all done you can:

Start mongo:
```
mongod
```

Then run app
```
./run.sh
```

Tests
----------

Make sure mongo is running

```
make test
```

Deployment
----------

In your production environment, make sure the ``SETTINGS`` environment variable is set to ``config.Config``.


Private environment variables
---------------------

Anything that is not sensitive and can go in version control can be put into
environment.sh. For anything private, add a file called environment-private.sh (which is git ignored) and put the variables in that file.


Adding data - a.k.a. management commands
----------------------------------------

To run any of these locally first source environment.sh

```
source environment.sh
```

Create all xgs users
```
python manage.py create-xgs-users
```

Create an ordinary (non admin user)
```
python manage.py create-user
```
Answer prompts - (note password not used yet)

Add an objective for a user
```
python manage.py add-user-objective
```
Answer prompt for email of user to add objective for.

#### To reset
With mongo running log into mongo

Switch dbs
```
use xgs
```
Remove everything
```
db.dropDatabase()
```
Then add everything with management commands as above
