"""
Add 3 demo farmer bills on 12-12-2024
"""
from app import create_app, db
from app.models import FarmerBill, FarmerBillItem
from datetime import datetime
import random
import uuid

app = create_app()

# Sample data
farmer_names = ["Govind Prasad", "Shyam Lal", "Mohan Das"]

items_list = [
    {"name": "Wheat", "hsn": "1001"},
    {"name": "Rice", "hsn": "1006"},
    {"name": "Corn", "hsn": "1005"},
    {"name": "Barley", "hsn": "1003"},
    {"name": "Soybean", "hsn": "1201"},
]

def create_farmer_bills_for_date():
    """Create 3 farmer bills for 12-12-2024"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("📝 Adding 3 Farmer Bills for 12-12-2024")
        print("="*60 + "\n")
        
        try:
            target_date = datetime(2024, 12, 12).date()
            
            # Get the next bill number
            existing_bills = FarmerBill.query.filter(
                db.extract('year', FarmerBill.date) == 2024,
                db.extract('month', FarmerBill.date) == 12
            ).count()
            
            for i in range(3):
                bill_num = existing_bills + i + 1
                
                bill = FarmerBill(
                    id=uuid.uuid4(),
                    bill_id=f"FB/2412/{str(bill_num).zfill(4)}",
                    date=target_date,
                    customer_name=farmer_names[i],
                    other_expense=random.choice([0, 50, 100]),
                    discount=random.choice([0, 100, 200]),
                    final_total=0
                )
                
                # Add 2-3 items per bill
                num_items = random.randint(2, 3)
                bill_items_total = 0
                
                for j in range(num_items):
                    item_data = random.choice(items_list)
                    weight = random.randint(100, 300)
                    price = random.randint(25, 45)
                    item_total = weight * price
                    bill_items_total += item_total
                    
                    bill_item = FarmerBillItem(
                        id=uuid.uuid4(),
                        farmer_bill_id=bill.id,
                        item=item_data["name"],
                        hsn_code=item_data["hsn"],
                        quantity_bags=random.randint(2, 8),
                        weight=weight,
                        price=price,
                        item_total=item_total
                    )
                    bill.items.append(bill_item)
                
                bill.final_total = bill_items_total + bill.other_expense - bill.discount
                
                db.session.add(bill)
                print(f"✓ Created: {bill.bill_id} - {bill.customer_name} - ₹{bill.final_total}")
            
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ Successfully added 3 farmer bills for 12-12-2024!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_farmer_bills_for_date()
