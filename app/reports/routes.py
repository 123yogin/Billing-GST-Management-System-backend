from flask import Blueprint, request, send_file
from app import db
from app.models import FarmerBill, DealerBill
from datetime import datetime
import pandas as pd
from io import BytesIO

bp = Blueprint('reports', __name__)

@bp.route('/farmer/excel', methods=['GET'])
def export_farmer_excel():
    """Export farmer bills to Excel"""
    try:
        month = request.args.get('month')
        year = request.args.get('year')
        
        query = FarmerBill.query
        
        if month and year:
            query = query.filter(
                db.extract('month', FarmerBill.date) == int(month),
                db.extract('year', FarmerBill.date) == int(year)
            )
        elif year:
            query = query.filter(db.extract('year', FarmerBill.date) == int(year))
        
        bills = query.order_by(FarmerBill.date.desc()).all()
        
        # Prepare data for Excel
        data = []
        for bill in bills:
            for item in bill.items:
                data.append({
                    'Bill ID': bill.bill_id,
                    'Date': bill.date.strftime('%Y-%m-%d'),
                    'Customer Name': bill.customer_name,
                    'Item': item.item,
                    'Weight': float(item.weight),
                    'Price': float(item.price),
                    'Item Total': float(item.item_total),
                    'Other Expense': float(bill.other_expense),
                    'Discount': float(bill.discount),
                    'Final Total': float(bill.final_total)
                })
        
        if not data:
            data = [{'Message': 'No data found for the selected period'}]
        
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Farmer Bills')
        output.seek(0)
        
        filename = f'farmer_bills_{month or "all"}_{year or "all"}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return {'error': str(e)}, 400

@bp.route('/dealer/excel', methods=['GET'])
def export_dealer_excel():
    """Export dealer bills to Excel with GST details"""
    try:
        month = request.args.get('month')
        year = request.args.get('year')
        
        query = DealerBill.query
        
        if month and year:
            query = query.filter(
                db.extract('month', DealerBill.date) == int(month),
                db.extract('year', DealerBill.date) == int(year)
            )
        elif year:
            query = query.filter(db.extract('year', DealerBill.date) == int(year))
        
        bills = query.order_by(DealerBill.date.desc()).all()
        
        # Prepare data for Excel
        data = []
        for bill in bills:
            for item in bill.items:
                data.append({
                    'Bill ID': bill.bill_id,
                    'Date': bill.date.strftime('%Y-%m-%d'),
                    'Customer Name': bill.customer_name,
                    'Item': item.item,
                    'Weight': float(item.weight),
                    'Price': float(item.price),
                    'Item Total': float(item.item_total),
                    'Other Expense': float(bill.other_expense),
                    'Discount': float(bill.discount),
                    'GST %': float(bill.gst_percentage),
                    'GST Amount': float(bill.gst_amount),
                    'CGST': float(bill.cgst),
                    'SGST': float(bill.sgst),
                    'Grand Total': float(bill.grand_total)
                })
        
        if not data:
            data = [{'Message': 'No data found for the selected period'}]
        
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dealer Bills')
        output.seek(0)
        
        filename = f'dealer_bills_{month or "all"}_{year or "all"}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return {'error': str(e)}, 400

