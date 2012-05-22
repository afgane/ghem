### Running the server during development

To run this [Django][1] application locally, start by installing 
Python and [virtualenv][2]. When developing locally,
build a local virtualenv, install the dependencies and start the server:

    $ cd <project root dir>
    $ git clone https://github.com/afgane/ghem.git
    $ virtualenv .
    $ source bin/activate
    $ pip install -r ghem/requirements.txt
    $ python ghem/ghem/manage.py runserver

### Production deployment

To deploy this app on an machine (e.g., cloud image), have it run behind a
web proxy (e.g., [nginx][3]), and start at machine boot, do the following (also
do all of the above steps excluding the one where the development server is
started):

1. Place nginx.conf in *?/nginx/conf/.* directory
1. Make sure nginx starts at instance boot (already happens for CloudMan images)
1. Place *ghem_upstart.conf* in */etc/init* (test that the service invocation works
    with: *service ghem_upstart start*)
1. Clean up and bundle the image

[1]: https://www.djangoproject.com/
[2]: https://github.com/pypa/virtualenv
[3]: http://wiki.nginx.org/Main