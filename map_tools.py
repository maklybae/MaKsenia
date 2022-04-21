import requests

from config import APIKEY
from exceptions import AddressError


def get_object_info(address: str) -> dict:
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": APIKEY,
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        raise AddressError("Адрес не найден. Проверьте правильность написания")
    try:
        return response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    except IndexError:
        raise AddressError("Адрес не найден. Проверьте правильность написания")


def get_object_coords_region(address: str) -> dict:
    item = get_object_info(address)
    longitude, latitude = item["Point"]["pos"].split(" ")
    try:
        region = item['metaDataProperty']['GeocoderMetaData']['Address']['Components'][2]['name']
    except IndexError:
        raise AddressError("Адрес не найден. Проверьте правильность написания")
    return {"longitude": longitude, "latitude": latitude, "region": region}


def static_map_href(longitude, latitude):
    return f"http://static-maps.yandex.ru/1.x/?l=map&{longitude},{latitude}&size=400,400&pt={longitude},{latitude},flag&spn=0.002,0.002"
