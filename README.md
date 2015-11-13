===============================
xgs_performance_prototype
===============================


Requirements
------------
python 3
mongodb

Quickstart
----------

Then run the following commands to bootstrap your environment.

```
mkvirtualenv --python=/path/to/required/python/version [appname]
```

Install python requirements.
```
pip install -r requirements/dev.txt
```

Set some environment variables. The following is required. Add as needed.

```
export SETTINGS='config.DevelopmentConfig'
```

Once that this all done you can:

```
python manage.py server
```

Deployment
----------

In your production environment, make sure the ``SETTINGS`` environment variable is set to ``config.Config``.


Adding data - a.k.a. management commands
----------------------------------------

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
