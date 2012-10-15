"""Base views.
"""
import os
import boto
import yaml
import hashlib
import logging
import tarfile
import subprocess

from django.http import HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.shortcuts import render

from ghem.jobs import JobWrapper
from ghem.jobs.drm import DRMAAJobRunner

log = logging.getLogger(__name__)

class RunModelForm(forms.Form):
    """Details needed to boot a setup and boot a CloudMan instance.
    """
    textbox_size = "input_xlarge"
    yr2000 = forms.DecimalField(required=True,
                label="2000 - 2009 (GtC/yr)",
                initial="9.37",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "readonly": "readonly",
                    "title": "This value cannot be changed"}))
    yr2010 = forms.DecimalField(required=True,
                label="2010 - 2019 (GtC/yr)",
                initial="10.81",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 1}))
    yr2020 = forms.DecimalField(required=True,
                label="2020 - 2029 (GtC/yr)",
                initial="12.18",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 2}))
    yr2030 = forms.DecimalField(required=True,
                label="2030 - 2039 (GtC/yr)",
                initial="13.17",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 3}))
    yr2040 = forms.DecimalField(required=True,
                label="2040 - 2049 (GtC/yr)",
                initial="14.10",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 4}))
    yr2050 = forms.DecimalField(required=True,
                label="2050 - 2059 (GtC/yr)",
                initial="15.18",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 5}))
    yr2060 = forms.DecimalField(required=True,
                label="2060 - 2069 (GtC/yr)",
                initial="16.39",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 6}))
    yr2070 = forms.DecimalField(required=True,
                label="2070 - 2079 (GtC/yr)",
                initial="17.59",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 7}))
    yr2080 = forms.DecimalField(required=True,
                label="2080 - 2089 (GtC/yr)",
                initial="18.79",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 8}))
    yr2090 = forms.DecimalField(required=True,
                label="2090 - 2099 (GtC/yr)",
                initial="20.00",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size, "tabindex": 9}))
    email = forms.CharField(required=True,
                widget=forms.TextInput(attrs={"class": 'input_xxlarge', "tabindex": 10}))


def run(request):
    if request.method == "POST":
        form = RunModelForm(request.POST)
        if form.is_valid():
            # Store the form data into a session object
            request.session["job_form_data"] = form.cleaned_data
            if run_models(request):
                return HttpResponseRedirect("/thankyou.html")
            else:
                form.non_field_errors = "Problem running the models"
    else:
        form = RunModelForm()
    return render(request, "run.html", {"form": form},
        context_instance=RequestContext(request))

def run_models(request):
    """
    Submit the models with the provided values for execution.

    :rtype: bool
    :return: True if the models were successfully submitted for execution.
             False otherwise.
    """
    job_form_data = request.session['job_form_data']
    job_wrapper = JobWrapper(job_form_data)
    if _already_have_results(job_wrapper.data_values):
        # Send the results email
        cmd = 'python /home/ubuntu/weather/ghem/ghem/send_email.py'
        subprocess.call(cmd, shell=True)
        # Terminate the cluster now (do this elsewhere?)
        log.info("Initiating cluster termination")
        # Wait a bit before terminating to give the web app enough time to
        # complete the request
        cmd = 'sleep 120;python /home/ubuntu/weather/ghem/ghem/terminate_cm.py'
        subprocess.Popen(cmd, shell=True)
        return True
    else:
        # Create and subit jobs to compute the results
        job_wrapper.create_data_file()
        log.debug("Job form data: {0}".format(job_wrapper.job_form_data))
        # Must run emits to generate emis_co2.dat - this step is requried to
        # run the models and it's a lot simpler to have it run form here than
        # from a job manager script
        cmd = "/var/opt/IMOGEN/EMITS/emits"
        p = subprocess.call(cmd, shell=True)
        log.debug("Ran {0} program".format(cmd))
        # Now submit the models via the job manager
        jr = DRMAAJobRunner()
        return jr.queue_job(job_wrapper)

def _already_have_results(input_data_values, results_dir='/mnt/transient_nfs/ghem'):
    """
    Check if the resulting plot for the provided input data values have already
    been computed and ther results are stored in an external repository. If the
    results already exist, download those and make them available in local
    directory ``results_dir`` and return ``True``. If results are not found,
    return ``False``.

    This method assumess existence of an S3 bucket that contains previously
    computed results. The name of this bucket it set in this method. Another
    assumption is that the owner of this is the same user as the one that started
    this instance (and because the general assumption for this app is that it's
    running atop CloudMan platform, the access keys for the bucket are obtained
    from CloudMan's user data).
    """
    try:
        data_values_string = '_'.join(input_data_values)
        results_hash = hashlib.md5(data_values_string).hexdigest()
        results_file_name = results_hash + '.tar.gz'

        # Get S3 bucket creds from CloudMan's user data
        cm_ud = {}
        ud_file = '/tmp/cm/userData.yaml'
        with open(ud_file) as f:
            cm_ud = yaml.load(f)
        aws_access_key = cm_ud.get('access_key', None)
        aws_secret_key = cm_ud.get('secret_key', None)

        # Check if the key (ie, file) matching the results already exist
        s3_conn = boto.connect_s3(aws_access_key, aws_secret_key)
        bucket_name = 'imogen-dev'
        bucket = s3_conn.get_bucket(bucket_name)
        key = bucket.get_key(results_file_name)
        if key:
            # Retrieve the file with the results
            file_name = os.path.join(results_dir, results_file_name)
            key.get_contents_to_filename(file_name)
            log.debug("Found previously computed results and saved them to {0}"\
                    .format(file_name))
            # Open the results tar file
            tfile = tarfile.open(file_name)
            # Extract the results tar file
            if tarfile.is_tarfile(file_name):
                tfile.extractall(results_dir)
                return True
            else:
                log.debug("Retrieved results file is not a tar file!?")
                return False
        else:
            log.debug("No results found; need to compute results.")
            return False
    except:
        # Fallback to recomputing the results
        return False

