import os
import errno
import shutil
import logging
log = logging.getLogger(__name__)

class JobWrapper(object):
    def __init__(self, job_form_data):
        self.job_form_data = job_form_data
        self.user_email = self.job_form_data.get('email', None)
        self.store_user_email()
        self.command_line = None
        self.run_path = "/var/opt/IMOGEN"
        if not os.path.exists(self.run_path):
            os.mkdir(self.run_path)

    def create_data_file(self, file_path='/var/opt/IMOGEN/EMITS/user.dat'):
        """
        Create the input data file from form data and save it to a file
        specified via ``file_path``. Only the form values are stored and they
        are stored in one value per line.

        If the value of ``file_path`` is changed from the default, must also
        change the corresponding copy line in the generated SGE script in drm.py
        """
        values = []
        for yr in range(10, 100, 10): # we're skipping the first decade since it's history
            values.append(str(self.job_form_data.get('yr20{0}'.format(yr), 0)))
        with open(file_path, 'w') as f:
            f.write('\n'.join(values))
        # Make sure the input data file exists on the NFS and in the dir where
        # the models expect it
        nfs_file_path = '/mnt/transient_nfs/ghem/user.dat'
        shutil.copy (file_path, nfs_file_path)

    def store_user_email(self, file_path='/mnt/transient_nfs/ghem/email.txt'):
        """
        Store the email address provided by the user to a text file.
        """
        dirname = os.path.dirname(file_path)
        try:
            os.makedirs(dirname)
        except OSError as ex:
            if ex.errno == errno.EEXIST:
                pass
            else:
                log.error("Cannot create directory for email {0}: {1}"\
                        .format(dirname, ex))
        with open(file_path, 'w') as f:
            f.write(self.user_email)

