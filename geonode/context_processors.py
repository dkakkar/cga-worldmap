from django.conf import settings
from django.contrib.sites.models import Site
from geonode import get_version

def resource_urls(request):
    site = Site.objects.get_current()
    return dict(
        STATIC_URL = settings.STATIC_URL,
        SITE_URL = settings.SITEURL,
        GEONODE_CLIENT_LOCATION = settings.GEONODE_CLIENT_LOCATION,
        GEOSERVER_BASE_URL = settings.GEOSERVER_BASE_URL,
        GOOGLE_API_KEY = settings.GOOGLE_API_KEY,
        GOOGLE_ANALYTICS_CODE = settings.GOOGLE_ANALYTICS_CODE,
        SITENAME = settings.SITENAME,
        REGISTRATION_OPEN = settings.REGISTRATION_OPEN,
        VERSION = get_version(),
        CUSTOM_GROUP_NAME = settings.CUSTOM_GROUP_NAME if settings.USE_CUSTOM_ORG_AUTHORIZATION else '',
        USE_CUSTOM_ORG_AUTHORIZATION = settings.USE_CUSTOM_ORG_AUTHORIZATION,
        USE_GAZETTEER = settings.USE_GAZETTEER,
    )

def set_my_language(request):
    context = {}
    #may have to check for existence of django_language - I think it exists already
    #temp_lang = request.session['django_language']
    #context['WM_USER_LANGUAGE'] = temp_lang
    #context['user_language'] = 'ch'
    context['user_language'] = request.session.get('django_language')
    return context
