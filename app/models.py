from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Date, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class FarmerBill(db.Model):
    __tablename__ = 'farmer_bills'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bill_id = Column(String, unique=True, nullable=False)
    date = Column(Date, nullable=False)
    customer_name = Column(Text, nullable=False)
    other_expense = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    final_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship('FarmerBillItem', backref='farmer_bill', cascade='all, delete-orphan', lazy=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'bill_id': self.bill_id,
            'date': self.date.isoformat() if self.date else None,
            'customer_name': self.customer_name,
            'other_expense': float(self.other_expense) if self.other_expense else 0,
            'discount': float(self.discount) if self.discount else 0,
            'final_total': float(self.final_total) if self.final_total else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class FarmerBillItem(db.Model):
    __tablename__ = 'farmer_bill_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_bill_id = Column(UUID(as_uuid=True), ForeignKey('farmer_bills.id', ondelete='CASCADE'), nullable=False)
    item = Column(Text, nullable=False)
    weight = Column(Numeric(10, 2), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    item_total = Column(Numeric(10, 2), nullable=False)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'farmer_bill_id': str(self.farmer_bill_id),
            'item': self.item,
            'weight': float(self.weight) if self.weight else 0,
            'price': float(self.price) if self.price else 0,
            'item_total': float(self.item_total) if self.item_total else 0
        }

class DealerBill(db.Model):
    __tablename__ = 'dealer_bills'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bill_id = Column(String, unique=True, nullable=False)
    date = Column(Date, nullable=False)
    customer_name = Column(Text, nullable=False)
    other_expense = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    gst_percentage = Column(Numeric(5, 2), default=18)
    gst_amount = Column(Numeric(10, 2), default=0)
    cgst = Column(Numeric(10, 2), default=0)
    sgst = Column(Numeric(10, 2), default=0)
    grand_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship('DealerBillItem', backref='dealer_bill', cascade='all, delete-orphan', lazy=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'bill_id': self.bill_id,
            'date': self.date.isoformat() if self.date else None,
            'customer_name': self.customer_name,
            'other_expense': float(self.other_expense) if self.other_expense else 0,
            'discount': float(self.discount) if self.discount else 0,
            'gst_percentage': float(self.gst_percentage) if self.gst_percentage else 18,
            'gst_amount': float(self.gst_amount) if self.gst_amount else 0,
            'cgst': float(self.cgst) if self.cgst else 0,
            'sgst': float(self.sgst) if self.sgst else 0,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class DealerBillItem(db.Model):
    __tablename__ = 'dealer_bill_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_bill_id = Column(UUID(as_uuid=True), ForeignKey('dealer_bills.id', ondelete='CASCADE'), nullable=False)
    item = Column(Text, nullable=False)
    weight = Column(Numeric(10, 2), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    item_total = Column(Numeric(10, 2), nullable=False)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'dealer_bill_id': str(self.dealer_bill_id),
            'item': self.item,
            'weight': float(self.weight) if self.weight else 0,
            'price': float(self.price) if self.price else 0,
            'item_total': float(self.item_total) if self.item_total else 0
        }

