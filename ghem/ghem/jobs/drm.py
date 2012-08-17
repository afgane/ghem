import os
import drmaa

import logging
log = logging.getLogger(__name__)

# TODO: Add email option and configure the system to send the email
drm_template = """#!/bin/sh
#$ -S /bin/sh

cd {run_path}

# Use this file as a flag to indicate when this run has completed
DONE_FILE=/tmp/imogen_run/{id}.done
RUNDIR=$(dirname $DONE_FILE)
LOG_FILE="{log_dir}/{id}.log"

# Initialize CloudMan and setup cluster size
echo "GCM {id} initializing CloudMan" > $LOG_FILE
python /home/ubuntu/weather/ghem/ghem/init_cm.py

# Test if run progress dir exists or create it
test -d $RUNDIR || mkdir -p $RUNDIR

# Invoke the model code w/ the appropriate input file
echo "GCM {id} starting at `date`" >> $LOG_FILE
./jules_fast.exe < 22GCM/{input_dir}/input.jin

# Create a file indicating the model ran
echo "GCM {id} completed at `date`" >> $LOG_FILE
touch $DONE_FILE

# Check if all other scripts ran. If so, generate the results
# plot and email the plot to the user
num_done=`ls $RUNDIR/*.done | wc -l`
# There are 22 models but the above command will count '.' and '..'
# directories so include those in the calculation
if [ $num_done -eq 22 ]; then
    echo "GCM {id} finished last; generating the plot" >> $LOG_FILE
    cd GRADSPLOT/
    ./test-ensemble.sh >> $LOGFILE 2>&1

    # Email the generated plot to the user
    echo "GCM {id} sending the email" >> $LOG_FILE
    python /home/ubuntu/weather/ghem/ghem/send_email.py >> $LOG_FILE

    # Terminate the cluster
    # TODO python /home/ubuntu/weather/ghem/ghem/terminate_cm.py
else
    echo "GCM {id} not last; currently $num_done completed" >> $LOG_FILE
fi
"""

# A list of the names of the directories where the models inputs are
gcm_dirs = [
    'bccr_bcm2_0_rel',
    'cccma_cgcm3_1_rel',
    'cnrm_cm3_rel',
    'csiro_mk_3_0_rel',
    'csiro_mk_3_5_rel',
    'gfdl_cm2_0_rel',
    'gfdl_cm2_1_rel',
    'giss_e_h_rel',
    'giss_e_r_rel',
    'iap_fgoals1_0_g_rel',
    'ingv_echam4_rel',
    'inmcm3_0_rel',
    'ipsl_cm4_rel',
    'miroc3_2_hires_rel',
    'miroc3_2_medres_rel',
    'miub_echo_g_rel',
    'mpi_echam5_rel',
    'mri_cgcm2_3_2a_rel',
    'ncar_ccsm3_0_rel',
    'ncar_pcm1_rel',
    'ukmo_hadcm3_rel',
    'ukmo_hadgem1_rel'
]

class DRMAAJobRunner(object):
    def __init__(self):
        self.ds = drmaa.Session()
        self.jobs_working_dir = "/var/opt/IMOGEN/jobs_working_dir"
        if not os.path.exists(self.jobs_working_dir):
            os.mkdir(self.jobs_working_dir)
        try:
            # Make sure we're starting with a clear session
            self.ds.exit()
        except drmaa.NoActiveSessionException:
            pass
        self.ds.initialize()

    def queue_job(self, job_wrapper):
        # Prepare the job
        # try:
        #     cmd_line = self.build_command_line(job_wrapper)
        # except Exception, e:
        #     log.error("Failure preparing job: {0}".format(e))
        #     return False

        # Iterate through the gcm_dirs and submit each as a separate job
        for i, input_dir in enumerate(gcm_dirs):
            # Define job attributes
            ofile = os.path.join(self.jobs_working_dir,
                "run_{0}.out".format(i))
            efile = os.path.join(self.jobs_working_dir,
                "run_{0}.err".format(i))
            jt = self.ds.createJobTemplate()
            jt.remoteCommand = os.path.join(self.jobs_working_dir,
                "run_{0}.sh".format(i))
            jt.outputPath = ":{0}".format(ofile)
            jt.errorPath = ":{0}".format(efile)

            script = drm_template.format(run_path=job_wrapper.run_path,
                id=i, input_dir=input_dir, log_dir=self.jobs_working_dir)
            with open(jt.remoteCommand, 'w') as sf:
                sf.write(script)
            os.chmod(jt.remoteCommand, 0750)

            # Submit the job
            log.debug("Submitting job script at {0}".format(jt.remoteCommand))
            job_id = self.ds.runJob(jt)
            log.info("Job queued as {0}".format(job_id))

            # Delete the job template
            self.ds.deleteJobTemplate(jt)

        # Close DRMAA Session
        self.ds.exit()

        return True

    def build_command_line(self, job_wrapper):
        """ Compose the command line that will be submitted to the DRM
        """
        # job_wrapper.command_line = "date; hostname -i" # Sample CL
        job_wrapper.command_line = "sh start.sh"
        return job_wrapper.command_line

