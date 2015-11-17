===============================
xgs_performance_prototype
===============================


Requirements
------------
- python 3
- mongodb
- sass (for flask assets)

Quickstart
----------

Checkout this repo.

Then run the following commands to bootstrap your environment.

```
mkvirtualenv --python=/path/to/python3 [appname]
```

Install python requirements.
```
pip install -r requirements/dev.txt
```

Environment variables for running application locally are in environment.sh

Once that this all done you can:

Start mongo:
```
mongod
```

Then run app
```
./run.sh
```

Deployment
----------

In your production environment, make sure the ``SETTINGS`` environment variable is set to ``config.Config``.


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
Type in any old password it isn't used at the moment

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
