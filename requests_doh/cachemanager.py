from datetime import datetime, timedelta

__all__ = ('set_dns_cache_expire_time', 'purge_dns_cache', 'cachemanager')

class DNSCacheManager:
    def __init__(self):
        self._expire = timedelta(seconds=300)
        self._data = {}
    
    def set_expire_time(self, time):
        if isinstance(time, float) or isinstance(time, int):        
            self._expire = timedelta(seconds=time)
        else:
            raise ValueError(f'{time.__class__.__name__} is not float type')
    
    def set_cache(self, host, answers):
        self._data[host] = {
            "expire": datetime.now() + self._expire,
            "data": answers
        }
    
    def get_cache(self, host):
        try:
            item = self._data[host]
        except KeyError:
            return None
        
        now = datetime.now()

        if item['expire'] < now:
            # DNS cache is expired
            self._data.pop(host)
            return None
        
        return item['data']

    def purge(self, host):
        try:
            self._data.pop(host)
        except KeyError:
            raise ValueError(f"host '{host}' is not cached")

    def purge_all(self):
        self._data.clear()

cachemanager = DNSCacheManager()

def set_dns_cache_expire_time(time):
    """Set DNS cache expired time in seconds
    
    Parameters
    -----------
    time: :class:`float`
        An expire time
    """
    cachemanager.set_expire_time(time)

def purge_dns_cache(host=None):
    """Purge DNS cache

    Parameters
    -----------
    host: :class:`str`
        Cached DNS host want to be purged, if ``host`` is None, all DNS caches will be purged.
    """
    if host:
        cachemanager.purge(host)
    else:
        cachemanager.purge_all()