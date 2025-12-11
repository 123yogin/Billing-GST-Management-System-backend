from flask import current_app
from jinja2 import Template
from xhtml2pdf import pisa
from io import BytesIO

FARMER_BILL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: #000; }
        .header { text-align: center; margin-bottom: 30px; }
        .bill-info { margin-bottom: 20px; }
        .bill-info table { width: 100%; border-collapse: collapse; }
        .bill-info td { padding: 5px; }
        .items-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .items-table th, .items-table td { border: 1px solid #000; padding: 8px; text-align: left; }
        .items-table th { background-color: #f0f0f0; }
        .items-table .text-right { text-align: right; }
        .totals { margin-top: 20px; margin-left: auto; width: 300px; }
        .totals table { border-collapse: collapse; width: 100%; }
        .totals td { padding: 5px 15px; }
        .totals .label { font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>FARMER BILL</h1>
    </div>
    <div class="bill-info">
        <table>
            <tr><td><strong>Bill ID:</strong></td><td>{{ bill.bill_id }}</td></tr>
            <tr><td><strong>Date:</strong></td><td>{{ bill.date }}</td></tr>
            <tr><td><strong>Customer Name:</strong></td><td>{{ bill.customer_name }}</td></tr>
        </table>
    </div>
    <table class="items-table">
        <thead>
            <tr>
                <th>Item</th>
                <th>Weight</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {% for item in bill.items %}
            <tr>
                <td>{{ item.item }}</td>
                <td class="text-right">{{ item.weight }}</td>
                <td class="text-right">{{ item.price }}</td>
                <td class="text-right">{{ item.item_total }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <div class="totals">
        <table>
            <tr><td class="label">Other Expense:</td><td>{{ bill.other_expense }}</td></tr>
            <tr><td class="label">Discount:</td><td>{{ bill.discount }}</td></tr>
            <tr><td class="label"><strong>Final Total:</strong></td><td><strong>{{ bill.final_total }}</strong></td></tr>
        </table>
    </div>
</body>
</html>
"""

DEALER_BILL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: #000; }
        .header { text-align: center; margin-bottom: 30px; }
        .bill-info { margin-bottom: 20px; }
        .bill-info table { width: 100%; border-collapse: collapse; }
        .bill-info td { padding: 5px; }
        .items-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .items-table th, .items-table td { border: 1px solid #000; padding: 8px; text-align: left; }
        .items-table th { background-color: #f0f0f0; }
        .items-table .text-right { text-align: right; }
        .totals { margin-top: 20px; margin-left: auto; width: 300px; }
        .totals table { border-collapse: collapse; width: 100%; }
        .totals td { padding: 5px 15px; }
        .totals .label { font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DEALER BILL</h1>
    </div>
    <div class="bill-info">
        <table>
            <tr><td><strong>Bill ID:</strong></td><td>{{ bill.bill_id }}</td></tr>
            <tr><td><strong>Date:</strong></td><td>{{ bill.date }}</td></tr>
            <tr><td><strong>Customer Name:</strong></td><td>{{ bill.customer_name }}</td></tr>
        </table>
    </div>
    <table class="items-table">
        <thead>
            <tr>
                <th>Item</th>
                <th>Weight</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {% for item in bill.items %}
            <tr>
                <td>{{ item.item }}</td>
                <td class="text-right">{{ item.weight }}</td>
                <td class="text-right">{{ item.price }}</td>
                <td class="text-right">{{ item.item_total }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <div class="totals">
        <table>
            <tr><td class="label">Other Expense:</td><td>{{ bill.other_expense }}</td></tr>
            <tr><td class="label">Discount:</td><td>{{ bill.discount }}</td></tr>
            <tr><td class="label">Sub Total:</td><td>{{ sub_total }}</td></tr>
            <tr><td class="label">GST ({{ bill.gst_percentage }}%):</td><td>{{ bill.gst_amount }}</td></tr>
            <tr><td class="label">CGST:</td><td>{{ bill.cgst }}</td></tr>
            <tr><td class="label">SGST:</td><td>{{ bill.sgst }}</td></tr>
            <tr><td class="label"><strong>Grand Total:</strong></td><td><strong>{{ bill.grand_total }}</strong></td></tr>
        </table>
    </div>
</body>
</html>
"""

def generate_farmer_bill_pdf(bill_data):
    """Generate PDF for farmer bill"""
    template = Template(FARMER_BILL_TEMPLATE)
    html = template.render(bill=bill_data)
    pdf_buffer = BytesIO()
    pisa.CreatePDF(html, dest=pdf_buffer, encoding='utf-8')
    pdf_buffer.seek(0)
    return pdf_buffer

def generate_dealer_bill_pdf(bill_data):
    """Generate PDF for dealer bill"""
    # Calculate sub_total for display (values are already formatted as strings)
    # Parse them back to float for calculation
    item_totals = sum(float(item['item_total']) for item in bill_data['items'])
    other_expense = float(bill_data['other_expense'])
    discount = float(bill_data['discount'])
    sub_total = item_totals + other_expense - discount
    template = Template(DEALER_BILL_TEMPLATE)
    html = template.render(bill=bill_data, sub_total=f"{sub_total:.2f}")
    pdf_buffer = BytesIO()
    pisa.CreatePDF(html, dest=pdf_buffer, encoding='utf-8')
    pdf_buffer.seek(0)
    return pdf_buffer

