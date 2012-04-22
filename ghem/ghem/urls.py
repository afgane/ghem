from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {'template': 'index.html'}, "home_page"),
    url(r'^index.html$', direct_to_template, {'template': 'index.html'}),
    url(r'^the_project.html$', direct_to_template, {'template': 'static/the_project.html'}, "project"),
    url(r'^contact.html$', direct_to_template, {'template': 'static/contact.html'}, "contact"),
    # url(r'^run.html$', direct_to_template, {'template': 'static/run.html'}, "run"),
    url(r'^run.html$', 'ghem.views.run', name='run'),
    url(r'^thankyou.html$', direct_to_template, {'template': 'static/thankyou.html'}, "thankyou"),
    url(r'^the_model.html$', direct_to_template, {'template': 'static/the_model.html'}, "model"),
    # Examples:
    # url(r'^$', 'ghem.views.home', name='home'),
    # url(r'^ghem/', include('ghem.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
