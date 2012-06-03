#!/bin/bash
set -e
LOGFILE=/tmp/log/gunicorn/ghem.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=2
# user/group to run as
USER=ubuntu
GROUP=ubuntu
# The following will be put in place by CloudMan @ runtime
export SGE_ROOT=/opt/sge
export DRMAA_LIBRARY_PATH=/opt/sge/lib/lx24-amd64/libdrmaa.so.1.0
# This assumes we cloned the source into the following dir
cd /home/ubuntu/weather/ghem
# Always update the code from the repo on service start
git pull
# Activate the virtual env
source ../bin/activate
# Update any new libs that might have been added to requirements.txt
pip install -r requirements.txt
# Setup the log file & permissions
test -d $LOGDIR || mkdir -p $LOGDIR
test -e $LOGFILE || touch $LOGFILE
chown -R $USER:$USER $LOGDIR
# Start the web app as a gunicorn-managed wsgi app
exec ../bin/gunicorn ghem.wsgi:application \
  -w $NUM_WORKERS \
  --user=$USER --group=$GROUP --log-level=debug \
  --log-file=$LOGFILE 2>>$LOGFILE \
  -b localhost:8080