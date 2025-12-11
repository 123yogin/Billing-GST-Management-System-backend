from app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Date, Numeric, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
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
    
    # New Invoice Fields
    transport_mode = Column(String)
    vehicle_number = Column(String)
    supply_date = Column(DateTime)
    place_of_supply = Column(String)
    
    receiver_address = Column(Text)
    receiver_state = Column(String)
    receiver_state_code = Column(String)
    receiver_gstin = Column(String)
    
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
            'discount': float(self.discount) if self.discount else 0,
            'final_total': float(self.final_total) if self.final_total else 0,
            
            'transport_mode': self.transport_mode,
            'vehicle_number': self.vehicle_number,
            'supply_date': self.supply_date.isoformat() if self.supply_date else None,
            'place_of_supply': self.place_of_supply,
            'receiver_address': self.receiver_address,
            'receiver_state': self.receiver_state,
            'receiver_state_code': self.receiver_state_code,
            'receiver_gstin': self.receiver_gstin,
            
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
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
    
    # New Invoice Fields
    transport_mode = Column(String)
    vehicle_number = Column(String)
    supply_date = Column(DateTime)
    place_of_supply = Column(String)
    
    receiver_address = Column(Text)
    receiver_state = Column(String)
    receiver_state_code = Column(String)
    receiver_gstin = Column(String)
    
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
            
            'transport_mode': self.transport_mode,
            'vehicle_number': self.vehicle_number,
            'supply_date': self.supply_date.isoformat() if self.supply_date else None,
            'place_of_supply': self.place_of_supply,
            'receiver_address': self.receiver_address,
            'receiver_state': self.receiver_state,
            'receiver_state_code': self.receiver_state_code,
            'receiver_gstin': self.receiver_gstin,
            
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class FarmerBillItem(db.Model):
    __tablename__ = 'farmer_bill_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_bill_id = Column(UUID(as_uuid=True), ForeignKey('farmer_bills.id', ondelete='CASCADE'), nullable=False)
    item = Column(Text, nullable=False)
    hsn_code = Column(String)
    quantity_bags = Column(Integer, default=0)
    weight = Column(Numeric(10, 2), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    item_total = Column(Numeric(10, 2), nullable=False)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'farmer_bill_id': str(self.farmer_bill_id),
            'item': self.item,
            'hsn_code': self.hsn_code,
            'quantity_bags': self.quantity_bags,
            'weight': float(self.weight) if self.weight else 0,
            'price': float(self.price) if self.price else 0,
            'item_total': float(self.item_total) if self.item_total else 0
        }

class DealerBillItem(db.Model):
    __tablename__ = 'dealer_bill_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_bill_id = Column(UUID(as_uuid=True), ForeignKey('dealer_bills.id', ondelete='CASCADE'), nullable=False)
    item = Column(Text, nullable=False)
    hsn_code = Column(String)
    quantity_bags = Column(Integer, default=0)
    weight = Column(Numeric(10, 2), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    item_total = Column(Numeric(10, 2), nullable=False)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'dealer_bill_id': str(self.dealer_bill_id),
            'item': self.item,
            'hsn_code': self.hsn_code,
            'quantity_bags': self.quantity_bags,
            'weight': float(self.weight) if self.weight else 0,
            'price': float(self.price) if self.price else 0,
            'item_total': float(self.item_total) if self.item_total else 0
        }

# ============ DEALER MANAGEMENT ============

class Dealer(db.Model):
    __tablename__ = 'dealers'
    
    dealer_id = Column(Integer, db.Sequence('dealer_id_seq'), unique=True, nullable=False, server_default=db.text("nextval('dealer_id_seq')"))
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    gstin = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'dealer_id': self.dealer_id,
            'id': str(self.id),
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'gstin': self.gstin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============ INTEREST CALCULATION MODELS ============

class Deal(db.Model):
    __tablename__ = 'deals'
    
    deal_id = Column(Integer, primary_key=True, autoincrement=True)
    dealer_id = Column(UUID(as_uuid=True), ForeignKey('dealers.id', ondelete='SET NULL'), nullable=True)
    customer_name = Column(Text, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    interest_percentage = Column(Numeric(5, 2), default=0)
    deal_date = Column(Date, nullable=False)
    status = Column(String, default='active')  # 'active', 'closed'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    installments = relationship('Installment', backref='deal', cascade='all, delete-orphan', lazy=True, order_by='Installment.due_date')
    payments = relationship('Payment', backref='deal', cascade='all, delete-orphan', lazy=True, order_by='Payment.payment_date')
    
    def to_dict(self):
        return {
            'deal_id': self.deal_id,
            'dealer_id': str(self.dealer_id) if self.dealer_id else None,
            'customer_name': self.customer_name,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'interest_percentage': float(self.interest_percentage) if self.interest_percentage else 0,
            'deal_date': self.deal_date.isoformat() if self.deal_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'installments': [inst.to_dict() for inst in self.installments],
            'payments': [payment.to_dict() for payment in self.payments]
        }

class Installment(db.Model):
    __tablename__ = 'installments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(Integer, ForeignKey('deals.deal_id', ondelete='CASCADE'), nullable=False)
    due_date = Column(Date, nullable=False)
    days = Column(Integer, nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    pending_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    payment_allocations = relationship('PaymentAllocation', backref='installment', cascade='all, delete-orphan', lazy=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'deal_id': self.deal_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'days': self.days,
            'percentage': float(self.percentage) if self.percentage else 0,
            'amount': float(self.amount) if self.amount else 0,
            'pending_amount': float(self.pending_amount) if self.pending_amount else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(Integer, ForeignKey('deals.deal_id', ondelete='CASCADE'), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String, default='installment')  # 'installment', 'interest', 'principal'
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    allocations = relationship('PaymentAllocation', backref='payment', cascade='all, delete-orphan', lazy=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'deal_id': self.deal_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'amount': float(self.amount) if self.amount else 0,
            'type': self.type,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'allocations': [alloc.to_dict() for alloc in self.allocations]
        }

class PaymentAllocation(db.Model):
    __tablename__ = 'payment_allocations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey('payments.id', ondelete='CASCADE'), nullable=False)
    installment_id = Column(UUID(as_uuid=True), ForeignKey('installments.id', ondelete='CASCADE'), nullable=False)
    allocated_amount = Column(Numeric(10, 2), nullable=False)
    interest_amount = Column(Numeric(10, 2), default=0)  # Realized interest for this allocation
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'payment_id': str(self.payment_id),
            'installment_id': str(self.installment_id),
            'allocated_amount': float(self.allocated_amount) if self.allocated_amount else 0,
            'interest_amount': float(self.interest_amount) if self.interest_amount else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Item(db.Model):
    __tablename__ = 'items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    hsn_code = Column(String)
    price = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'hsn_code': self.hsn_code,
            'price': float(self.price) if self.price else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
