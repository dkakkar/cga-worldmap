package org.geonode.rest;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.logging.Level;

import javax.xml.namespace.QName;

import junit.framework.Test;
import net.sf.json.JSONArray;
import net.sf.json.JSONNull;
import net.sf.json.JSONObject;
import net.sf.json.test.JSONAssert;

import org.apache.commons.io.IOUtils;
import org.geonode.geojson.GeoJSONParser;
import org.geoserver.data.test.MockData;
import org.geoserver.test.GeoServerTestSupport;
import org.geotools.TestData;
import org.restlet.data.Status;

import com.mockrunner.mock.web.MockHttpServletResponse;
import com.vividsolutions.jts.geom.Polygon;

public class ProcessRestletTest extends GeoServerTestSupport {

    private static final String RESTLET_PATH = "/rest/process/hazard";

    private static final QName POLITICAL_LAYER = new QName(MockData.DEFAULT_URI, "states",
            MockData.DEFAULT_PREFIX);

    static {
        ProcessRestlet.LOGGER.setLevel(Level.FINER);
    }

    /**
     * This is a READ ONLY TEST so we can use one time setup
     */
    public static Test suite() {
        return new OneTimeTestSetup(new ProcessRestletTest());
    }

    @Override
    protected void populateDataDirectory(MockData dataDirectory) throws Exception {
        super.populateDataDirectory(dataDirectory);
        dataDirectory.addWellKnownCoverageTypes();
        URL properties = TestData.url(this, "states.properties");
        QName politicalLayer = POLITICAL_LAYER;
        dataDirectory.addPropertiesType(politicalLayer, properties, null);
    }

    public void testHTTPMethod() throws Exception {
        MockHttpServletResponse r = getAsServletResponse(RESTLET_PATH);
        assertEquals(Status.CLIENT_ERROR_METHOD_NOT_ALLOWED.getCode(), r.getStatusCode());
    }

    public void testSuccessCode() throws Exception {
        String jsonRequest = loadTestData("sample-request-DEM-point.json");

        MockHttpServletResponse r = postAsServletResponse(RESTLET_PATH, jsonRequest);
        assertEquals(200, r.getStatusCode());
    }

    public void testOutputObjects() throws Exception {
        String jsonRequest = loadTestData("sample-request-DEM-point.json");

        final String resultStr;
        {
            final InputStream in = post(RESTLET_PATH, jsonRequest);
            resultStr = IOUtils.toString(in, "UTF-8");
        }

        JSONObject result = JSONObject.fromObject(resultStr);
        assertTrue(result.containsKey("statistics"));
        assertTrue(result.containsKey("political"));
        assertTrue(result.containsKey("buffer"));
    }

    public void testRequestOneCoverageWithPoint() throws Exception {
        String jsonRequest = loadTestData("sample-request-DEM-point.json");

        final String resultStr;
        {
            final InputStream in = post(RESTLET_PATH, jsonRequest);
            resultStr = IOUtils.toString(in, "UTF-8");
        }
        // System.out.println(resultStr);

        JSONObject result = JSONObject.fromObject(resultStr);
        assertTrue(result.get("statistics") instanceof JSONObject);

        JSONObject statistics = (JSONObject) result.get("statistics");
        assertEquals(1, statistics.size());

        assertTrue(statistics.get("wcs:DEM") instanceof JSONObject);
        JSONObject demStats = (JSONObject) ((JSONObject) result.get("statistics")).get("wcs:DEM");

        assertTrue(demStats.get("min") instanceof JSONArray);
        assertTrue(demStats.get("max") instanceof JSONArray);
        assertTrue(demStats.get("mean") instanceof JSONArray);
        assertTrue(demStats.get("stddev") instanceof JSONArray);
    }

    public void testBufferResponse() throws Exception {
        String jsonRequest = loadTestData("sample-request-DEM-point.json");

        final String resultStr;
        {
            final InputStream in = post(RESTLET_PATH, jsonRequest);
            resultStr = IOUtils.toString(in, "UTF-8");
        }
        // System.out.println(resultStr);

        JSONObject result = JSONObject.fromObject(resultStr);
        JSONObject buffer = result.getJSONObject("buffer");

        Object parsed = GeoJSONParser.parse(buffer);
        assertTrue(parsed instanceof Polygon);
    }

    /**
     * If the request geometry/buffer does not intersect the requested coverage the returned
     * statistics shall be {@code null}
     * <p>
     * Sample response:
     * 
     * <code>
     * <pre>
     * {
     *     "statistics": {"wcs:DEM": null},
     *     "political":   {
     *       "country": "Tasmania",
     *       "municipality": "Bicheno"
     *     },
     *     "buffer": {"type":"Polygon", "coordinates":[...]}
     *  }
     * </pre>
     * <code>
     * </p>
     * 
     * @throws Exception
     */
    public void testRequestBuffedDoesNotIntersectCoverage() throws Exception {
        String jsonRequest = loadTestData("sample-request-DEM-point-not-intersecting.json");

        final String resultStr;
        {
            final InputStream in = post(RESTLET_PATH, jsonRequest);
            resultStr = IOUtils.toString(in, "UTF-8");
        }
        // System.out.println(resultStr);

        JSONObject result = JSONObject.fromObject(resultStr);
        assertTrue(result.get("statistics") instanceof JSONObject);

        JSONObject statistics = (JSONObject) result.get("statistics");
        assertEquals(1, statistics.size());

        assertTrue(statistics.containsKey("wcs:DEM"));
        assertTrue(statistics.get("wcs:DEM") instanceof JSONNull);
    }

