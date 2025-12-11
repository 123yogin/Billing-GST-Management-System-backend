from app import create_app, db
from app.models import Item
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables: {tables}")
        
        if 'items' in tables:
            print("Table 'items' exists.")
            columns = [col['name'] for col in inspector.get_columns('items')]
            print(f"Columns in 'items': {columns}")
            
            # Try to insert
            print("Attempting to insert test item...")
            test_item = Item(name="Test Item Check", hsn_code="1234", price=100)
            db.session.add(test_item)
            db.session.commit()
            print("Successfully inserted test item")
            
            # Clean up
            db.session.delete(test_item)
            db.session.commit()
            print("Successfully cleaned up test item")
        else:
            print("Table 'items' DOES NOT EXIST!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
