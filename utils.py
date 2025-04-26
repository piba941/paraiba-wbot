import xml.etree.ElementTree as ET
from models import db, Order

def parse_xml_and_update_db(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for row in root.findall('row'):
        order_no = row.find('Order_no').text
        first_name = row.find('FirstName').text
        last_name = row.find('LastName').text
        mobile_number = row.find('mobile').text
        order_details = row.find('order_details').text
        order_status = row.find('Order_status').text
        
        # Check if order already exists
        existing_order = Order.query.filter_by(order_no=order_no).first()
        
        if not existing_order:
            new_order = Order(
                order_no=order_no,
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile_number,
                order_details=order_details,
                order_status=order_status
            )
            db.session.add(new_order)
        else:
            # update existing
            existing_order.order_status = order_status
            existing_order.order_details = order_details

    db.session.commit()