    public void testRequestTwoCoveragesWithPoint() throws Exception {
        String jsonRequest = loadTestData("sample-request-DEM-BlueMarble-point.json");

        final String resultStr;
        {
            final InputStream in = post(RESTLET_PATH, jsonRequest);
            resultStr = IOUtils.toString(in, "UTF-8");
        }
        // System.out.println(resultStr);

        JSONObject result = JSONObject.fromObject(resultStr);
        assertTrue(result.get("statistics") instanceof JSONObject);

        JSONObject statistics = (JSONObject) result.get("statistics");
        assertEquals(2, statistics.size());

        assertTrue(statistics.get("wcs:BlueMarble") instanceof JSONObject);
        assertTrue(statistics.get("wcs:DEM") instanceof JSONObject);
        JSONObject demStats = (JSONObject) ((JSONObject) result.get("statistics"))
                .get("wcs:BlueMarble");

        assertTrue(demStats.get("min") instanceof JSONArray);
        assertEquals(3, ((JSONArray) demStats.get("min")).size());

        assertTrue(demStats.get("max") instanceof JSONArray);
        assertEquals(3, ((JSONArray) demStats.get("max")).size());

        assertTrue(demStats.get("mean") instanceof JSONArray);
        assertEquals(3, ((JSONArray) demStats.get("mean")).size());

        assertTrue(demStats.get("stddev") instanceof JSONArray);
        assertEquals(3, ((JSONArray) demStats.get("stddev")).size());
    }

    public void testPoliticalLayer() throws Exception {
        String jsonRequest = loadTestData("political-layer-test-request.json");

        final String resultStr;
        {
            final InputStream in = post(RESTLET_PATH, jsonRequest);
            resultStr = IOUtils.toString(in, "UTF-8");
        }

        JSONObject result = JSONObject.fromObject(resultStr);
        assertTrue(result.get("political") instanceof JSONArray);

        final JSONArray expected = JSONArray.fromObject("["
                + "{\"STATE_NAME\":\"New York\",\"SUB_REGION\":\"Mid Atl\"},"
                + "{\"STATE_NAME\":\"Pennsylvania\",\"SUB_REGION\":\"Mid Atl\"}" + "]");
        final JSONArray actual = result.getJSONArray("political");

        JSONAssert.assertEquals(expected, actual);
    }

    public void testPoliticalLayerNonExistent() throws Exception {
        String jsonRequest;
        {
            jsonRequest = loadTestData("political-layer-test-request.json");
            JSONObject req = JSONObject.fromObject(jsonRequest);
            req.put("politicalLayer", "nonExistentLayerName");
            jsonRequest = req.toString(2);
        }

        MockHttpServletResponse r = postAsServletResponse(RESTLET_PATH, jsonRequest);
        assertEquals(Status.CLIENT_ERROR_EXPECTATION_FAILED.getCode(), r.getStatusCode());
    }

    public void testPoliticalLayerIsNotAVectorLayer() throws Exception {
        String jsonRequest;
        {
            jsonRequest = loadTestData("political-layer-test-request.json");
            JSONObject req = JSONObject.fromObject(jsonRequest);
            req.put("politicalLayer", "wcs:DEM");
            jsonRequest = req.toString(2);
        }

        MockHttpServletResponse r = postAsServletResponse(RESTLET_PATH, jsonRequest);
        assertEquals(Status.CLIENT_ERROR_EXPECTATION_FAILED.getCode(), r.getStatusCode());
    }

    public void testPoliticalLayerAttributesNotProvided() throws Exception {
        String jsonRequest;
        {
            jsonRequest = loadTestData("political-layer-test-request.json");
            JSONObject req = JSONObject.fromObject(jsonRequest);
            req.remove(ProcessRestlet.POLITICAL_LAYER_ATTRIBUTES_PARAM);
            jsonRequest = req.toString(2);
        }

        MockHttpServletResponse response = postAsServletResponse(RESTLET_PATH, jsonRequest);
        assertEquals(Status.CLIENT_ERROR_EXPECTATION_FAILED.getCode(), response.getStatusCode());

        {
            jsonRequest = loadTestData("political-layer-test-request.json");
            JSONObject req = JSONObject.fromObject(jsonRequest);
            req.put(ProcessRestlet.POLITICAL_LAYER_ATTRIBUTES_PARAM, new JSONArray());
            jsonRequest = req.toString(2);
        }

        response = postAsServletResponse(RESTLET_PATH, jsonRequest);
        assertEquals(Status.CLIENT_ERROR_EXPECTATION_FAILED.getCode(), response.getStatusCode());
    }

    public void testPoliticalLayerAttributesIncludesNonExistentAtt() throws Exception {
        String jsonRequest;
        {
            jsonRequest = loadTestData("political-layer-test-request.json");
            JSONObject req = JSONObject.fromObject(jsonRequest);
            JSONArray atts = req.getJSONArray("politicalLayerAttributes");
            atts.add("NonExistentAttribute");
            req.put(ProcessRestlet.POLITICAL_LAYER_ATTRIBUTES_PARAM, atts);
            jsonRequest = req.toString(2);
        }

        MockHttpServletResponse response = postAsServletResponse(RESTLET_PATH, jsonRequest);
        assertEquals(Status.CLIENT_ERROR_EXPECTATION_FAILED.getCode(), response.getStatusCode());
    }

    private String loadTestData(final String fileName) throws IOException {
        StringBuilder sb = new StringBuilder();
        BufferedReader reader = new BufferedReader(new InputStreamReader(TestData.openStream(this,
                fileName)));
        String line;
        while ((line = reader.readLine()) != null) {
            sb.append(line).append('\n');
        }
        return sb.toString();
    }
}
