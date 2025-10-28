# Copyright (c) 2025, Rashih and contributors
# For license information, please see license.txt

import frappe
import razorpay
import json
import qrcode
import io
import hmac
import hashlib
from frappe.utils.file_manager import save_file
from frappe.model.document import Document
from frappe.utils import get_url



class Payment(Document):
    # Empty placeholder for your "Payment" DocType — keep if needed
    pass


@frappe.whitelist()
def send_booking_email_with_qr(booking_name):
    """Generate a QR code for a booking and email it to the user with the QR attached."""

    # --- 1️⃣ Fetch the Booking document ---
    booking = frappe.get_doc("Booking", booking_name)

    # --- 2️⃣ Generate QR Code Image ---
    qr_text = f"""
    Booking ID: {booking.name}
    Event: {booking.event}
    Customer: {getattr(booking, 'attendee_name', 'N/A')}
    """

    img = qrcode.make(qr_text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    image_bytes = buf.read()

    # --- 3️⃣ Save QR File and attach to Booking record ---
    file_doc = save_file(
        f"QR_{booking.name}.png",
        content=image_bytes,
        dt="Booking",
        dn=booking.name,
        is_private=0
    )
    booking.db_set("qr_code", file_doc.file_url)

    # --- 4️⃣ Determine Recipient Email ---
    recipient = booking.get("email") or booking.get("attendee_email")

    if not recipient:
        frappe.msgprint("⚠️ No email address found in this booking.")
        return

    # --- 5️⃣ Prepare Email Content ---
    subject = f"🎟️ Your Ticket Confirmation - {booking.event}"
    message = f"""
    <p>Hello {getattr(booking, 'attendee_name', '')},</p>
    <p>Thank you for booking your ticket for <b>{booking.event}</b>.</p>
    <p>Your booking ID is <b>{booking.name}</b>.</p>
    <p>Your QR code is attached below — please show it at the event entrance.</p>
    <br>
    <p>Best Regards,<br>EventOps Team</p>
    """

    # --- 6️⃣ Send Email with QR Attachment ---
    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=message,
        attachments=[
            {
                "fname": f"QR_{booking.name}.png",
                "fcontent": image_bytes
            }
        ]
    )

    frappe.msgprint(f"✅ Booking email sent with QR code to {recipient}.")
    return {"recipient": recipient, "file_url": file_doc.file_url}
'''
@frappe.whitelist(allow_guest=True)
def make_payment(attendee_name, attendee_email, event, total_amount):
    """
    Creates Booking document and returns Razorpay checkout URL
    """

    # 1️⃣ Create a new Booking
    booking = frappe.get_doc({
        "doctype": "Booking",
        "attendee_name": attendee_name,
        "attendee_email": attendee_email,
        "event": event,
        "total_amount": total_amount
    }).insert(ignore_permissions=True)

    # 2️⃣ Connect to Razorpay API
    settings = frappe.get_single("Razorpay Settings")
    client = razorpay.Client(auth=(settings.api_key, settings.get_password("api_secret", raise_exception=False)))

    # 3️⃣ Create an order in Razorpay
    order = client.order.create({
        "amount": int(float(total_amount) * 100),  # Convert to paise
        "currency": "INR",
        "receipt": booking.name,
        "payment_capture": 1
    })

    booking.db_set("razorpay_order_id", order.get("id"))

    # 4️⃣ Generate redirect URL to Razorpay
    redirect_url = (
        get_url(f"/razorpay_checkout?booking={booking.name}"
                f"&order_id={order.get('id')}"
                f"&amount={total_amount}")
    )

    return redirect_url


# 🎯 Razorpay callback / success handler
@frappe.whitelist(allow_guest=True)
def verify_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature, booking_name):
    """
    Called after successful payment from Razorpay
    """
    settings = frappe.get_single("Razorpay Settings")
    client = razorpay.Client(auth=(settings.api_key, settings.get_password("api_secret", raise_exception=False)))

    # Verify signature using Razorpay SDK
    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature
    }

    try:
        client.utility.verify_payment_signature(params_dict)

        # Mark booking as paid
        frappe.db.set_value("Booking", booking_name, "paid", 1)
        frappe.db.commit()
        return {"success": True, "message": "Payment verified"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Razorpay Signature Verification Failed")
        return {"success": False, "message": str(e)}
'''