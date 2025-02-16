import random
from config.config import PROXIES

def get_random_proxy():
    return random.choice(PROXIES)
