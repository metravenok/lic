from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    sam_account_name: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    is_admin: bool = False


class UserRead(BaseModel):
    id: int
    sam_account_name: str
    display_name: Optional[str]
    email: Optional[str]
    department: Optional[str]
    is_admin: bool

    class Config:
        from_attributes = True


class VendorCreate(BaseModel):
    name: str
    homepage: Optional[str] = None
    notes: Optional[str] = None


class VendorRead(VendorCreate):
    id: int

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    vendor_id: Optional[int] = None
    notes: Optional[str] = None


class ProductRead(ProductCreate):
    id: int

    class Config:
        from_attributes = True


class LicenseCreate(BaseModel):
    product_id: int
    license_key: Optional[str] = None
    license_type: str = Field(default="per_seat")
    seat_count: int = 1
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    maintenance_end_date: Optional[date] = None
    purchase_order_id: Optional[int] = None
    owner_user_id: Optional[int] = None
    cost_total: Optional[float] = None
    currency: Optional[str] = None
    notes: Optional[str] = None


class LicenseRead(LicenseCreate):
    id: int

    class Config:
        from_attributes = True


class AssignmentCreate(BaseModel):
    license_id: int
    assigned_to_user_id: int
    assigned_machine: Optional[str] = None
    due_back_at: Optional[datetime] = None


class AssignmentRead(AssignmentCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


class PurchaseOrderCreate(BaseModel):
    number: str
    vendor_id: Optional[int] = None
    purchaser_user_id: Optional[int] = None
    requestor_user_id: Optional[int] = None
    requested_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    total_cost: Optional[float] = None
    currency: Optional[str] = None
    memo: Optional[str] = None


class PurchaseOrderRead(PurchaseOrderCreate):
    id: int

    class Config:
        from_attributes = True


class MemoCreate(BaseModel):
    related_type: str
    related_id: int
    content: str


class MemoRead(MemoCreate):
    id: int
    author_user_id: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(UserRead):
    pass