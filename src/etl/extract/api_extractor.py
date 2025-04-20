"""
API Extraktor pro získání dat z REST API.
"""
import os
import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union

# Konfigurace loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApiExtractor:
    """Třída pro extrakci dat z REST API."""
    
    def __init__(self, base_url: str, cache_dir: Optional[str] = None, cache_expiry: int = 3600):
        """
        Inicializace API extraktoru.
        
        Args:
            base_url: Základní URL pro API požadavky
            cache_dir: Adresář pro uložení cache (None = žádná cache)
            cache_expiry: Platnost cache v sekundách (výchozí 1 hodina)
        """
        self.base_url = base_url
        self.cache_dir = cache_dir
        self.cache_expiry = cache_expiry
        
        # Vytvoření cache adresáře, pokud neexistuje
        if self.cache_dir and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Vytvořen cache adresář: {self.cache_dir}")
    
    def _get_cache_path(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Vrátí cestu k cache souboru pro daný endpoint a parametry."""
        if not self.cache_dir:
            return None
            
        # Vytvoření hash klíče z endpointu a parametrů
        param_str = json.dumps(params, sort_keys=True) if params else ""
        cache_key = f"{endpoint}_{param_str}".replace("/", "_").replace(":", "_")
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Zkontroluje, zda je cache stále platná na základě času vytvoření."""
        if not cache_path or not os.path.exists(cache_path):
            return False
            
        # Zkontrolovat stáří souboru
        file_time = os.path.getmtime(cache_path)
        file_age = time.time() - file_time
        
        # Cache je platná, pokud je mladší než cache_expiry
        return file_age < self.cache_expiry
    
    def _load_from_cache(self, cache_path: str) -> Optional[Dict[str, Any]]:
        """Načte data z cache souboru."""
        if not self._is_cache_valid(cache_path):
            return None
            
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Data načtena z cache: {cache_path}")
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Nepodařilo se načíst cache: {str(e)}")
            return None
    
    def _save_to_cache(self, cache_path: str, data: Dict[str, Any]) -> None:
        """Uloží data do cache souboru."""
        if not self.cache_dir or not cache_path:
            return
            
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
                logger.info(f"Data uložena do cache: {cache_path}")
        except IOError as e:
            logger.warning(f"Nepodařilo se uložit do cache: {str(e)}")
    
    def extract(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                headers: Optional[Dict[str, str]] = None, use_cache: bool = True,
                max_retries: int = 3, retry_delay: int = 5) -> Dict[str, Any]:
        """
        Extrahuje data z API.
        
        Args:
            endpoint: Endpoint API (relativní k base_url)
            params: URL parametry pro požadavek
            headers: Hlavičky pro požadavek
            use_cache: Zda použít cache (výchozí True)
            max_retries: Maximální počet pokusů při selhání
            retry_delay: Zpoždění mezi pokusy v sekundách
            
        Returns:
            Slovník s daty získanými z API
            
        Raises:
            requests.RequestException: Pokud se požadavek nezdaří po všech pokusech
        """
        # Sestavit URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Zkusit načíst z cache, pokud je to povoleno
        cache_path = self._get_cache_path(endpoint, params) if use_cache else None
        if use_cache and cache_path:
            cached_data = self._load_from_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Výchozí hlavičky
        default_headers = {
            'User-Agent': 'ETL-Pipeline/1.0',
            'Accept': 'application/json'
        }
        
        # Sloučit s uživatelskými hlavičkami
        if headers:
            default_headers.update(headers)
        
        # Provést požadavek s retry logikou
        retry_count = 0
        last_exception = None
        
        while retry_count < max_retries:
            try:
                logger.info(f"Odesílám požadavek na: {url}")
                response = requests.get(url, params=params, headers=default_headers, timeout=30)
                response.raise_for_status()  # Vyvolá výjimku při HTTP chybě
                
                # Parsování odpovědi jako JSON
                data = response.json()
                
                # Uložit do cache, pokud je to povoleno
                if use_cache and cache_path:
                    self._save_to_cache(cache_path, data)
                
                logger.info(f"Úspěšně získána data z API: {url}")
                return data
                
            except (requests.RequestException, json.JSONDecodeError) as e:
                last_exception = e
                retry_count += 1
                
                if retry_count < max_retries:
                    wait_time = retry_delay * (2 ** (retry_count - 1))  # Exponenciální backoff
                    logger.warning(f"Pokus {retry_count} selhal: {str(e)}. Čekání {wait_time}s před dalším pokusem.")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Všechny pokusy selhaly při volání API: {url}")
        
        # Pokud jsme se dostali sem, všechny pokusy selhaly
        raise last_exception or requests.RequestException(f"Nepodařilo se získat data z API: {url}")

    def extract_currency_rates(self, base_currency: str = 'EUR') -> Dict[str, float]:
        """
        Získá aktuální směnné kurzy měn.
        
        Args:
            base_currency: Základní měna pro kurzy (výchozí EUR)
            
        Returns:
            Slovník s kurzy měn: {'USD': 1.1, 'CZK': 25.5, ...}
        """
        try:
            # Používáme veřejné API pro směnné kurzy
            endpoint = f"latest"
            params = {'base': base_currency}
            
            data = self.extract(endpoint, params)
            
            # Extrahujeme jen kurzy
            if 'rates' in data:
                return data['rates']
            else:
                logger.warning(f"Neočekávaný formát odpovědi z API: {data}")
                return {}
                
        except Exception as e:
            logger.error(f"Chyba při získávání kurzů měn: {str(e)}")
            raise 