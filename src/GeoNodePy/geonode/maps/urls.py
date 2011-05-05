from django.conf.urls.defaults import patterns, url

js_info_dict = {
    'packages': ('geonode.maps',),
}

urlpatterns = patterns('geonode.maps.views',
    (r'^$', 'maps'),
<<<<<<< HEAD
    url(r'^new/?$', 'newmap', name="map_new"),
    (r'^(?P<mapid>\d+)/share/?$', 'map_share'),
    (r'^(?P<mapid>\d+)/edit/?$', 'map_controller'),
    (r'^(?P<mapid>\d+)/edit/describe/?$', 'describemap'),
    (r'^(?P<mapid>\d+)/download/?$', 'map_download'),
    (r'^check/?$', 'check_download'),
    (r'^checkurl/?$', 'ajax_url_lookup'),
    (r'^history/(?P<mapid>\d+)/?$', 'ajax_snapshot_history'),
    (r'^embed/?$', 'embed'),
    (r'^(?P<mapid>\w+)/embed/?$', 'embed'),
    (r'^(?P<mapid>\d+)/data/?$', 'mapJSON'),
    (r'^searchfields/?$', 'searchFieldsJSON'),
    (r'^snapshot/create/?$', 'snapshot_create'),
    url(r'^search/?$', 'maps_search_page', name='maps_search'),
    url(r'^search/api/?$', 'maps_search', name='maps_search_api'),
    url(r'^(?P<mapid>\d+)/ajax-permissions/?$', 'ajax_map_permissions', name='ajax_map_permissions'),
    url(r'^(?P<mapid>\d+)/ajax-permissions-email/?$', 'ajax_map_permissions_by_email', name='ajax_map_permissions_by_email'),
    url(r'^change-poc/(?P<ids>\w+)/?$', 'change_poc', name="change_poc"),
    (r'^(?P<mapid>\w+)/(?P<snapshot>\w+)/?$', 'view'),
    (r'^(?P<mapid>\w+)/(?P<snapshot>\w+)/embed/?$', 'embed'),
    (r'^(?P<mapid>[A-Za-z0-9_\-]+)/?$', 'view'),
=======
    url(r'^new$', 'newmap', name="map_new"),
    (r'^(?P<mapid>\d+)$', 'map_controller'),
    (r'^(?P<mapid>\d+)/view$', 'view'),
    (r'^(?P<mapid>\d+)/download/$', 'map_download'),
    (r'^check/$', 'check_download'),
    (r'^embed/$', 'embed'),
    (r'^(?P<mapid>\d+)/embed$', 'embed'),
    (r'^(?P<mapid>\d+)/data$', 'mapJSON'),
    url(r'^search/?$', 'maps_search_page', name='maps_search'),
    url(r'^search/api/?$', 'maps_search', name='maps_search_api'),
    url(r'^(?P<mapid>\d+)/ajax-permissions$', 'ajax_map_permissions', name='ajax_map_permissions'),
    url(r'^change-poc/(?P<ids>\w+)$', 'change_poc', name="change_poc"),

>>>>>>> 62e10950604c85ea2fec4f0bb54c420c0ea66ed4
)
