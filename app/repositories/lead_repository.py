from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.lead import LeadModel
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadRepository:
    """Repository for handling database operations related to leads."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, lead_id: int) -> LeadModel | None:
        """Fetch a single lead by its ID."""
        result = await self.db.execute(select(LeadModel).where(LeadModel.id == lead_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[LeadModel]:
        """Fetch a paginated list of leads."""
        result = await self.db.execute(select(LeadModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, lead_in: LeadCreate) -> LeadModel:
        """Create a new lead record."""
        db_lead = LeadModel(
            company_name=lead_in.company_name,
            website=lead_in.website,
            email=lead_in.email,
            phone=lead_in.phone,
            status=lead_in.status,
            notes=lead_in.notes,
        )
        self.db.add(db_lead)
        await self.db.flush()
        await self.db.refresh(db_lead)
        return db_lead

    async def update(self, db_lead: LeadModel, lead_in: LeadUpdate) -> LeadModel:
        """Update an existing lead record."""
        update_data = lead_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_lead, field, value)
        
        self.db.add(db_lead)
        await self.db.flush()
        await self.db.refresh(db_lead)
        return db_lead

    async def delete(self, db_lead: LeadModel) -> None:
        """Delete a lead record."""
        await self.db.delete(db_lead)
        await self.db.flush()