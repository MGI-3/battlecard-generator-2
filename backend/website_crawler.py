# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# import time
# from typing import Set, Dict, List

# class WebsiteCrawler:
#     def __init__(self, base_url: str, max_pages: int = 100, delay: float = 0.5):
#         """
#         Initialize the website crawler.
        
#         Args:
#             base_url: The starting URL to crawl
#             max_pages: Maximum number of pages to crawl
#             delay: Delay between requests in seconds to be respectful
#         """
#         self.base_url = base_url
#         self.max_pages = max_pages
#         self.delay = delay
#         self.domain = urlparse(base_url).netloc
#         self.visited_urls = set()
#         self.url_queue = [base_url]
#         self.page_contents = {}
#         self.headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }

#     def is_valid_url(self, url: str) -> bool:
#         """Check if URL is valid and belongs to the same domain."""
#         parsed = urlparse(url)
#         return bool(parsed.netloc) and parsed.netloc == self.domain and parsed.scheme in ['http', 'https']

#     def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
#         """Extract all links from the page."""
#         links = []
#         for a_tag in soup.find_all('a', href=True):
#             href = a_tag['href']
#             absolute_url = urljoin(current_url, href)
#             if self.is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
#                 links.append(absolute_url)
#         return links

#     def clean_text(self, soup: BeautifulSoup) -> str:
#         """Clean the page content and extract text."""
#         # Remove script and style elements
#         for element in soup(["script", "style", "header", "footer", "nav"]):
#             element.decompose()
        
#         # Get text
#         text = soup.get_text(separator='\n', strip=True)
        
#         # Remove excessive whitespace
#         lines = (line.strip() for line in text.splitlines())
#         chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#         text = '\n'.join(chunk for chunk in chunks if chunk)
        
#         return text

#     def crawl(self) -> Dict[str, str]:
#         """
#         Crawl the website starting from the base URL.
        
#         Returns:
#             Dictionary mapping URLs to their text content.
#         """
#         page_count = 0
        
#         while self.url_queue and page_count < self.max_pages:
#             current_url = self.url_queue.pop(0)
            
#             if current_url in self.visited_urls:
#                 continue
            
#             print(f"Crawling: {current_url}")
#             self.visited_urls.add(current_url)
            
#             try:
#                 response = requests.get(current_url, headers=self.headers, timeout=10)
#                 response.raise_for_status()
                
#                 # Skip non-HTML content
#                 content_type = response.headers.get('Content-Type', '')
#                 if 'text/html' not in content_type.lower():
#                     continue
                
#                 soup = BeautifulSoup(response.text, 'html.parser')
                
#                 # Extract and store text content
#                 text_content = self.clean_text(soup)
#                 if text_content:  # Only store if there's actual content
#                     page_title = soup.title.string if soup.title else current_url
#                     self.page_contents[current_url] = {
#                         'title': page_title,
#                         'content': text_content
#                     }
#                     page_count += 1
                
#                 # Extract links for further crawling
#                 links = self.extract_links(soup, current_url)
#                 for link in links:
#                     if link not in self.visited_urls and link not in self.url_queue:
#                         self.url_queue.append(link)
                
#                 # Be respectful with a delay
#                 time.sleep(self.delay)
                
#             except Exception as e:
#                 print(f"Error crawling {current_url}: {str(e)}")
        
#         print(f"Crawled {len(self.page_contents)} pages")
#         return self.page_contents

#     def get_combined_text(self) -> str:
#         """Get all crawled text combined into a single string."""
#         combined_text = []
        
#         for url, data in self.page_contents.items():
#             combined_text.append(f"--- Page: {data['title']} ({url}) ---")
#             combined_text.append(data['content'])
#             combined_text.append("\n")
        
