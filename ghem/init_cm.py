"""
Connect to and initialize the instance of CloudMan running on this instance
"""
import os
import sys
import yaml
import math
import subprocess
from blend.cloudman import CloudMan

# Setup logging
import logging
log = logging.getLogger('init_cm')
hdlr = logging.FileHandler('/mnt/transient_nfs/ghem/manipulate_cm.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)

# Get the public IP address of this instance for ID purposes in the log
process = subprocess.Popen(['curl', 'http://169.254.169.254/latest/meta-data/public-ipv4'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ip, err = process.communicate()
# Get CloudMan password from the user data file
ud = {}
try:
    ud_file = '/tmp/cm/userData.yaml'
    with open(ud_file, 'r') as f:
        ud = yaml.load(f)
    role = ud.get('role', '')
    cm_pwd = ud.get('password', '')
except Exception, e:
    log.error("[{2}] Error reading user data file {0}: {1}".format(ud_file, e, ip))
    sys.exit(1)
# Initialize CM only on the master node. This assumes the master is:
#  1. Running jobs
#  2. Runs the very first job
if role == 'master':
    # Initialize CloudMan if not already initialized
    cm = CloudMan('http://127.0.0.1:42284/', cm_pwd)
    cm_type = cm.get_cluster_type()
    log.debug("[{0}] Current CloudMan type: '{1}'".format(ip, cm_type))
    if cm_type == '' or cm_type is None:
        log.debug("[{0}] Initializing CloudMan to type 'SGE'".format(ip))
        cm.initialize(type='SGE')
        # Enable autoscaling with sufficient cluster size limits to enable the
        # 22 models to run in parallel
        # Get the number of cores on this machine to set autoscaling appropriately
        process = subprocess.Popen(['grep', '-c', 'processor', '/proc/cpuinfo'],
                stdout=subprocess.PIPE)
        out, err = process.communicate()
        try:
            # We need an integer big enough to accomodate running all 22 models in parallel
            as_max = int(math.ceil(22.0/int(out.strip())))
            log.debug("[{0}] Setting CloudMan auto-scaling limits to 0 and {1}".format(ip, as_max))
            cm.enable_autoscaling(0, as_max)
        except Exception:
            # Default to large instance type w/ 4 cores per worker
            log.error("[{0}] Had trouble getting the number of cores on this instance. "\
                "Assuming 'Large' instance type and setting auto-scaling limits to 0-6"\
                .format(ip))
            cm.enable_autoscaling(0, 6)
    else:
        log.debug("[{0}] CloudMan already setup; didn't do anything.".format(ip))
else:
    log.debug("[{0}] Worker job; not attempting to initialize CloudMan".format(ip))
