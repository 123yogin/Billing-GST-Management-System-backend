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

@bp.route('/daily-ledger', methods=['GET'])
def get_daily_ledger():
    """Get daily ledger data with farmer and dealer bills for a specific date"""
    try:
        date_str = request.args.get('date')
        
        if not date_str:
            return {'error': 'Date parameter is required'}, 400
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get farmer bills for the date
        farmer_bills = FarmerBill.query.filter(
            FarmerBill.date == target_date
        ).order_by(FarmerBill.created_at).all()
        
        # Get dealer bills for the date
        dealer_bills = DealerBill.query.filter(
            DealerBill.date == target_date
        ).order_by(DealerBill.created_at).all()
        
        # Calculate totals
        farmer_total = sum(float(bill.final_total) for bill in farmer_bills)
        dealer_total = sum(float(bill.grand_total) for bill in dealer_bills)
        
        return {
            'date': date_str,
            'day': target_date.strftime('%A'),
            'farmer_bills': [bill.to_dict() for bill in farmer_bills],
            'dealer_bills': [bill.to_dict() for bill in dealer_bills],
            'farmer_total': farmer_total,
            'dealer_total': dealer_total
        }, 200
    except ValueError as e:
        return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400
    except Exception as e:
        return {'error': str(e)}, 400

@bp.route('/date-range', methods=['GET'])
def get_available_dates():
    """Get available date range for ledger navigation"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        query_farmer = db.session.query(FarmerBill.date)
        query_dealer = db.session.query(DealerBill.date)
        
        if from_date:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            query_farmer = query_farmer.filter(FarmerBill.date >= from_date_obj)
            query_dealer = query_dealer.filter(DealerBill.date >= from_date_obj)
        
        if to_date:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            query_farmer = query_farmer.filter(FarmerBill.date <= to_date_obj)
            query_dealer = query_dealer.filter(DealerBill.date <= to_date_obj)
        
        farmer_dates = [d[0] for d in query_farmer.distinct().all()]
        dealer_dates = [d[0] for d in query_dealer.distinct().all()]
        
        # Combine and get unique dates
        all_dates = sorted(set(farmer_dates + dealer_dates))
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in all_dates],
            'count': len(all_dates)
        }, 200
    except Exception as e:
        return {'error': str(e)}, 400

@bp.route('/bills', methods=['GET'])
def get_bills_report():
    """Get farmer and dealer bills for date range"""
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        if not from_date or not to_date:
            return {'error': 'Both from_date and to_date are required'}, 400
        
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        
        # Get farmer bills
        farmer_bills = FarmerBill.query.filter(
            FarmerBill.date >= from_date_obj,
            FarmerBill.date <= to_date_obj
        ).order_by(FarmerBill.date.desc()).all()
        
        # Get dealer bills
        dealer_bills = DealerBill.query.filter(
            DealerBill.date >= from_date_obj,
            DealerBill.date <= to_date_obj
        ).order_by(DealerBill.date.desc()).all()
        
        return {
            'farmer_bills': [bill.to_dict() for bill in farmer_bills],
            'dealer_bills': [bill.to_dict() for bill in dealer_bills],
            'farmer_total': sum(float(bill.final_total) for bill in farmer_bills),
            'dealer_total': sum(float(bill.grand_total) for bill in dealer_bills),
            'from_date': from_date,
            'to_date': to_date
        }, 200
    except Exception as e:
        return {'error': str(e)}, 400