#         return "\n".join(combined_text)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import time
from typing import Set, Dict, List, Tuple, Optional
import re
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebsiteCrawler:
    def __init__(self, 
                 base_url: str, 
                 max_pages: int = 25,  # Increased default 
                 delay: float = 0.5,
                 max_depth: int = 3,
                 priority_keywords: Optional[List[str]] = None,
                 exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the website crawler with advanced options.
        
        Args:
            base_url: The starting URL to crawl
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds to be respectful
            max_depth: Maximum depth of pages to crawl from the base URL
            priority_keywords: List of keywords to prioritize in URLs (e.g., 'solutions', 'services')
            exclude_patterns: Patterns to exclude from crawling (e.g., '/blog/', '/careers/')
        """
        self.base_url = base_url
        self.max_pages = max_pages
        self.delay = delay
        self.max_depth = max_depth
        self.domain = urlparse(base_url).netloc
        
        # Define default priority patterns if none provided
        self.priority_keywords = priority_keywords or [
            'solution', 'service', 'product', 'case-stud', 'success', 
            'offering', 'platform', 'technology', 'feature', 'capability',
            'benefit', 'customer', 'client', 'industry', 'overview'
        ]
        
        # Define default exclusion patterns if none provided
        self.exclude_patterns = exclude_patterns or [
            '/career', '/job', '/about-us', '/contact', '/login', 
            '/register', '/sign-up', '/sign-in', '/blog', '/news',
            '/press', '/media', '/event', '/webinar', '/term', 
            '/privacy', '/cookie', '/sitemap', '/search', '/tag', '/author'
        ]
        
        # Initialize data structures
        self.visited_urls = set()
        self.url_queue = [(base_url, 0)]  # (url, depth)
        self.page_contents = {}
        self.url_scores = {}  # Store URL scores for prioritization
        self.content_relevance = {}  # Store content relevance scores
        
        # Headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid, belongs to the same domain, and doesn't match exclusion patterns."""
        parsed = urlparse(url)
        
        # Basic validation
        if not bool(parsed.netloc) or parsed.netloc != self.domain or parsed.scheme not in ['http', 'https']:
            return False
        
        # Check for URL normalization (avoid duplication)
        normalized_url = self._normalize_url(url)
        if normalized_url in self.visited_urls:
            return False
        
        # Check for excluded patterns
        for pattern in self.exclude_patterns:
            if pattern in parsed.path.lower():
                return False
                
        return True

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to avoid crawling duplicates with different query parameters."""
        parsed = urlparse(url)
        
        # Remove common tracking parameters
        if parsed.query:
            query_dict = parse_qs(parsed.query)
            # Remove tracking parameters like utm_source, etc.
            for param in list(query_dict.keys()):
                if param.startswith(('utm_', 'ref_', 'source=', 'tracking')):
                    del query_dict[param]
            
            # Reconstruct the normalized URL without these parameters
            normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if query_dict:
                normalized_url += "?" + "&".join(f"{k}={v[0]}" for k, v in query_dict.items())
            return normalized_url
        
        return url

    def _calculate_url_priority(self, url: str, depth: int) -> float:
        """Calculate priority score for a URL based on keywords and depth."""
        # Lower depth gets higher priority
        depth_score = 1.0 / (depth + 1)
        
        # Keywords in URL boost priority
        keyword_score = 0
        url_lower = url.lower()
        
        for keyword in self.priority_keywords:
            if keyword.lower() in url_lower:
                keyword_score += 0.2  # Boost for each matching keyword
        
        # Additional boosts for high-value pages
        if '/solution' in url_lower or '/service' in url_lower:
            keyword_score += 0.5
        if '/case-stud' in url_lower or '/success' in url_lower:
            keyword_score += 0.8
        if '/product' in url_lower or '/offering' in url_lower:
            keyword_score += 0.4
            
        # Penalty for likely irrelevant pages (not excluded but lower priority)
        if '/faq' in url_lower or '/help' in url_lower:
            keyword_score -= 0.2
            
        # Calculate final score - higher is better
        final_score = depth_score + keyword_score
        return final_score

    def extract_links(self, soup: BeautifulSoup, current_url: str, current_depth: int) -> List[Tuple[str, int]]:
        """Extract and prioritize links from the page."""
        if current_depth >= self.max_depth:
            return []
            
        links = []
        seen_urls = set()  # To avoid duplicates within the same page
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(current_url, href)
            
            # Skip already processed URLs
            if absolute_url in seen_urls or absolute_url in self.visited_urls:
                continue
                
            seen_urls.add(absolute_url)
                
            # Check if URL is valid for crawling
            if self.is_valid_url(absolute_url):
                # Calculate priority score for this URL
                priority = self._calculate_url_priority(absolute_url, current_depth + 1)
                self.url_scores[absolute_url] = priority
                
                links.append((absolute_url, current_depth + 1))
        
        # Sort links by priority score (highest first)
        links.sort(key=lambda x: self.url_scores.get(x[0], 0), reverse=True)
        return links

    def _extract_page_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from the page to determine its relevance."""
        metadata = {
            'title': '',
            'headings': [],
            'content_length': 0,
            'has_forms': False,
            'has_product_info': False,
            'has_pricing': False,
            'has_case_study': False,
        }
        
        # Extract title
        if soup.title:
            metadata['title'] = soup.title.string
        
        # Extract headings
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            if heading.text.strip():
                metadata['headings'].append(heading.text.strip())
        
        # Check for forms (often not relevant for battlecards)
        metadata['has_forms'] = len(soup.find_all('form')) > 0
        
        # Check for product information
        product_indicators = ['price', 'pricing', 'feature', 'product', 'service', 'solution', 'platform']
        content_text = soup.get_text().lower()
        metadata['content_length'] = len(content_text)
        
        metadata['has_product_info'] = any(indicator in content_text for indicator in product_indicators)
        metadata['has_pricing'] = 'price' in content_text or 'pricing' in content_text
        metadata['has_case_study'] = 'case study' in content_text or 'success story' in content_text or 'customer story' in content_text
        
        return metadata

    def _calculate_content_relevance(self, metadata: Dict, soup: BeautifulSoup) -> float:
        """Calculate the relevance score of the page content for battlecards."""
        relevance_score = 0.0
        
        # Higher weightage for case studies and success stories
        if metadata['has_case_study']:
            relevance_score += 3.0
            
        # Product or solution pages are highly relevant
        if metadata['has_product_info']:
            relevance_score += 2.0
            
        # Pricing information can be useful
        if metadata['has_pricing']:
            relevance_score += 1.5
            
        # Form pages are usually less relevant (contact forms, etc.)
        if metadata['has_forms']:
            relevance_score -= 1.0
            
        # Longer content might be more informative (up to a point)
        if 1000 <= metadata['content_length'] <= 10000:
            relevance_score += 1.0
            
        # Check for relevant keywords in headings
        relevant_heading_keywords = ['solution', 'product', 'service', 'feature', 'benefit', 
                                    'case study', 'success', 'customer', 'client', 'result']
        
        for heading in metadata['headings']:
            heading_lower = heading.lower()
            if any(keyword in heading_lower for keyword in relevant_heading_keywords):
                relevance_score += 0.5
                
        # Check page structure for sections that suggest battlecard-relevant content
        if soup.find_all(['table', 'ul', 'ol']):  # Lists and tables often contain good structured info
            relevance_score += 0.5
            
        return relevance_score

    def clean_text(self, soup: BeautifulSoup) -> str:
        """Clean the page content and extract text, removing boilerplate elements."""
        # Remove non-content elements
        for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.decompose()
        
        # Remove common non-content classes and IDs
        non_content_selectors = [
            ".cookie-banner", ".newsletter-signup", ".social-share", 
            ".related-posts", ".advertisement", "#cookie-notice",
            ".popup", ".modal", ".sidebar", ".widget"
        ]
        
        for selector in non_content_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Get clean text
        text = soup.get_text(separator='\n', strip=True)
        
        # Remove excessive whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text

    def crawl(self) -> Dict[str, Dict]:
        """
        Crawl the website starting from the base URL with advanced prioritization.
        
        Returns:
            Dictionary mapping URLs to their text content and metadata.
        """
        page_count = 0
        
        logger.info(f"Starting crawl of {self.base_url}")
        logger.info(f"Max pages: {self.max_pages}, Max depth: {self.max_depth}")
        
        while self.url_queue and page_count < self.max_pages:
            # Get URL with highest priority
            current_url, depth = self.url_queue.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            logger.info(f"Crawling: {current_url} (depth {depth})")
            self.visited_urls.add(current_url)
            
            try:
                response = requests.get(current_url, headers=self.headers, timeout=15)
                response.raise_for_status()
                
                # Skip non-HTML content
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    logger.info(f"Skipping non-HTML content: {current_url}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract metadata for relevance scoring
                metadata = self._extract_page_metadata(soup)
                relevance_score = self._calculate_content_relevance(metadata, soup)
                self.content_relevance[current_url] = relevance_score
                
                logger.info(f"Page relevance score: {relevance_score}")
                
                # Extract and store text content if relevant
                if relevance_score > 0:  # Only store relevant content
                    text_content = self.clean_text(soup)
                    if text_content:  # Only store if there's actual content
                        page_title = metadata['title'] or current_url
                        self.page_contents[current_url] = {
                            'title': page_title,
                            'content': text_content,
                            'relevance': relevance_score,
                            'depth': depth,
                            'metadata': metadata
                        }
                        page_count += 1
                
                # Extract links for further crawling
                links = self.extract_links(soup, current_url, depth)
                
                # Add new links to the queue
                for link, link_depth in links:
                    if link not in self.visited_urls and not any(link == url for url, _ in self.url_queue):
                        self.url_queue.append((link, link_depth))
                
                # Sort the queue by priority score
                self.url_queue.sort(key=lambda x: self.url_scores.get(x[0], 0), reverse=True)
                
                # Be respectful with a delay
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error crawling {current_url}: {str(e)}")
        
        logger.info(f"Crawl completed. Processed {len(self.visited_urls)} URLs, stored {len(self.page_contents)} pages")
        return self.page_contents

    def get_combined_text(self) -> str:
        """Get all crawled text combined into a single string, ordered by relevance."""
        combined_text = []
        
        # Sort pages by relevance score (highest first)
        sorted_pages = sorted(
            self.page_contents.items(), 
            key=lambda x: x[1]['relevance'], 
            reverse=True
        )
        
        for url, data in sorted_pages:
            combined_text.append(f"--- Page: {data['title']} ({url}) ---")
            combined_text.append(data['content'])
            combined_text.append("\n")
        
        return "\n".join(combined_text)
    
    def get_crawl_summary(self) -> Dict:
        """Return a summary of the crawl process."""
        return {
            'pages_crawled': len(self.visited_urls),
            'pages_stored': len(self.page_contents),
            'max_depth_reached': max(data['depth'] for _, data in self.page_contents.items()) if self.page_contents else 0,
            'top_relevant_pages': [
                {'url': url, 'title': data['title'], 'relevance': data['relevance']}
                for url, data in sorted(self.page_contents.items(), key=lambda x: x[1]['relevance'], reverse=True)[:5]
            ]
        }