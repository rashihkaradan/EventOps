import frappe
import qrcode
import io
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils.file_manager import save_file
from frappe.utils import nowdate
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

# ---------------------------------------------------------------------
# BOOKING CLASS
# ---------------------------------------------------------------------
class Booking(Document):
    def validate(self):
        # in booking.py
        if self.ticket_type:
            price = frappe.db.get_value(
                "Item Price",
                {"item_code": self.ticket_type, "price_list": "Standard Selling"},
                "price_list_rate"
            )
            self.price = price or 0

        """Calculate total before saving."""
        self.total_amount = (self.price or 0) * (self.quantity or 0)

    def before_save(self):
        """Generate QR code when event or attendee changes."""
        if not self.qr_code or self.has_value_changed("event") or self.has_value_changed("attendee"):
            self.generate_qr_code()

    def generate_qr_code(self):
        """Generate and attach a QR code to this Booking."""
        qr_data = f"Booking ID: {self.name}\nAttendee: {self.attendee}\nEvent: {self.event}"
        img = qrcode.make(qr_data)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        file_name = f"qr_code_{self.name}.png"
        file_doc = save_file(file_name, buf.getvalue(), self.doctype, self.name, is_private=False)
        self.qr_code = file_doc.file_url


# ---------------------------------------------------------------------
# 1️⃣ MAP BOOKING → SALES ORDER
# ---------------------------------------------------------------------
@frappe.whitelist()
def make_sales_order(booking_name):
    booking = frappe.get_doc("Booking", booking_name)

    # Create Sales Order
    so = frappe.new_doc("Sales Order")
    so.customer = booking.attendee
    so.transaction_date = nowdate()
    so.delivery_date = nowdate()
    so.append("items", {
        "item_code": booking.ticket_type,
        "qty": booking.quantity,
        "rate": booking.price,
        "amount": booking.total_amount
    })
    so.insert(ignore_permissions=True)
    so.submit()

    # Link back to Booking
    booking.sales_order = so.name
    booking.save(ignore_permissions=True)

    frappe.logger("razorpay_webhook").info(f"[Webhook] Sales Order Created: {so.name}")
    return so

@frappe.whitelist()
def create_invoice_and_payment(sales_order_name):
    so = frappe.get_doc("Sales Order", sales_order_name)

    # Create Sales Invoice
    si = frappe.new_doc("Sales Invoice")
    si.customer = so.customer
    si.due_date = nowdate()
    for item in so.items:
        si.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate,
            "sales_order": so.name
        })
    si.insert(ignore_permissions=True)
    si.submit()

    # Create Payment Entry
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer"
    pe.party = so.customer
    pe.paid_amount = si.grand_total
    pe.received_amount = si.grand_total
    pe.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": si.name,
        "allocated_amount": si.grand_total
    })

    # ✅ Set target exchange rate safely
    if pe.paid_from_account_currency != pe.paid_to_account_currency:
        pe.target_exchange_rate = frappe.db.get_value(
            "Currency Exchange",
            {
                "from_currency": pe.paid_from_account_currency,
                "to_currency": pe.paid_to_account_currency
            },
            "exchange_rate"
        ) or 1
    else:
        pe.target_exchange_rate = 1

    pe.insert(ignore_permissions=True)
    pe.submit()

    # ✅ Link to Booking
    booking_name = frappe.db.get_value("Booking", {"sales_order": so.name}, "name")
    if booking_name:
        booking = frappe.get_doc("Booking", booking_name)
        booking.sales_invoice = si.name
        booking.payment_status = "Paid"
        booking.save(ignore_permissions=True)

    frappe.db.commit()
    frappe.logger("razorpay_webhook").info(f"[Webhook] Invoice: {si.name}, Payment Entry: {pe.name}")
    return {"sales_invoice": si.name, "payment_entry": pe.name}

# ---------------------------------------------------------------------
# 3️⃣ CREATE RAZORPAY PAYMENT ORDER
# ---------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def create_razorpay_order(amount, reference):
    """Create a Razorpay order via server-side API."""
    settings = frappe.get_single("Razorpay Settings")
    import razorpay
    client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

    order = client.order.create({
        "amount": int(amount * 100),
        "currency": "INR",
        "receipt": reference,
        "payment_capture": 1
    })
    return order
