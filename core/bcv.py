import requests
from bs4 import BeautifulSoup
import urllib3

# Desactivar advertencias de SSL por certificados del BCV
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_tasa_bcv():
    url = "https://www.bcv.org.ve/"
    tasa_fallback = 36.50  # Valor de respaldo predeterminado
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=6, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Buscar el contenedor del dólar en la estructura del BCV
            div_dolar = soup.find('div', id='dolar')
            if div_dolar:
                str_tasa = div_dolar.find('strong').text.strip().replace(',', '.')
                return float(str_tasa)
    except Exception:
        pass
    return tasa_fallback
