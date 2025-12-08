from app import create_app, db
from app.models import FarmerBill, FarmerBillItem, DealerBill, DealerBillItem
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        print("Database tables initialized")
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

