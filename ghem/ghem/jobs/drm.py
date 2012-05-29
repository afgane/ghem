import os
import drmaa

import logging
log = logging.getLogger(__name__)

# TODO: Add email option and configure the system to send the email
drm_template = """#!/bin/sh
#$ -S /bin/sh
cd {path}
{cmd}
"""

class DRMAAJobRunner(object):
    def __init__(self):
        self.ds = drmaa.Session()
        try:
            # Make sure we're starting with a clear session
            self.ds.exit()
        except drmaa.NoActiveSessionException:
            pass
        self.ds.initialize()
    
    def queue_job(self, job_wrapper):
        # Prepare the job
        try:
            cmd_line = self.build_command_line(job_wrapper)
        except Exception, e:
            log.error("Failure preparing job: {0}".format(e))
            return False
        
        # Define job attributes
        ofile = os.path.join(job_wrapper.run_path, "run.out")
        efile = os.path.join(job_wrapper.run_path, "run.err")
        jt = self.ds.createJobTemplate()
        jt.remoteCommand = os.path.join(job_wrapper.run_path, "run.sh")
        jt.outputPath = ":{0}".format(ofile)
        jt.errorPath = ":{0}".format(efile)
        
        script = drm_template.format(path=job_wrapper.run_path, cmd=cmd_line)
        with open(jt.remoteCommand, 'w') as sf:
            sf.write(script)
        os.chmod(jt.remoteCommand, 0750)
        
        # Submit the job
        log.debug("Submitting job script at {0}".format(jt.remoteCommand))
        log.debug("Job command is {0}".format(cmd_line))
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
    
