### Deployment

To run this [Django][1] application locally, start by installing 
Python and [virtualenv][2]. When developing locally,
build a local virtualenv, install the dependencies and start the server:

    $ cd <project root dir>
    $ git clone https://github.com/afgane/ghem.git
    $ virtualenv .
    $ source bin/activate
    $ pip install -r ghem/requirements.txt
    $ python ghem/ghem/manage.py runserver

[1]: https://www.djangoproject.com/
[2]: https://github.com/pypa/virtualenv
