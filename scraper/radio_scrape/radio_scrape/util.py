import requests
from datetime import datetime
def sever_file_last_update(url):
    """
        Attempts to retrieve the 'last-modified' header from the server.
        Returns date as a datetime object 
    """

    try:
        last_mod = requests.head(url).headers['last-modified']
        last_mod_dt = datetime.strptime(last_mod.replace(" GMT",""), "%a, %d %b %Y %H:%M:%S")
    except:
        last_mod_dt = None
    
    return last_mod_dt