from errbot import BotPlugin, botcmd, arg_botcmd, webhook


import forecastio
from geopy.geocoders import Nominatim
import pygeoip

# API documentations
# forecastio: https://github.com/ZeevG/python-forecast.io
# geopy: https://github.com/geopy/geopy
# pygeoip: http://pygeoip.readthedocs.org/en/v0.3.2/getting-started.html

# This product includes GeoLite data created by MaxMind, available from
# <a href="http://www.maxmind.com">http://www.maxmind.com</a>.


import settings


class WeatherBot(BotPlugin):
    """ I am Miss Good Weather
    """

    # GeoIP localize
    __gi = None

    _place = ""
    _latitude = None
    _longitude = None
    _forecast = None
    _language = None

    _last_location = None


    def _load_forecast(self,lat,long,language):
        if language == 'en':
            return forecastio.load_forecast(settings.FORECASTIO_API_KEY, lat, long)
        else:
            # Hack, hack, hack
            return forecastio.load_forecast(settings.FORECASTIO_API_KEY, lat, long,units='auto&lang=%s' % language)


    def _get_location_from_ip(self,ip):
        if ip is None or ip == "":
            return (None,(None,None))
        if self.__gi is None:
            self.__gi = pygeoip.GeoIP(settings.GEOIP_FILE)
        location = self.__gi.record_by_addr(ip)
        return {'city':location['city'], 'country':location['country_name'],
                'lat':location['latitude'], 'long':location['longitude']}


    def _get_weather(self, place = None, ip = None):
        if place is None or place == "":
            if ip is not None:
                location = self._get_location_from_ip(ip)
                self._last_location = "%s, %s" % (location['city'],location['country'])
            else:
                return None
        else:
            geo_locator = Nominatim()
            result = geo_locator.geocode(place)
            self._last_location = result
            # Get city, country (last), latitude & longitude
            location = {'city':result[0].split(",")[3].strip(), 'country':result[0].split(",")[-1].strip(),
                        'lat':str(result[1][0]), 'long':str(result[1][1])}
        self._latitude = location['lat']
        self._longitude = location['long']
        self._place = location['city']
        self._forecast = self._load_forecast(location['lat'], location['long'],self._language)
        return self._forecast.hourly().summary

    #@arg_botcmd('place', type=str)
    #@arg_botcmd('-l', dest='language', type=str)
    @botcmd()
    def meteo(self, message, place=None, language='en'):
        """ Renvoie la meteo du lieu indique"""
        if self._language is None:
            self._language = language
        meteo = self._get_weather(place,self._language)
        return "Sorry?" if meteo is None else meteo

    @botcmd()
    def francais(self,message,args):
        """ Parle en francais"""
        self._language = 'fr'
        return "Salut !"

    @botcmd()
    def english(self,message,args):
        """ Changes language to English"""
        self._language = 'en'
        return "Hello!"

    @botcmd()
    def get_internals(self,message,args):
        """ Internals"""
        return "Status: %s, %s, %s, %s" % (self._last_location,self._latitude,self._longitude,self._language)


if __name__ == "__main__":
    test = WeatherBot()
    print(test._get_weather(place="Meudon, France", language = 'fr'))
    print(test._get_weather(ip='88.170.200.70'))