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
hdlr = logging.FileHandler('/tmp/init_cm.log')
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
# Do the work only if we're running on the master instance
# FIXME: more than 1 job can end up on master - need another method!
if role == 'master':
    # Initialize CloudMan now
    cm = CloudMan('http://127.0.0.1:42284/', cm_pwd)
    log.debug("Initializing CloudMan to type SGE")
    cm.initialize(type='SGE')
    log.debug("Scaling the size of CloudMan cluster")
    # TODO: Add enough nodes to enable the 22 models to run in parallel
