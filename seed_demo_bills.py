"""
Seed script to add 10 demo farmer bills and 10 demo dealer bills
"""
from app import create_app, db
from app.models import FarmerBill, FarmerBillItem, DealerBill, DealerBillItem
from datetime import datetime, timedelta
import random
import uuid

app = create_app()

# Sample data
farmer_names = [
    "Ramesh Kumar", "Suresh Patel", "Mahesh Singh", "Rajesh Sharma", 
    "Dinesh Yadav", "Naresh Gupta", "Mukesh Verma", "Rakesh Jain",
    "Lokesh Pandey", "Hitesh Malhotra"
]

dealer_names = [
    "Anil Traders", "Bharat Enterprises", "Chandan Store", "Diamond Corporation",
    "Eagle Distributors", "Fortune Suppliers", "Galaxy Traders", "Hindustan Merchants",
    "Ideal Wholesale", "Jai Hind Trading"
]

items_list = [
    {"name": "Wheat", "hsn": "1001"},
    {"name": "Rice", "hsn": "1006"},
    {"name": "Corn", "hsn": "1005"},
    {"name": "Barley", "hsn": "1003"},
    {"name": "Soybean", "hsn": "1201"},
    {"name": "Mustard", "hsn": "1205"},
    {"name": "Cotton", "hsn": "5201"},
    {"name": "Jute", "hsn": "5303"},
    {"name": "Pulses", "hsn": "0713"},
    {"name": "Groundnut", "hsn": "1202"}
]

def generate_bill_id(prefix, index):
    """Generate bill ID with date and sequence"""
    today = datetime.now()
    return f"{prefix}/{today.strftime('%y%m')}/{str(index+1).zfill(4)}"

def create_farmer_bills():
    """Create 10 demo farmer bills"""
    print("\n📝 Creating Farmer Bills...")
    
    for i in range(10):
        # Create bills for the last 10 days
        bill_date = datetime.now().date() - timedelta(days=9-i)
        
        bill = FarmerBill(
            id=uuid.uuid4(),
            bill_id=generate_bill_id("FB", i),
            date=bill_date,
            customer_name=farmer_names[i],
            other_expense=random.choice([0, 50, 100, 150]),
            discount=random.choice([0, 100, 200, 300]),
            final_total=0  # Will calculate after items
        )
        
        # Add 2-4 random items per bill
        num_items = random.randint(2, 4)
        bill_items_total = 0
        
        for j in range(num_items):
            item_data = random.choice(items_list)
            weight = random.randint(50, 500)
            price = random.randint(20, 50)
            item_total = weight * price
            bill_items_total += item_total
            
            bill_item = FarmerBillItem(
                id=uuid.uuid4(),
                farmer_bill_id=bill.id,
                item=item_data["name"],
                hsn_code=item_data["hsn"],
                quantity_bags=random.randint(1, 10),
                weight=weight,
                price=price,
                item_total=item_total
            )
            bill.items.append(bill_item)
        
        # Calculate final total
        bill.final_total = bill_items_total + bill.other_expense - bill.discount
        
        db.session.add(bill)
        print(f"✓ Created Farmer Bill: {bill.bill_id} - {bill.customer_name} - ₹{bill.final_total}")
    
    db.session.commit()
    print("✅ All Farmer Bills created successfully!\n")

def create_dealer_bills():
    """Create 10 demo dealer bills"""
    print("📝 Creating Dealer Bills...")
    
    for i in range(10):
        # Create bills for the last 10 days
        bill_date = datetime.now().date() - timedelta(days=9-i)
        
        gst_percentage = 18
        other_expense = random.choice([0, 100, 200, 300])
        discount = random.choice([0, 200, 400, 500])
        
        bill = DealerBill(
            id=uuid.uuid4(),
            bill_id=generate_bill_id("DB", i),
            date=bill_date,
            customer_name=dealer_names[i],
            other_expense=other_expense,
            discount=discount,
            gst_percentage=gst_percentage,
            gst_amount=0,
            cgst=0,
            sgst=0,
            grand_total=0  # Will calculate after items
        )
        
        # Add 2-4 random items per bill
        num_items = random.randint(2, 4)
        bill_items_total = 0
        
        for j in range(num_items):
            item_data = random.choice(items_list)
            weight = random.randint(50, 500)
            price = random.randint(30, 60)
            item_total = weight * price
            bill_items_total += item_total
            
            bill_item = DealerBillItem(
                id=uuid.uuid4(),
                dealer_bill_id=bill.id,
                item=item_data["name"],
                hsn_code=item_data["hsn"],
                quantity_bags=random.randint(1, 10),
                weight=weight,
                price=price,
                item_total=item_total
            )
            bill.items.append(bill_item)
        
        # Calculate GST and totals
        subtotal = bill_items_total + other_expense - discount
        gst_amount = subtotal * (gst_percentage / 100)
        
        bill.gst_amount = round(gst_amount, 2)
        bill.cgst = round(gst_amount / 2, 2)
        bill.sgst = round(gst_amount / 2, 2)
        bill.grand_total = subtotal + gst_amount
        
        db.session.add(bill)
        print(f"✓ Created Dealer Bill: {bill.bill_id} - {bill.customer_name} - ₹{bill.grand_total}")
    
    db.session.commit()
    print("✅ All Dealer Bills created successfully!\n")

def main():
    """Main function to seed demo bills"""
    with app.app_context():
        print("\n" + "="*60)
        print("🌱 SEEDING DEMO BILLS")
        print("="*60)
        
        try:
            create_farmer_bills()
            create_dealer_bills()
            
            # Show summary
            farmer_count = FarmerBill.query.count()
            dealer_count = DealerBill.query.count()
            
            print("="*60)
            print("📊 DATABASE SUMMARY")
            print("="*60)
            print(f"Total Farmer Bills: {farmer_count}")
            print(f"Total Dealer Bills: {dealer_count}")
            print("="*60)
            print("✨ Seeding completed successfully!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    main()
