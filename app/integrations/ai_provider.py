import logging
import json
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import get_settings
from app.schemas.lead import LeadCreate

logger = logging.getLogger(__name__)
settings = get_settings()


class AILeadAnalyzer:
    """Service layer that utilizes Google Gemini API to analyze scraped website text and extract lead details."""

    def __init__(self) -> None:
        # Initialize the official Google GenAI client using settings
        api_key = settings.GEMINI_API_KEY.get_secret_value() if settings.GEMINI_API_KEY else None
        self.client = genai.Client(api_key=api_key)
        self.model_name = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def analyze_text(self, scraped_text: str, website_url: str) -> LeadCreate:
        """
        Sends scraped website text to Gemini, forcing a structured response 
        that conforms to the Lead schema using Google GenAI Structured Outputs.
        """
        prompt = (
            f"Analyze the following website text extracted from '{website_url}' and extract company information. "
            f"Find the company name, contact email, phone number, and a short summary/notes about what the company does.\n\n"
            f"Website Text Content:\n{scraped_text[:15000]}"  # Truncate to fit token limits safely
        )

        logger.info(f"Sending text to Gemini model ({self.model_name}) for lead extraction...")

        try:
            # Using Google GenAI SDK with structured response schema configuration
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LeadCreate,
                    temperature=0.1,  # Low temperature for factual extraction
                ),
            )

            # Parse response text back into the LeadCreate Pydantic model
            response_text = response.text
            lead_data = json.loads(response_text)
            
            # Ensure website URL is correctly attached if missing
            if not lead_data.get("website"):
                lead_data["website"] = website_url

            logger.info(f"Successfully extracted lead via AI: {lead_data.get('company_name')}")
            return LeadCreate(**lead_data)

        except Exception as e:
            logger.error(f"Error during Gemini AI analysis: {str(e)}")
            raise RuntimeError(f"AI Lead Analysis failed: {str(e)}")