"""
SpyDialer phone lookup service.
Free reverse phone lookup with name, address, age, emails, relatives.
"""
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re


class SpyDialerService:
    BASE_URL = "https://spydialer.com/search"
    
    async def lookup(self, phone: str) -> Optional[Dict]:
        """Lookup phone number on SpyDialer."""
        try:
            # Clean phone number
            clean_phone = re.sub(r'[^\d]', '', phone)
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}?number={clean_phone}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    return self._parse_result(html, phone)
                    
        except Exception as e:
            print(f"SpyDialer lookup error: {e}")
            return None
    
    def _parse_result(self, html: str, phone: str) -> Optional[Dict]:
        """Parse SpyDialer HTML response."""
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'phone': phone,
            'name': None,
            'age': None,
            'address': None,
            'addresses': [],
            'emails': [],
            'relatives': [],
            'source': 'SpyDialer'
        }
        
        # Look for result containers
        # SpyDialer typically shows results in card-like containers
        
        # Try to find name
        name_elem = soup.find('h2', class_=re.compile(r'name|title', re.I))
        if not name_elem:
            name_elem = soup.find('div', class_=re.compile(r'result-name|person-name', re.I))
        if not name_elem:
            # Try generic h2 or h3
            name_elem = soup.find('h2')
        
        if name_elem:
            result['name'] = name_elem.get_text(strip=True)
        
        # Look for age
        age_match = re.search(r'(\d+)\s*years?\s*old', html, re.I)
        if age_match:
            result['age'] = int(age_match.group(1))
        
        # Look for addresses
        address_elems = soup.find_all('div', class_=re.compile(r'address|location', re.I))
        for addr in address_elems:
            text = addr.get_text(strip=True)
            if text and len(text) > 10:
                result['addresses'].append(text)
        
        # Try to find primary address
        if result['addresses']:
            result['address'] = result['addresses'][0]
        
        # Look for emails
        email_pattern = re.findall(r'[\w.-]+@[\w.-]+\.\w+', html)
        result['emails'] = list(set(email_pattern))[:5]  # Unique, max 5
        
        # Look for relatives
        relative_section = soup.find('div', class_=re.compile(r'relative|family', re.I))
        if relative_section:
            relative_names = relative_section.find_all('div', class_=re.compile(r'name|person', re.I))
            for rel in relative_names:
                text = rel.get_text(strip=True)
                if text and text != result['name']:
                    result['relatives'].append(text)
        
        # If we found at least a name, return result
        if result['name']:
            return result
        
        return None
    
    def format_result(self, result: Dict) -> str:
        """Format SpyDialer result for Telegram message."""
        if not result:
            return "❌ Ничего не найдено в SpyDialer"
        
        text = f"🔍 <b>Результат SpyDialer</b>\n\n"
        text += f"📱 <b>Телефон:</b> {result['phone']}\n"
        
        if result.get('name'):
            text += f"👤 <b>Имя:</b> {result['name']}\n"
        
        if result.get('age'):
            text += f"🎂 <b>Возраст:</b> {result['age']} лет\n"
        
        if result.get('address'):
            text += f"🏠 <b>Адрес:</b> {result['address']}\n"
        
        if result.get('emails'):
            text += f"\n📧 <b>Emails:</b>\n"
            for email in result['emails'][:3]:
                text += f"   • {email}\n"
        
        if result.get('relatives'):
            text += f"\n👥 <b>Родственники:</b>\n"
            for rel in result['relatives'][:5]:
                text += f"   • {rel}\n"
        
        return text
    
    async def health_check(self) -> bool:
        """Check if SpyDialer is accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, timeout=10) as response:
                    return response.status == 200
        except:
            return False
