from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sam_account_name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)

    owned_licenses: Mapped[list[License]] = relationship(back_populates="owner_user", cascade="all,delete")  # type: ignore


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    homepage: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text())

    products: Mapped[list[SoftwareProduct]] = relationship(back_populates="vendor", cascade="all,delete")  # type: ignore


class SoftwareProduct(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text())

    vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"), nullable=True)
    vendor: Mapped[Optional[Vendor]] = relationship(back_populates="products")

    licenses: Mapped[list[License]] = relationship(back_populates="product", cascade="all,delete")  # type: ignore


from enum import Enum as PyEnum


class LicenseType(PyEnum):
    PER_SEAT = "per_seat"
    FLOATING = "floating"
    SUBSCRIPTION = "subscription"
    NETWORK = "network"
    CONCURRENT = "concurrent"


class License(Base):
    __tablename__ = "licenses"
    __table_args__ = (
        UniqueConstraint("product_id", "license_key", name="uq_product_license_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped[SoftwareProduct] = relationship(back_populates="licenses")

    license_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    license_type: Mapped[LicenseType] = mapped_column(Enum(LicenseType), default=LicenseType.PER_SEAT)
    seat_count: Mapped[int] = mapped_column(Integer, default=1)

    start_date: Mapped[Optional[date]] = mapped_column(Date())
    end_date: Mapped[Optional[date]] = mapped_column(Date(), index=True)
    maintenance_end_date: Mapped[Optional[date]] = mapped_column(Date())

    purchase_order_id: Mapped[int | None] = mapped_column(ForeignKey("purchase_orders.id"))
    purchase_order: Mapped[Optional[PurchaseOrder]] = relationship(back_populates="licenses")  # type: ignore

    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    owner_user: Mapped[Optional[User]] = relationship(back_populates="owned_licenses")

    cost_total: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(10))

    notes: Mapped[Optional[str]] = mapped_column(Text())

    assignments: Mapped[list[Assignment]] = relationship(back_populates="license", cascade="all,delete")  # type: ignore


class AssignmentStatus(PyEnum):
    ASSIGNED = "assigned"
    RETURNED = "returned"
    EXPIRED = "expired"


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    license_id: Mapped[int] = mapped_column(ForeignKey("licenses.id"))
    license: Mapped[License] = relationship(back_populates="assignments")

    assigned_to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assigned_to_user: Mapped[User] = relationship()

    assigned_machine: Mapped[Optional[str]] = mapped_column(String(255))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    due_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus), default=AssignmentStatus.ASSIGNED)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"))
    vendor: Mapped[Optional[Vendor]] = relationship()

    purchaser_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    requestor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    requested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    total_cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(10))

    memo: Mapped[Optional[str]] = mapped_column(Text())

    licenses: Mapped[list[License]] = relationship(back_populates="purchase_order")  # type: ignore


class Memo(Base):
    __tablename__ = "memos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[User] = relationship()

    related_type: Mapped[str] = mapped_column(String(50))  # e.g., license, product, purchase_order
    related_id: Mapped[int] = mapped_column(Integer)

    content: Mapped[str] = mapped_column(Text())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor: Mapped[Optional[User]] = relationship()

    action: Mapped[str] = mapped_column(String(100))
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[int] = mapped_column(Integer)

    before: Mapped[Optional[str]] = mapped_column(Text())
    after: Mapped[Optional[str]] = mapped_column(Text())