import exifread
import sys
import math
import piexif
from datetime import datetime
from PIL import Image

# based on https://gist.github.com/erans/983821

def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format

    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)

def _convert_to_double(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format

    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    print ("EXIT VALUE",value, file=sys.stderr)
    return float(value.values[0].num) / float(value.values[0].den)

def _convert_to_date(value):
    return datetime.strptime(str(value), '%Y:%m:%d  %H:%M:%S')

def get_exif_values(exif_data):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """

    gps_latitude = _get_if_exist(exif_data, 'GPS GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data, 'GPS GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'GPS GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'GPS GPSLongitudeRef')
    gps_altitude = _get_if_exist(exif_data, 'GPS GPSAltitude')
    gps_track = _get_if_exist(exif_data, 'GPS GPSTrack')
    gps_img_direction = _get_if_exist(exif_data, 'GPS GPSImgDirection')
    gps_pitch = _get_if_exist(exif_data, 'GPS GPSPItch')
    gps_roll = _get_if_exist(exif_data, 'GPS GPSRoll')
    sensor_pixel_width = _get_if_exist(exif_data, 'EXIF PixelXDimension')
    focal_plane_x_res = _get_if_exist(exif_data, 'EXIF FocalPlaneXResolution')
    focal_plane_res_unit = _get_if_exist(exif_data, 'EXIF FocalPlaneResolutionUnit')
    focal_length = _get_if_exist(exif_data, 'EXIF FocalLength')
    camera_maker = _get_if_exist(exif_data, 'Image Make')
    camera_model = _get_if_exist(exif_data, 'Image Model')
    original_date_time = _get_if_exist(exif_data, 'EXIF DateTimeOriginal')
    digitized_date_time = _get_if_exist(exif_data, 'EXIF DateTimeDigitized')

    print ("sensor_pixel_width",sensor_pixel_width, file=sys.stderr)
    print ("focal_plane_x_res",focal_plane_x_res, file=sys.stderr)
    print ("focal_plane_res_unit",focal_plane_res_unit, file=sys.stderr)
    print ("focal_length",sensor_pixel_width, file=sys.stderr)

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon
    else:
        lat = None
        lon = None

    if gps_track:
        track = _convert_to_double(gps_track)
    else:
        track = None

    if gps_img_direction:
        img_direction = _convert_to_double(gps_img_direction)
    else:
        img_direction = None

    if gps_pitch:
        pitch = _convert_to_double(gps_pitch)
    else:
        pitch = None

    if gps_roll:
        roll = _convert_to_double(gps_roll)
    else:
        roll = None

    if gps_altitude:
        altitude = _convert_to_double(gps_altitude)
    else:
        altitude = None

    if original_date_time or digitized_date_time:
        shot_time = _convert_to_date(digitized_date_time or original_date_time)
    else:
        shot_time = None

    if sensor_pixel_width and focal_plane_x_res and focal_length:
        sensor_dim = _convert_to_double(sensor_pixel_width) / _convert_to_double(focal_plane_x_res)
        fov =  2 * atan( (sensor_dim/2) / _convert_to_double(focal_length))
    else:
        fov = None

    return lat, lon, altitude, track or img_direction, gps_pitch, gps_roll, fov, camera_maker, camera_model, shot_time

def set_heading_tag(img_file,heading):
    img = Image.open(img_file)
    exif_dict = piexif.load(img.info['exif'])
    exif_dict['GPS'][piexif.GPSIFD.GPSImgDirection] = heading.as_integer_ratio()
    exif_bytes = piexif.dump(exif_dict)
    img.save(img_file, "jpeg", exif=exif_bytes) #assuming file format is JPEG
