# Copyright (c) 2025, rashih and contributors
# For license information, please see license.txt
import frappe, razorpay, json
from frappe.utils import now_datetime
from frappe import _
import hmac, hashlib
import qrcode
import io
from frappe.utils.file_manager import save_file
from frappe.model.document import Document


class Payment(Document):
	pass

@frappe.whitelist()
def send_booking_email_with_qr(booking_name):
    """
    Generate a QR code for a booking and email it to the user with the QR attached.
    """

    # Get booking document
    booking = frappe.get_doc("Booking", booking_name)

    # --- 1️⃣ Generate QR text ---
    qr_text = f"Booking ID: {booking.name}\nEvent: {booking.event}\nCustomer: {getattr(booking, 'attendee_name', '')}"
    img = qrcode.make(qr_text)

    # --- 2️⃣ Save QR image in memory ---
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    image_bytes = buf.read()

    # --- 3️⃣ Attach QR to Booking record ---
    file_doc = save_file(f"QR_{booking.name}.png", image_bytes, "Booking", booking.name, is_private=0)
    booking.db_set("qr_code", file_doc.file_url)

    # --- 4️⃣ Prepare email ---
    recipient = None
    if getattr(booking, "email", None):
        recipient = booking.email
    elif getattr(booking, "attendee_email", None):
        recipient = booking.attendee_email

    if not recipient:
        frappe.msgprint("⚠️ No email found in booking.")
        return

    subject = f"🎟️ Your Ticket Confirmation - {booking.event}"
    message = f"""
    <p>Hello {getattr(booking, 'attendee_name', '')},</p>
    <p>Thank you for booking your ticket for <b>{booking.event}</b>.</p>
    <p>Your booking ID is <b>{booking.name}</b>.</p>
    <p>Please find your QR code attached below — show it at the entry gate.</p>
    <br>
    <p>Best Regards,<br>EventOps Team</p>
    """

    # --- 5️⃣ Send Email ---
    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=message,
        attachments=[{
            "fname": f"QR_{booking.name}.png",
            "fcontent": image_bytes
        }]
    )

    frappe.msgprint(f"✅ Email with QR sent to {recipient}.")
