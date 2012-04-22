import logging
log = logging.getLogger(__name__)

class JobWrapper(object):
    def __init__(self, job_form_data):
        self.job_form_data = job_form_data
        self.command_line = None
    
