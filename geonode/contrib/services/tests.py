# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from .models import Service




class ServicesTests(TestCase):
    """Tests geonode.contrib.services app/module
    """

    def setUp(self):
        self.user = 'admin'
        self.passwd = 'admin'

    fixtures = ['map_data.json', 'initial_data.json']

    def test_placholder(self):
        self.assertEqual(1,1)


    def test_register_indexed_wms(self):
        """Test registering demo.geonode.org as an indexed WMS
        """
        c = Client()
        c.login(username='admin', password='admin')
        response = c.post(reverse('register_service'),
                            {
                             'type':'WMS',
                             'url':'http://metaspatial.net/cgi-bin/ogc-wms.xml',
                            })
        self.assertEqual(response.status_code, 200)
        service_dict = json.loads(response.content)[0]


        try:
            service = Service.objects.get(id=service_dict['service_id'])
            self.assertTrue(service.layer_set.all().count() > 0) #Harvested some layers
            self.assertEqual(service.method, "I")
            self.assertEqual(service.type, "WMS")
            self.assertEqual(service.ptype(), 'gxp_wmscsource')


        except Exception, e:
            self.fail("Service not created: %s" % str(e))

    def test_register_arcrest(self):
        """Test registering demo.geonode.org as an indexed WMS
        """
        c = Client()
        c.login(username='admin', password='admin')
        response = c.post(reverse('register_service'),
                          {
                              'type':'REST',
                              'url':'http://maps1.arcgisonline.com/ArcGIS/rest/services/EPA_Facilities/MapServer',
                              })
        self.assertEqual(response.status_code, 200)
        service_dict = json.loads(response.content)[0]


        try:
            service = Service.objects.get(id=service_dict['service_id'])
            self.assertTrue(service.layer_set.all().count() > 0) #Harvested some layers
            self.assertEqual(service.method, "I")
            self.assertEqual(service.type, "REST")
            self.assertEqual(service.ptype(), 'gxp_arcrestsource')
        except Exception, e:
            self.fail("Service not created: %s" % str(e))


    def test_register_csw(self):
        c = Client()
        c.login(username='admin', password='admin')
        response = c.post(reverse('register_service'),
                      {
                          'type':'CSW',
                          'url':'http://demo.pycsw.org/cite/csw',

        })
        self.assertEqual(response.status_code, 200)
        service_dict = json.loads(response.content)[0]
        try:
            service = Service.objects.get(id=service_dict['service_id'])
        except Exception, e:
            self.fail("Service not created: %s" % str(e))
        self.assertEqual(service.method, "H")
        self.assertEqual(service.type, "CSW")
        self.assertEqual(service.base_url, 'http://demo.pycsw.org/cite/csw')
        #TODO: Use CSW or make mock CSW containing just a few small WMS & ESRI service records
        self.assertEquals(service.service_set.all().count(), 0) #No WMS/REST services
        self.assertEquals(service.layer_set.all().count(),0)   # No Layers for this one
