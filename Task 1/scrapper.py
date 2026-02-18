import requests
from bs4 import BeautifulSoup
import re
import time

EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

class WebFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.common_pages = ['/contact', '/about', '/team', '/contact-us', '/about-us']

    def find_emails_in_text(self, text):
        try:
            return set(re.findall(EMAIL_PATTERN, text))
        except:
            return set()

    def scan_website(self, base_url):
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url
            
        found_emails = set()
        
        try:
            domain_part = "/".join(base_url.split("/")[:3])
        except:
            domain_part = base_url

        urls_to_check = [base_url]
        for page in self.common_pages:
            urls_to_check.append(domain_part + page)
            
        pages_scanned = 0
        
        for link in urls_to_check:
            if len(found_emails) >= 5:
                break
                
            try:
                resp = requests.get(link, headers=self.headers, timeout=5)
                
                if resp.status_code == 200:
                    pages_scanned += 1
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    text = soup.get_text()
                    emails = self.find_emails_in_text(text)
                    found_emails.update(emails)
                    
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href']
                        if 'mailto:' in href:
                            clean_email = href.replace('mailto:', '').split('?')[0]
                            found_emails.add(clean_email)
                            
            except Exception as e:
                continue
                
        return {
            'base_url': base_url,
            'emails': list(found_emails),
            'pages_crawled': pages_scanned,
            'email_count': len(found_emails),
            'error': None if len(found_emails) > 0 else "No emails found"
        }