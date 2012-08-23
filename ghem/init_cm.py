"""
Connect to and initialize the instance of CloudMan running on this instance
"""
import os
import sys
import yaml
from blend.cloudman import CloudMan

# Setup logging
import logging
log = logging.getLogger('init_cm')
hdlr = logging.FileHandler('/tmp/log/gunicorn/manipulate_cm.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)

# Get CloudMan password from the user data file
ud = {}
try:
    ud_file = '/tmp/cm/userData.yaml'
    with open(ud_file, 'r') as f:
        ud = yaml.load(f)
    role = ud.get('role', 'master')
    cm_pwd = ud.get('password', '')
except Exception, e:
    log.error("Error reading user data file {0}: {1}".format(ud_file, e))
    sys.exit(1)
# Initialize CloudMan if not already initialized
cm = CloudMan('http://127.0.0.1:42284/', cm_pwd)
cm_type = cm.get_cluster_type()
log.debug("\nCurrent CloudMan type: '{0}'".format(cm_type))
if cm_type == '' or cm_type is None:
    log.debug("Initializing CloudMan to type 'SGE'")
    cm.initialize(type='SGE')
    log.debug("Scaling the size of CloudMan cluster")
    # Enable autoscaling with sufficient cluster size limits to enable the
    # 22 models to run in parallel (assuming Large instance types w/ 4 CPUs)
    cm.enable_autoscaling(0, 7)
else:
    log.debug("CloudMan already setup; didn't do anything.")
