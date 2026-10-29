import datetime
from pydantic import BaseModel, EmailStr, Field


class LeadBase(BaseModel):
    """Base schema with shared attributes for leads."""
    company_name: str = Field(..., min_length=1, max_length=255, description="Name of the company")
    website: str | None = Field(None, max_length=500, description="Company website URL")
    email: EmailStr | None = Field(None, description="Contact email address")
    phone: str | None = Field(None, max_length=50, description="Contact phone number")
    status: str = Field(default="new", max_length=50, description="Lead processing status")
    notes: str | None = Field(None, description="Additional notes about the lead")


class LeadCreate(LeadBase):
    """Schema for creating a new lead (payload validation)."""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating an existing lead (all fields optional)."""
    company_name: str | None = Field(None, min_length=1, max_length=255)
    website: str | None = Field(None, max_length=500)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=50)
    notes: str | None = None


class LeadResponse(LeadBase):
    """Schema for returning a lead from the API (includes DB fields)."""
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read data directly from SQLAlchemy models