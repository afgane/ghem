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
web proxy (*e.g.,* [nginx][3]), and start at machine boot, do the following steps. By default, scripts included in the repository assume the code is cloned to (*i.e.,* the project root directory is) ``/home/ubuntu/weather``

1. Do all of the above above steps excluding starting the development server
1. Place ``nginx.conf`` in ``?/nginx/conf/.`` directory
1. Make sure ``nginx`` starts at instance boot (already happens for CloudMan images)
1. Place ``ghem_upstart.conf`` in ``/etc/init`` (to test that the service invocation works,
    make sure ``nginx`` is running and then start the service with: ``service ghem_upstart start``)
1. Clean up and bundle the image (if using [CloudBioLinux][4] scripts, this can be done with the
    following command: ``fab -f fabfile.py -u ubuntu -i [key] -H [ip] install_biolinux:target=cleanup``)

### Logging and debugging

The default location for the source of the Django app is 
``/home/ubuntu/weather``. The app starts up via an Upstart job
and runs ``run_gunicorn.sh`` from the source repo.

The location of the log file for the Django app is specified in
``run_gunicorn.sh`` file (defaults to ``/tmp/log/gunicorn/ghem.log``).

All of the models to be run are stored in ``/var/opt/IMOGEN/``

The locations of CloudMan log files, which is used to orchestrate the setup of the system, are in the the following locations:

1. /opt/cloudman/pkg/ec2autorun.log
1. /tmp/cm/cm_boot.log
1. /mnt/cm/paster.log

[1]: https://www.djangoproject.com/
[2]: https://github.com/pypa/virtualenv
[3]: http://wiki.nginx.org/Main
[4]: http://cloudbiolinux.org/
