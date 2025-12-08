from decimal import Decimal

def calculate_farmer_bill_totals(items, other_expense=0, discount=0):
    """
    Calculate totals for farmer bill (no GST)
    
    Args:
        items: List of dicts with 'weight' and 'price'
        other_expense: Additional expense amount
        discount: Discount amount
    
    Returns:
        dict with item_totals and final_total
    """
    item_totals = []
    for item in items:
        weight = Decimal(str(item.get('weight', 0)))
        price = Decimal(str(item.get('price', 0)))
        item_total = weight * price
        item_totals.append(float(item_total))
        item['item_total'] = float(item_total)
    
    sub_total = Decimal(str(sum(item_totals)))
    other_expense = Decimal(str(other_expense))
    discount = Decimal(str(discount))
    final_total = sub_total + other_expense - discount
    
    return {
        'item_totals': item_totals,
        'final_total': float(final_total)
    }

def calculate_dealer_bill_totals(items, other_expense=0, discount=0, gst_percentage=18):
    """
    Calculate totals for dealer bill (with GST)
    
    Args:
        items: List of dicts with 'weight' and 'price'
        other_expense: Additional expense amount
        discount: Discount amount
        gst_percentage: GST percentage (default 18)
    
    Returns:
        dict with item_totals, sub_total, gst_amount, cgst, sgst, grand_total
    """
    item_totals = []
    for item in items:
        weight = Decimal(str(item.get('weight', 0)))
        price = Decimal(str(item.get('price', 0)))
        item_total = weight * price
        item_totals.append(float(item_total))
        item['item_total'] = float(item_total)
    
    sub_total = Decimal(str(sum(item_totals)))
    other_expense = Decimal(str(other_expense))
    discount = Decimal(str(discount))
    sub_total_after_expenses = sub_total + other_expense - discount
    
    gst_percentage = Decimal(str(gst_percentage))
    gst_amount = (sub_total_after_expenses * gst_percentage) / Decimal('100')
    cgst = gst_amount / Decimal('2')
    sgst = gst_amount / Decimal('2')
    grand_total = sub_total_after_expenses + gst_amount
    
    return {
        'item_totals': item_totals,
        'sub_total': float(sub_total),
        'gst_amount': float(gst_amount),
        'cgst': float(cgst),
        'sgst': float(sgst),
        'grand_total': float(grand_total)
    }

