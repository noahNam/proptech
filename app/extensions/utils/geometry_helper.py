def input_coordinates_from_lat_lon(lat, lon):
    """
        coordinates = 'SRID=4326;POINT({latitude} {longitude})'
    """
    return 'SRID=4326;POINT(' + str(lat) + ' ' + str(lon) + ')'
