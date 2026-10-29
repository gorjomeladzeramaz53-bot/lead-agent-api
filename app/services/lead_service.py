from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.lead_repository import LeadRepository
from app.models.lead import LeadModel
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadService:
    """Service layer containing business logic for lead management."""

    def __init__(self, db: AsyncSession) -> None:
        self.repository = LeadRepository(db)

    async def get_lead_by_id(self, lead_id: int) -> LeadModel:
        """Fetch a lead by ID or raise a 404 error if not found."""
        lead = await self.repository.get_by_id(lead_id)
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with ID {lead_id} not found."
            )
        return lead

    async def get_leads_list(self, skip: int = 0, limit: int = 100) -> list[LeadModel]:
        """Fetch a paginated list of leads."""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create_new_lead(self, lead_in: LeadCreate) -> LeadModel:
        """Create a new lead with business rule validation if needed."""
        # Here you could add extra business logic (e.g., checking for duplicates)
        return await self.repository.create(lead_in)

    async def update_lead(self, lead_id: int, lead_in: LeadUpdate) -> LeadModel:
        """Update an existing lead after ensuring it exists."""
        db_lead = await self.get_lead_by_id(lead_id)
        return await self.repository.update(db_lead, lead_in)

    async def delete_lead(self, lead_id: int) -> None:
        """Delete a lead after ensuring it exists."""
        db_lead = await self.get_lead_by_id(lead_id)
        await self.repository.delete(db_lead)