"""Base views.
"""
import logging
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
    job_wrapper.create_data_file()
    print job_wrapper.job_form_data
    # Must run emits to generate emis_co2.dat - this step is requried to
    # run the models and it's a lot simpler to have it run form here than
    # from a job manager script
    cmd = "/var/opt/IMOGEN/EMITS/emits"
    subprocess.call(cmd, shell=True)
    print "Ran {0} program".format(cmd)
    # Now submit the models via the job manager
    jr = DRMAAJobRunner()
    return jr.queue_job(job_wrapper)

