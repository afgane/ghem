import logging
log = logging.getLogger(__name__)

class JobWrapper(object):
    def __init__(self, job_form_data):
        self.job_form_data = job_form_data
        self.user_email = self.job_form_data.get('email', None)
        self.command_line = None
        self.run_path = "/var/opt/IMOGEN"
    
    def create_data_file(self, file_path='/var/opt/IMOGEN/EMITS/user.dat'):
        """
        Create the input data file from form data and save it to a file
        specified via file_path. Only the form values are stored and they
        are stored in one value per line.
        """
        values = []
        for yr in range(10, 100, 10): # we're skipping the first decade since it's history
            values.append(str(self.job_form_data.get('yr20{0}'.format(yr), 0)))
        with open(file_path, 'w') as f:
            f.write('\n'.join(values))
    
