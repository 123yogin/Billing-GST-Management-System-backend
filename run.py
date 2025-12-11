from app import create_app, db
from app.models import FarmerBill, DealerBill, Item, Deal, Installment, Payment, PaymentAllocation, Dealer
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

app = create_app()

# enable migration
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
