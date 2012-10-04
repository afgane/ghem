import os
import yaml
import smtplib
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
   mailServer.sendmail(from_email, to, msg.as_string())
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
    # Get S3 bucket creds from CloudMan's user data
    cm_ud = {}
    ud_file = '/tmp/cm/userData.yaml'
    with open(ud_file) as f:
        cm_ud = yaml.load(f)
    aws_access_key = cm_ud.get('access_key', None)
    aws_secret_key = cm_ud.get('secret_key', None)

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

ses_user, ses_pass = get_ses_creds()
attach_files = ['/mnt/transient_nfs/ghem/out1.jpg',
                '/mnt/transient_nfs/ghem/out2.jpg',
                '/mnt/transient_nfs/ghem/out3.jpg',
                '/mnt/transient_nfs/ghem/out4.jpg',
                '/mnt/transient_nfs/ghem/out5.jpg',
                '/mnt/transient_nfs/ghem/out6.jpg']
for af in attach_files:
    if not os.path.exists(af):
        print "Results file {0} not found. Not attaching the file to the email."\
            .format(af)
        attach_files.remove(af)
mail(to=get_user_email(),
   subject="Your IMOGEN portal results",
   text="Attached to this message are the results of the run you submitted "
    "to the IMOGEN portal on the AWS cloud.",
   attach_files=attach_files)

