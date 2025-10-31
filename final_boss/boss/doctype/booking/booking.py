import frappe
import razorpay
import qrcode
import io
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request



# ---------------------------------------------------------------------
# BOOKING CLASS
# ---------------------------------------------------------------------
class Booking(Document):

    # Calculate total before saving
    def validate(self):
        self.total_amount = (self.price or 0) * (self.quantity or 0)

    def before_save(self):
        """Generate a QR code dynamically when event or attendee changes."""
        if not self.qr_code or self.has_value_changed('event') or self.has_value_changed('attendee'):
            self.generate_qr_code()

    def generate_qr_code(self):
        """Generate and attach QR Code to booking record."""
        qr_data = f"Booking ID: {self.name}"
        img = qrcode.make(qr_data)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_bytes = buf.getvalue()

        file_name = f"qr_code_{self.name}.png"
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "content": qr_bytes,
            "is_private": 0,
            "attached_to_doctype": self.doctype,
            "attached_to_name": self.name,
        })
        file_doc.save(ignore_permissions=True)
        self.qr_code = file_doc.file_url

# ---------------------------------------------------------------------
# 1️⃣ MAP BOOKING → SALES ORDER
# ---------------------------------------------------------------------
@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
    """Map Booking DocType to Sales Order."""
    def set_missing_values(source, target):
        target.transaction_date = frappe.utils.nowdate()
        target.customer = source.attendee or source.customer

    mapped = get_mapped_doc(
        "Booking",
        source_name,
        {
            "Booking": {
                "doctype": "Sales Order",
                "field_map": {
                    "attendee": "customer",
                    "event": "remarks"
                },
            },
            "Ticket Type": {
                "doctype": "Sales Order Item",
                "field_map": {
                    "ticket_type": "item_code",
                    "price": "rate",
                    "quantity": "qty"
                },
            }
        },
        target_doc,
        set_missing_values
    )

    sales_order = mapped
    sales_order.insert(ignore_permissions=True)
    frappe.db.set_value("Booking", source_name, "sales_order", sales_order.name)
    return sales_order.as_dict()

# ---------------------------------------------------------------------
# 2️⃣ INVOICE + PAYMENT REQUEST
# ---------------------------------------------------------------------
@frappe.whitelist()
def create_invoice_and_payment(so_name, make_payment_request_flag=True):
    """Create a Sales Invoice and Payment Request for a Sales Order."""
    so = frappe.get_doc("Sales Order", so_name)

    # Create Invoice
    si = frappe.new_doc("Sales Invoice")
    si.customer = so.customer
    si.due_date = frappe.utils.nowdate()
    for item in so.items:
        si.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate,
            "sales_order": so.name
        })
    si.insert(ignore_permissions=True)

    frappe.db.set_value("Sales Order", so.name, "sales_invoice", si.name)
    frappe.db.commit()

    payment_request_name = None
    if make_payment_request_flag:
        pr = make_payment_request(
            dt="Sales Invoice", dn=si.name,
            recipient_id=None,  # optional if customer email is set in invoice
            payment_gateway="Razorpay"  # Must match the configured Gateway name
        )
        pr.insert(ignore_permissions=True)
        payment_request_name = pr.name

        # Link back to related booking
        booking_name = frappe.db.get_value("Sales Order", so.name, "booking")
        if booking_name:
            frappe.db.set_value("Booking", booking_name, "payment_request", pr.name)

    return {"sales_invoice": si.name, "payment_request": payment_request_name}

# ---------------------------------------------------------------------
# 3️⃣ CREATE RAZORPAY PAYMENT ORDER
# ---------------------------------------------------------------------
# @frappe.whitelist(allow_guest=True)
# def create_payment_order(amount, reference):
#     """Create a Razorpay payment order through server-side API."""
#     settings = frappe.get_single("Razorpay Settings")  # Must exist in Integrations
#     client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

#     payment = client.order.create({
#         "amount": int(amount * 100),  # in paise
#         "currency": "INR",
#         "receipt": reference,
#         "payment_capture": 1
#     })
#     return payment


