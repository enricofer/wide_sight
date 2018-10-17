import sys

def get_utm_srid_from_lonlat(lon,lat):
    EPSG_srid = int(32700-round((45+lat)/90,0)*100 + round((183+lon)/6,0))
    return EPSG_srid
