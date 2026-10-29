import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.integrations.scraper import WebScraper
from app.integrations.ai_provider import AILeadAnalyzer
from app.services.lead_service import LeadService
from app.services.email_service import EmailService
from app.models.lead import LeadModel

logger = logging.getLogger(__name__)


class ScrapingOrchestratorService:
    """Orchestrates the end-to-end flow: Scrape -> AI Analysis -> Database Persistence -> Automated Email Outreach."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.scraper = WebScraper()
        self.ai_analyzer = AILeadAnalyzer()
        self.lead_service = LeadService(db)
        self.email_service = EmailService()

    async def process_url_to_lead(self, url: str) -> LeadModel:
        """
        Takes a website URL, scrapes its content, analyzes it with AI, 
        saves the extracted lead into the database, and triggers an automated email if an email exists.
        """
        logger.info(f"Starting orchestration pipeline for URL: {url}")

        # Step 1: Scrape the raw text from the website
        scraped_text = await self.scraper.fetch_page_text(url)

        # Step 2: Analyze the text using the AI provider to get structured Lead data
        lead_create_schema = await self.ai_analyzer.analyze_text(scraped_text, website_url=url)

        # Step 3: Save the extracted lead using the lead service/repository
        created_lead = await self.lead_service.create_new_lead(lead_create_schema)

        logger.info(f"Successfully orchestrated and stored lead ID {created_lead.id} for {url}")

        # Step 4: Trigger automated email outreach if email was found
        if created_lead.email:
            try:
                email_sent = await self.email_service.send_outreach_email(
                    recipient_email=created_lead.email,
                    company_name=created_lead.company_name,
                    summary=created_lead.notes,
                )
                if email_sent:
                    logger.info(f"Outreach email successfully dispatched for lead ID {created_lead.id}")
                else:
                    logger.warning(f"Outreach email dispatch returned False for lead ID {created_lead.id}")
            except Exception as e:
                # We log the email error but do not fail the whole scraping pipeline
                logger.error(f"Failed to send automated outreach email for lead ID {created_lead.id}: {str(e)}")
        else:
            logger.info(f"No email address found for lead ID {created_lead.id}. Skipping email outreach.")

        return created_lead