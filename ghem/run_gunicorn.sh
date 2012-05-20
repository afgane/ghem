#!/bin/bash
set -e
LOGFILE=/tmp/log/gunicorn/ghem.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=2
# user/group to run as
USER=ubuntu
GROUP=ubuntu
# This assumes we cloned the source into the following dir
cd /home/ubuntu/weather/ghem/ghem
source ../../bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR
exec ../../bin/gunicorn ghem.wsgi:application \
  -w $NUM_WORKERS \
  --user=$USER --group=$GROUP --log-level=debug \
  --log-file=$LOGFILE 2>>$LOGFILE \
  -b localhost:8080