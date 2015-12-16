===============================
Civil Service Digital Prototype
===============================

[![Build Status](https://travis-ci.org/crossgovernmentservices/csdigital-prototype.svg)](https://travis-ci.org/crossgovernmentservices/csdigital-prototype)

Requirements
------------
- python 3
- mongodb
- sass (for flask assets)

Quickstart
----------

Checkout this repo.

```
* If you don't have Python3 installed, then go to python.org/downloads and get the latest version.
* If you don't have mongodb running, you will need "Brew" set up to install it. Go to http://brew.sh/, open a terminal window and type in the shell command there.
* Now open a new Terminal window and type "brew install mongodb"
* Start mongoDB  with the command at the end of the install. "launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist" - this window won't return to the command prompt - it's now running mongoDB until you ctrl-C it.
* In your other window type "sudo gem install sass"
```

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


Tests
----------

Make sure mongo is running

```
make test
```

Deployment
----------

In your production environment, make sure the ``SETTINGS`` environment variable is set to ``config.Config``.


Environment variables
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

#### To reset
With mongo running log into mongo

Switch dbs
```
use xgs
```
Remove everything
```
db.user.remove({})
```
Then add everything with management commands as above
