"""
Terminate and delete the instance of CloudMan running on this instance. This
also includes terminating the instance itself.
"""
import os
import sys
import yaml
from blend.cloudman import CloudMan

# Setup logging
import logging
log = logging.getLogger('terminate_cm')
hdlr = logging.FileHandler('/mnt/transient_nfs/ghem/manipulate_cm.log')
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
    cm_pwd = ud.get('password', '')
except Exception, e:
    log.error("Error reading user data file {0}: {1}".format(ud_file, e))
    sys.exit(1)
# Get a handle to CloudMan and terminate the cluster
cm = CloudMan('http://127.0.0.1:42284/', cm_pwd)
log.debug("Initiating termination and deletion of this cluster")
cm.terminate(terminate_master_instance=True, delete_cluster=True)
