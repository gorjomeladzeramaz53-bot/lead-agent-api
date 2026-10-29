import logging
import httpx
from bs4 import BeautifulSoup
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WebScraper:
    """Resilient asynchronous web scraper using httpx and BeautifulSoup."""

    def __init__(self) -> None:
        # Use config settings if available, with safe production fallbacks
        self.timeout = getattr(settings, "SCRAPER_TIMEOUT", 10.0)
        self.user_agent = getattr(settings, "SCRAPER_USER_AGENT", "LeadAgentBot/1.0")

    async def fetch_page_text(self, url: str) -> str:
        """
        Asynchronously fetches HTML content from a given URL, 
        cleans up unnecessary tags (scripts, styles, etc.), and extracts raw text.
        """
        headers = {"User-Agent": self.user_agent}
        
        # Ensure the URL includes a scheme
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        logger.info(f"Starting web scraping for URL: {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                html_content = response.text
                
                # Parse HTML content
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Remove boilerplate/unwanted tags to keep text clean for LLM analysis
                for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                    element.decompose()

                # Extract plain text with spaces
                raw_text = soup.get_text(separator=" ", strip=True)
                logger.info(f"Successfully scraped {url} (Extracted characters: {len(raw_text)})")
                return raw_text

        except httpx.TimeoutException:
            logger.error(f"Timeout occurred while scraping URL: {url}")
            raise RuntimeError(f"Scraping operation timed out for URL: {url}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            raise RuntimeError(f"HTTP error {e.response.status_code} received while scraping {url}")
        except Exception as e:
            logger.error(f"Unexpected error while scraping {url}: {str(e)}")
            raise RuntimeError(f"Failed to scrape URL {url}: {str(e)}")