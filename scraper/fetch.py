import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from utils.proxy import get_random_proxy
from config.config import HEADERS, COOKIES
from utils.logging import log_error

retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504, 405],
    allowed_methods=["HEAD", "GET", "OPTIONS"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

def fetch_page(link):
    proxy = get_random_proxy()
    proxy_url = f"http://{proxy['login']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
    proxies_dict = {
        "http": proxy_url,
        "https": proxy_url,
    }
    try:
        response = http.get(link, cookies=COOKIES, headers=HEADERS, proxies=proxies_dict, verify=False, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.SSLError as e:
        log_error(f"SSL ошибка для {link} с прокси {proxy_url}: {e}", link=link)
    except requests.exceptions.HTTPError as e:
        log_error(f"HTTP ошибка для {link} с прокси {proxy_url}: {e}", link=link)
    except requests.exceptions.RequestException as e:
        log_error(f"Ошибка запроса для {link} с прокси {proxy_url}: {e}", link=link)
    except KeyError as e:
        log_error(f"Ошибка при работе с прокси: {e}", link=link)
    return None
