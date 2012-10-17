import os
import boto
import yaml
import hashlib
import smtplib
import tarfile
import subprocess
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

from boto.s3.key import Key
from boto.s3.connection import S3Connection
from boto.exception import S3ResponseError

ses_user = ""
ses_pass = ""
# This email address must be verified from AWS SES
from_email = "afgane@gmail.com"

def mail(to, subject, text, attach_files=None):
   """
   Compose and send an email using smtplib via AWS SES
   """
   msg = MIMEMultipart()

   msg['From'] = from_email
   msg['To'] = to
   recepients = to.split(',') # Allow multiple emails to be sent
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   for af in attach_files:
       try:
           with open(af, 'r') as f:
               part = MIMEBase('application', 'octet-stream')
               part.set_payload(f.read())
               Encoders.encode_base64(part)
               part.add_header('Content-Disposition',
                       'attachment; filename="%s"' % os.path.basename(af))
               msg.attach(part)
       except IOError:
           print "Error: can't open file {0}".format(af)

   mailServer = smtplib.SMTP("email-smtp.us-east-1.amazonaws.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(ses_user, ses_pass)
   mailServer.sendmail(from_email, recepients, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

def get_user_email(file_path='/mnt/transient_nfs/ghem/email.txt'):
    """
    Read the file where user's email was saved by the ghem web app JobWrapper
    class - the path provided must match the path used by JobWrapper!
    """
    with open(file_path, 'r') as f:
        address = str(f.read()).strip()
    print "Retrieved user's email from file {0} as {1}"\
        .format(file_path, address)
    return address

def get_aws_creds():
    """
    Retrieve AWS account credentials from CloudMan's user data.
    Return a tuple containing ``aws_access_key`` and ``aws_secret_key``.
    """
    cm_ud = {}
    ud_file = '/tmp/cm/userData.yaml'
    with open(ud_file) as f:
        cm_ud = yaml.load(f)
    aws_access_key = cm_ud.get('access_key', None)
    aws_secret_key = cm_ud.get('secret_key', None)
    return aws_access_key, aws_secret_key

def get_ses_creds():
    """
    AWS SES uses its own set of credentials. So, have these creds saved
    in a file in an S3 bucket and use the AWS creds from the instance
    user data to retrieve those creds so an email can be sent.
    Note that the creds used to start the instance (ie, creds in user data)
    must have access to the file in the S3 bucket for this to work.
    Furthermore, this method assumes the user data is formatted to match
    user data of CloudMan (usecloudman.org).
    """
    aws_access_key, aws_secret_key = get_aws_creds()
    # Get the creds file from the S3 bucket
    bucket_name = 'imogen-dev'
    remote_filename = 'ses_creds.yaml'
    local_file = '/mnt/transient_nfs/ghem/ses_creds.yaml'
    if aws_access_key is None or aws_secret_key is None:
        print "Could not retrieve credentials from CloudMan's user data. " \
              "Cannot retrieve SES credentials from S3 bucket; not continuing."
        return None
    try:
        s3_conn = S3Connection(aws_access_key, aws_secret_key)
        b = s3_conn.get_bucket(bucket_name)
        k = Key(b, remote_filename)
        k.get_contents_to_filename(local_file)
        print("Retrieved file '%s' from bucket '%s' to '%s'." \
              % (remote_filename, bucket_name, local_file))
    except S3ResponseError, e:
        print("Failed to get file '%s' from bucket '%s': %s" \
              % (remote_filename, bucket_name, e))
        return None

    # Extract the creds from the file
    with open(local_file, 'r') as f:
        creds = yaml.load(f)
    ses_user = creds['ses_user']
    ses_pass = creds['ses_pass']
    return ses_user, ses_pass

def store_computed_results(attach_files):
    """
    Store the ``attach_files`` as the computed results to an S3 bucket. This
    enables the same results to be retrieved instead of having to be re-computed.

    The name of the key stored in S3 is a hash based on the input values used to
    compute the results, thus providing a uniquie mappaing between the input and
    the results.
    """
    # Figure out a unique file name for the results file (based on the used input values)
    input_values_file = '/mnt/transient_nfs/ghem/user.dat'
    if os.path.exists(input_values_file):
        with open(input_values_file, 'r') as f:
            values = f.read().strip()
        values = values.replace('\n', '_')
        # Derive the actual file name based on the inputs hash
        results_hash = hashlib.md5(values).hexdigest()
        results_file_name = results_hash + '.tar.gz'

        # Create a tar file with the results
        try:
            dir_name = None
            file_names = []
            for results_file in attach_files:
                dir_name = os.path.dirname(results_file)
                file_names.append(os.path.basename(results_file))
            file_names_str = ' '.join(file_names)
            p = subprocess.call("cd {0};tar -cvzf {1} {2}"\
                .format(dir_name, results_file_name, file_names_str), shell=True)
            computed_results_file = os.path.join(dir_name, results_file_name)
        except Exception, e:
            print "Error: can't find results file {0}: {1}".format(results_file, e)

        # Upload the results file to S3
        aws_access_key, aws_secret_key = get_aws_creds()
        s3_conn = boto.connect_s3(aws_access_key, aws_secret_key)
        bucket_name = 'imogen-dev'
        b = s3_conn.get_bucket(bucket_name)
        k = Key(b, results_file_name)
        k.set_contents_from_filename(computed_results_file)
        print "Saved results file to bucket {0} as key {1}".format(bucket_name, k.name)
    else:
        print "Not saving computed results because cannot find the input data "\
              "values file {0}".format(input_values_file)

ses_user, ses_pass = get_ses_creds()
results_files = ['/mnt/transient_nfs/ghem/csoil-1861.png',
                '/mnt/transient_nfs/ghem/csoil-2099.png',
                '/mnt/transient_nfs/ghem/npp-1861.png',
                '/mnt/transient_nfs/ghem/npp-2099.png']
attach_files = []
for af in results_files:
    if os.path.exists(af):
        attach_files.append(af)
    else:
        print "Results file {0} not found; not including this file."\
            .format(af)
store_computed_results(attach_files)
mail(to=get_user_email(),
   subject="Your IMOGEN portal results",
   text="Attached to this message are the results of the run you submitted "
    "to the IMOGEN portal on the AWS cloud.",
   attach_files=attach_files)

