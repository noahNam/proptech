from geojson_pydantic import Feature


def input_coordinates_from_lat_lon(lat, lon):
    """
        coordinates = 'SRID=4326;POINT({latitude} {longitude})'
    """
    return 'SRID=4326;POINT(' + str(lat) + ' ' + str(lon) + ')'


def make_geometry_point_of_pydantic(lat, lon):
    feat = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lat, lon],
        },
    }
    return Feature(**feat)
