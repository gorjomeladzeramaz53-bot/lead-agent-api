from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(lead_in: LeadCreate, db: AsyncSession = Depends(get_db)) -> LeadResponse:
    """Create a new lead."""
    service = LeadService(db)
    lead = await service.create_new_lead(lead_in)
    return lead


@router.get("/", response_model=list[LeadResponse], status_code=status.HTTP_200_OK)
async def list_leads(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> list[LeadResponse]:
    """Retrieve a paginated list of leads."""
    service = LeadService(db)
    leads = await service.get_leads_list(skip=skip, limit=limit)
    return leads


@router.get("/{lead_id}", response_model=LeadResponse, status_code=status.HTTP_200_OK)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)) -> LeadResponse:
    """Retrieve a specific lead by ID."""
    service = LeadService(db)
    lead = await service.get_lead_by_id(lead_id)
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse, status_code=status.HTTP_200_OK)
async def update_lead(lead_id: int, lead_in: LeadUpdate, db: AsyncSession = Depends(get_db)) -> LeadResponse:
    """Update an existing lead."""
    service = LeadService(db)
    lead = await service.update_lead(lead_id, lead_in)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a lead."""
    service = LeadService(db)
    await service.delete_lead(lead_id)
    return None
from pydantic import BaseModel, Field
from app.services.scraping_service import ScrapingOrchestratorService


class ScrapeRequest(BaseModel):
    url: str = Field(..., description="The website URL to scrape and analyze")


@router.post("/scrape", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def scrape_and_create_lead(
    payload: ScrapeRequest, db: AsyncSession = Depends(get_db)
) -> LeadResponse:
    """Trigger the end-to-end scraper and AI analysis pipeline for a given website URL."""
    orchestrator = ScrapingOrchestratorService(db)
    lead = await orchestrator.process_url_to_lead(payload.url)
    return lead