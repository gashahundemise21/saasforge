from datetime import datetime
from pydantic import BaseModel

class InvoiceResponse(BaseModel):
    id: str
    amount_due: int
    amount_paid: int
    amount_remaining: int
    status: str
    created: datetime
    hosted_invoice_url: str | None = None
    invoice_pdf: str | None = None

class SubscriptionDetailsResponse(BaseModel):
    id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    plan_id: str | None = None
    amount: int | None = None
    currency: str | None = None
