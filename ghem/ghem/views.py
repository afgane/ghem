"""Base views.
"""
import logging

# from django.http import HttpResponse
from django.template import RequestContext
from django import forms
from django.shortcuts import render, redirect

from ghem.jobs import JobWrapper
# from ghem.jobs.drm import DRMAAJobRunner

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
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2010 = forms.DecimalField(required=True,
                label="2010 - 2019 (GtC/yr)",
                initial="10.81",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2020 = forms.DecimalField(required=True,
                label="2020 - 2029 (GtC/yr)",
                initial="12.18",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2030 = forms.DecimalField(required=True,
                label="2030 - 2039 (GtC/yr)",
                initial="13.17",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2040 = forms.DecimalField(required=True,
                label="2040 - 2049 (GtC/yr)",
                initial="14.10",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2050 = forms.DecimalField(required=True,
                label="2050 - 2059 (GtC/yr)",
                initial="15.18",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2060 = forms.DecimalField(required=True,
                label="2060 - 2069 (GtC/yr)",
                initial="16.39",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2070 = forms.DecimalField(required=True,
                label="2070 - 2079 (GtC/yr)",
                initial="17.59",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2080 = forms.DecimalField(required=True,
                label="2080 - 2089 (GtC/yr)",
                initial="18.79",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    yr2090 = forms.DecimalField(required=True,
                label="2090 - 2099 (GtC/yr)",
                initial="20.00",
                min_value=0,
                max_value=50,
                decimal_places=2,
                widget=forms.TextInput(attrs={"class": textbox_size}))
    email = forms.EmailField(required=True,
                widget=forms.TextInput(attrs={"class": 'input_xxlarge'}))
    

def run(request):
    if request.method == "POST":
        form = RunModelForm(request.POST)
        if form.is_valid():
            # non_field_errors = None # Flag to capture errors not resulting from form data validation
            log.debug("Form fields are valid: {0}".format(form.cleaned_data))
            # Store the form data into a session object
            request.session["job_form_data"] = form.cleaned_data
            if run_models(request):
                return redirect("/thankyou.html")
            else:
                form.non_field_errors = "Problem running the models"
    else:
        form = RunModelForm()
    return render(request, "run.html", {"form": form}, context_instance=RequestContext(request))

def run_models(request):
    """ Submit the model with the provided values for execution
        :rtype: bool
        :return: True if the models were successfully submitted for execution.
                 False otherwise.
    """
    job_form_data = request.session['job_form_data']
    job_wrapper = JobWrapper(job_form_data)
    print job_wrapper.job_form_data
    # jr = DRMAAJobRunner()
    # return jr.queue_job(job_wrapper)
