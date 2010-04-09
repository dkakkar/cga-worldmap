from django.conf import settings
from django.db import models
from owslib.wms import WebMapService
from geoserver.catalog import Catalog
import httplib2
import math

_wms = None
_user, _password = settings.GEOSERVER_CREDENTIALS

class LayerManager(models.Manager):
    
    def __init__(self):
        models.Manager.__init__(self)
        url = "%srest" % settings.GEOSERVER_BASE_URL
        user, password = settings.GEOSERVER_CREDENTIALS
        self.gs_catalog = Catalog(url, user, password)


    def slurp(self):
        cat = self.gs_catalog
        for store in cat.get_stores():
            resources = store.get_resources()
            for resource in resources:
                if resource.name is not None and self.filter(name=resource.name).count() == 0:
                    typename = "%s:%s" % (store.workspace.name,resource.name)
                    models.Model.save(
                        self.model(
                            workspace=store.workspace.name,
                            store=store.name,
                            storeType=store.resource_type,
                            name=resource.name,
                            typename=typename
                        )
                    )


class Layer(models.Model):
    """
    XXX docs strings
    """
    
    objects = LayerManager()
    workspace = models.CharField(max_length=128)
    store = models.CharField(max_length=128)
    storeType = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    typename = models.CharField(max_length=128)


    def delete(self, *args, **kwargs): 
        """
        Override default method to remove a layer. This 
        removes the layer from the GeoServer Catalog as
        removing it from the Django models
        """
        # GEOSERVER_CREDENTIALS 
        HTTP = httplib2.Http(".cache")
        HTTP.add_credentials(_user,_password)
        def _getFeatureUrl(self): 
            if self.storeType == "dataStore":
                return "%srest/workspaces/%s/datastores/%s/featuretypes/%s" % (settings.GEOSERVER_BASE_URL, self.workspace, self.store, self.name)
            if self.storeType == "coverageStore":
                return "%srest/workspaces/%s/coveragestores/%s" % (settings.GEOSERVER_BASE_URL,self.workspace,self.name)
        try:
            print("removing layer from GeoNode") 
            layerURL = "%srest/layers/%s" % (settings.GEOSERVER_BASE_URL,self.name)
            HTTP.request(layerURL,"DELETE")     
            HTTP.request(_getFeatureUrl(self),"DELETE")
            super(Layer, self).delete(*args, **kwargs)
        except ValueError:
            raise NameError("Unable to remove Layer from the GeoNode")

    def download_links(self):
        """Returns a list of (mimetype, URL) tuples for downloads of this data
        in various formats."""
 
        bbox = self.resource.latlon_bbox

        dx = float(bbox[1]) - float(bbox[0])
        dy = float(bbox[3]) - float(bbox[2])

        dataAspect = dx / dy

        height = 550
        width = int(height * dataAspect)

        # bbox: this.adjustBounds(widthAdjust, heightAdjust, values.llbbox).toString(),

        srs = bbox[4]
        bboxString = "%s,%s,%s,%s" % (bbox[0], bbox[2], bbox[1], bbox[3])

        links = []        

        if self.resource.resource_type == "featureType":
            links.append(("SHAPE-ZIP", "%swfs?request=GetFeature&typename=%s&outputformat=SHAPE-ZIP" % (settings.GEOSERVER_BASE_URL, self.typename)))
        elif self.resource.resource_type == "coverage":
            links.append(("GeoTiff", "%swms?request=GetMap&layers=%s&Format=image/geotiff&height=%s&width=%s&srs=%s&bbox=%s" % (settings.GEOSERVER_BASE_URL, self.typename, height, width, srs, bboxString)))

        # ("application/vnd.google-earth.kml+xml", "%swms?request=GetMap&layers=%s&outputformat=application/vnd.google-earth.kml+xml" % (settings.GEOSERVER_BASE_URL, self.typename)) 
        # ("application/pdf", "%swms?request=GetMap&layers=%s&format=application/pdf" % (settings.GEOSERVER_BASE_URL, self.typename)),

        return links

    def metadata_links(self):
        """Returns a list of (type, URL) tuples for known metadata documents
        about this data"""
        #TODO: This function is just a stub
        return [("GeoNode Listing", ".")]

    def maps(self):
        """Return a list of all the maps that use this layer"""
        local_wms = "%swms" % settings.GEOSERVER_BASE_URL
        return set([layer.map for layer in MapLayer.objects.filter(ows_url=local_wms, name=self.typename).select_related()])

    def metadata(self): 
        global _wms
        if (_wms is None) or (self.typename not in _wms.contents):
            wms_url = "%swms?request=GetCapabilities" % settings.GEOSERVER_BASE_URL
            _wms = WebMapService(wms_url)
        return _wms[self.typename]

    @property
    def attribute_names(self):
        if self.resource.resource_type == "featureType":
            return self.resource.attributes
        elif self.resource.resource_type == "coverage":
            return [dim.name for dim in self.resource.dimensions]

    @property
    def display_type(self):
        return ({
            "dataStore" : "Vector Data",
            "coverageStore": "Raster Data",
        }).get(self.storeType, "Data")

    def _set_title(self, title):
        self.resource.title = title

    def _get_title(self):
        return self.resource.title

    title = property(_get_title, _set_title)

    def _set_abstract(self, abstract):
        self.resource.abstract = abstract

    def _get_abstract(self):
        return self.resource.abstract

    abstract = property(_get_abstract, _set_abstract)

    def _set_metadatalinks(self, links):
        self.resource.metadata_links = links

    def _get_metadatalinks(self):
        return self.resource.metadata_links

    metadata_links = property(_get_metadatalinks, _set_metadatalinks)

    def _set_keywords(self, keywords):
        self.resource.keywords = keywords

    def _get_keywords(self):
        return self.resource.keywords

    keywords = property(_get_keywords, _set_keywords)

    @property
    def resource(self):
        if not hasattr(self, "_resource_cache"):
            cat = Layer.objects.gs_catalog
            ws = cat.get_workspace(self.workspace)
            store = cat.get_store(self.store, ws)
            self._resource_cache = cat.get_resource(self.name, store)
        return self._resource_cache

    def _get_default_style(self):
        return self.publishing.default_style

    def _set_default_style(self, style):
        self.publishing.default_style = style

    default_style = property(_get_default_style, _set_default_style)

    def _get_styles(self):
        return self.publishing.styles

    def _set_styles(self, styles):
        self.publishing.styles = styles

    styles = property(_get_styles, _set_styles)

    @property
    def publishing(self):
        if not hasattr(self, "_publishing_cache"):
            cat = Layer.objects.gs_catalog
            self._publishing_cache = cat.get_layer(self.name)
        return self._publishing_cache

    def save(self, *args, **kw):
        models.Model.save(self, *args, **kw)
        if hasattr(self, "_resource_cache"):
            Layer.objects.gs_catalog.save(self._resource_cache)
        if hasattr(self, "_publishing_cache"):
            Layer.objects.gs_catalog.save(self._publishing_cache)

    def get_absolute_url(self):
        return "/data/%s" % self.typename

    def __str__(self):
        return "%s Layer" % self.typename


class Map(models.Model):
    # metadata fields
    title = models.CharField(max_length=200)
    abstract = models.CharField(max_length=200)
    contact = models.CharField(max_length=200)
    featured = models.BooleanField()
    endorsed = models.BooleanField()

    # viewer configuration
    zoom = models.IntegerField()
    center_lat = models.FloatField()
    center_lon = models.FloatField()

    def __unicode__(self):
        return '%s by %s' % (self.title, self.contact)

    def get_absolute_url(self):
        return '/maps/%i' % self.id


class MapLayer(models.Model):
    name = models.CharField(max_length=200)
    ows_url = models.URLField()
    group = models.CharField(max_length=200,blank=True)
    stack_order = models.IntegerField()
    map = models.ForeignKey(Map, related_name="layer_set")

    class Meta:
        ordering = ["stack_order"]

    def __unicode__(self):
        return '%s?layers=%s' % (self.ows_url, self.name)
