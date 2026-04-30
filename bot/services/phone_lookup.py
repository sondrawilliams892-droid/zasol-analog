import aiohttp
import logging
from typing import Optional, Dict, List
from bs4 import BeautifulSoup

from bot.config import WHITEPAGES_API_KEY, NUMVERIFY_API_KEY, USE_SCRAPING
from bot.services.spy_dialer import SpyDialerService

logger = logging.getLogger(__name__)

# Free proxy rotation for scraping (GeoNode API)
SCRAPING_PROXIES = [
    "http://38.183.146.83:80",      # elite, Indonesia
    "http://54.39.154.107:8082",    # anonymous, Canada  
    "http://188.132.150.253:8080",  # transparent, Turkey
    "http://31.145.149.75:9090",    # transparent, Turkey
    "http://103.48.68.29:83",       # transparent, India
]


class PhoneLookupService:
    """Multi-source phone lookup: paid API -> free API -> scraping fallback"""
    
    def __init__(self):
        self.spy_dialer = SpyDialerService()
    
    async def lookup(self, phone: str) -> Optional[Dict]:
        phone = self._normalize(phone)
        logger.info(f"=== PHONE LOOKUP START: {phone} ===")
        
        results = []
        
        # 1. Try Whitepages Pro (paid, best quality)
        if WHITEPAGES_API_KEY:
            logger.info(f"Trying Whitepages for {phone}")
            result = await self._whitepages_lookup(phone)
            if result and result.get("name"):
                logger.info(f"Whitepages hit for {phone}: {result['name']}")
                results.append(result)
            else:
                logger.info(f"Whitepages miss for {phone}")
        else:
            logger.info("Whitepages API key not configured, skipping")
        
        # 2. Try Numverify (free, basic)
        if NUMVERIFY_API_KEY:
            logger.info(f"Trying Numverify for {phone}")
            result = await self._numverify_lookup(phone)
            if result:
                logger.info(f"Numverify hit for {phone}")
                results.append(result)
            else:
                logger.info(f"Numverify miss for {phone}")
        else:
            logger.info("Numverify API key not configured, skipping")
        
        # 3. Scraping fallback (TruePeopleSearch + SpyDialer)
        if USE_SCRAPING:
            logger.info(f"Trying scraping sources for {phone}")
            
            # Try TruePeopleSearch
            logger.info(f"Trying TruePeopleSearch for {phone}")
            result = await self._truepeoplesearch_scrape(phone)
            if result and result.get("name"):
                logger.info(f"TruePeopleSearch hit for {phone}: {result['name']}")
                results.append(result)
            else:
                logger.info(f"TruePeopleSearch miss for {phone}")
            
            # Try SpyDialer
            logger.info(f"Trying SpyDialer for {phone}")
            result = await self.spy_dialer.lookup(phone)
            if result and result.get("name"):
                logger.info(f"SpyDialer hit for {phone}: {result['name']}")
                results.append(result)
            else:
                logger.info(f"SpyDialer miss for {phone}")
        else:
            logger.info("Scraping disabled (USE_SCRAPING=False)")
        
        # Return best result (prioritize by data completeness)
        if results:
            # Sort by number of fields present
            def score_result(r):
                score = 0
                if r.get("name"): score += 10
                if r.get("address"): score += 5
                if r.get("age") or r.get("dob"): score += 3
                if r.get("emails"): score += 2
                if r.get("relatives"): score += 1
                return score
            
            results.sort(key=score_result, reverse=True)
            best = results[0]
            logger.info(f"=== PHONE LOOKUP END: {phone} -> {best.get('source', 'unknown')} | {best.get('name', 'no name')} ===")
            return best
        
        logger.warning(f"=== PHONE LOOKUP END: {phone} -> NO RESULTS ===")
        return None
    
    def _normalize(self, phone: str) -> str:
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) == 10:
            digits = "1" + digits  # US default
        return digits
    
    async def _whitepages_lookup(self, phone: str) -> Optional[Dict]:
        """Whitepages Pro API - $0.03-0.07 per lookup"""
        try:
            url = "https://proapi.whitepages.com/3.0/phone"
            params = {
                "api_key": WHITEPAGES_API_KEY,
                "phone": phone,
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    
                    result = {
                        "source": "whitepages",
                        "phone": phone,
                        "name": "",
                        "address": "",
                        "emails": [],
                        "phones": [],
                        "addresses": [],
                        "dob": "",
                        "age": "",
                        "raw": data
                    }
                    
                    if "belongs_to" in data and data["belongs_to"]:
                        person = data["belongs_to"][0] if isinstance(data["belongs_to"], list) else data["belongs_to"]
                        result["name"] = person.get("name", "")
                        result["age"] = str(person.get("age_range", ""))
                    
                    if "current_addresses" in data and data["current_addresses"]:
                        addr = data["current_addresses"][0]
                        result["address"] = f"{addr.get('street_line_1','')}, {addr.get('city','')} {addr.get('state_code','')} {addr.get('postal_code','')}"
                        result["addresses"].append(result["address"])
                    
                    return result
        except Exception as e:
            logger.error(f"Whitepages error: {e}")
            return None
    
    async def _numverify_lookup(self, phone: str) -> Optional[Dict]:
        """Numverify - free 250/month, basic data only (no name/address)"""
        try:
            url = "http://apilayer.net/api/validate"
            params = {"access_key": NUMVERIFY_API_KEY, "number": phone, "format": 1}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    if not data.get("valid"):
                        return None
                    return {
                        "source": "numverify",
                        "phone": data.get("number", phone),
                        "name": "",
                        "address": f"{data.get('location', '')}, {data.get('country_name', '')}",
                        "emails": [],
                        "phones": [phone],
                        "addresses": [],
                        "carrier": data.get("carrier", ""),
                        "line_type": data.get("line_type", ""),
                        "country": data.get("country_name", ""),
                        "raw": data
                    }
        except Exception as e:
            logger.error(f"Numverify error: {e}")
            return None
    
    async def _truepeoplesearch_scrape(self, phone: str) -> Optional[Dict]:
        """Scrape TruePeopleSearch.com - FREE but fragile"""
        try:
            formatted = f"({phone[1:4]}) {phone[4:7]}-{phone[7:]}" if len(phone) == 11 else phone
            url = f"https://www.truepeoplesearch.com/results?phoneno={formatted.replace(' ', '%20').replace('(', '%28').replace(')', '%29')}"
            
            logger.info(f"TruePeopleSearch: Looking up {phone} via {url}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }
            
            # Try with proxy first, then without
            proxies_to_try = SCRAPING_PROXIES + [None]  # None = direct
            
            for proxy_url in proxies_to_try:
                try:
                    async with aiohttp.ClientSession() as session:
                        proxy = proxy_url if proxy_url else None
                        logger.info(f"TruePeopleSearch: Requesting via {'proxy ' + proxy if proxy else 'direct'}")
                        
                        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15), allow_redirects=True, proxy=proxy) as resp:
                            logger.info(f"TruePeopleSearch: Response status {resp.status} via {'proxy' if proxy else 'direct'}")
                            
                            if resp.status != 200:
                                logger.warning(f"TruePeopleSearch returned {resp.status}")
                                continue
                            
                            html = await resp.text()
                            logger.info(f"TruePeopleSearch: Got HTML length {len(html)}")
                            
                            # Check for cloudflare/blocking
                            if 'cloudflare' in html.lower() or 'cf-browser-verification' in html.lower():
                                logger.warning("TruePeopleSearch: Cloudflare detected")
                                continue
                            if 'blocked' in html.lower() or 'captcha' in html.lower():
                                logger.warning("TruePeopleSearch: Blocking detected")
                                continue
                            
                            soup = BeautifulSoup(html, "lxml")
                            break
                except Exception as e:
                    logger.warning(f"TruePeopleSearch: {'Proxy ' + proxy_url if proxy_url else 'Direct'} failed: {e}")
                    continue
            else:
                logger.error("TruePeopleSearch: All proxies/direct failed")
                return None
                    
                    result = {
                        "source": "truepeoplesearch",
                        "phone": phone,
                        "name": "",
                        "address": "",
                        "emails": [],
                        "phones": [phone],
                        "addresses": [],
                        "dob": "",
                        "age": "",
                        "raw": {}
                    }
                    
                    # Parse results
                    cards = soup.find_all("div", class_="card")
                    if not cards:
                        cards = soup.find_all("div", class_="card-summary")
                    
                    for card in cards[:1]:  # Take first result
                        name_tag = card.find("a", class_="name") or card.find("h2") or card.find("span", class_="name")
                        if name_tag:
                            result["name"] = name_tag.get_text(strip=True)
                        
                        addr_tags = card.find_all("div", class_="address") or card.find_all("span", class_="address")
                        for addr in addr_tags:
                            addr_text = addr.get_text(strip=True)
                            if addr_text:
                                result["addresses"].append(addr_text)
                        
                        if result["addresses"]:
                            result["address"] = result["addresses"][0]
                        
                        email_tags = card.find_all("a", href=lambda x: x and "mailto:" in x)
                        for email in email_tags:
                            email_text = email.get_text(strip=True)
                            if email_text and email_text not in result["emails"]:
                                result["emails"].append(email_text)
                        
                        phone_tags = card.find_all("a", href=lambda x: x and "tel:" in x)
                        for p in phone_tags:
                            p_text = p.get_text(strip=True)
                            if p_text and p_text not in result["phones"]:
                                result["phones"].append(p_text)
                    
                    if result["name"]:
                        return result
                    return None
                    
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return None
    
    def format_result(self, result: Dict) -> str:
        if not result:
            return "❌ Ничего не найдено."
        
        source = result.get('source', 'unknown')
        source_display = {
            'whitepages': 'Whitepages Pro',
            'numverify': 'NumVerify',
            'truepeoplesearch': 'TruePeopleSearch',
            'SpyDialer': 'SpyDialer'
        }.get(source, source)
        
        lines = [f"<b>🔍 Результат поиска ({source_display})</b>"]
        lines.append(f"\n📞 Номер: <code>{result.get('phone', '')}</code>")
        
        if result.get("name"):
            lines.append(f"👤 Имя: <b>{result['name']}</b>")
        if result.get("age"):
            lines.append(f"🎂 Возраст: {result['age']}")
        if result.get("dob"):
            lines.append(f"📅 DOB: {result['dob']}")
        
        if result.get("address"):
            lines.append(f"\n🏠 Адрес:\n{result['address']}")
        
        if result.get("addresses") and len(result["addresses"]) > 1:
            lines.append("\n📍 Все адреса:")
            for i, addr in enumerate(result["addresses"][:5], 1):
                lines.append(f"  {i}. {addr}")
        
        if result.get("emails"):
            lines.append(f"\n📧 Email{'ы' if len(result['emails']) > 1 else ''}:")
            for email in result["emails"][:10]:
                lines.append(f"  • {email}")
        
        if result.get("phones") and len(result["phones"]) > 1:
            lines.append(f"\n📞 Связанные номера:")
            for p in result["phones"][:10]:
                lines.append(f"  • {p}")
        
        if result.get("relatives"):
            lines.append(f"\n👥 Родственники:")
            for rel in result["relatives"][:5]:
                lines.append(f"  • {rel}")
        
        if result.get("carrier"):
            lines.append(f"\n📡 Оператор: {result['carrier']}")
        if result.get("line_type"):
            lines.append(f"📶 Тип: {result['line_type']}")
        if result.get("country"):
            lines.append(f"🌍 Страна: {result['country']}")
        
        lines.append("\n<i>⚠️ Данные из публичных источников.</i>")
        return "\n".join(lines)

phone_service = PhoneLookupService()
