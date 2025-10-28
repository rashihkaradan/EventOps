# ---------------------------------------------------------------------
#  PAYMENT CREATION FOR BOOKING WEB FORM
# ---------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def create_payment_for_booking(booking_name):
    """
    Called after Web Form submission.
    Creates a Payment Request for the Booking using Razorpay gateway.
    Returns Razorpay payment URL.
    """
    booking = frappe.get_doc("Booking", booking_name)

    if not booking.total_amount:
        frappe.throw("Booking total amount is missing.")

    # ✅ Create Payment Request
    payment_request = frappe.get_doc({
        "doctype": "Payment Request",
        "payment_gateway_account": "Razorpay - INR",  # Must exist in Payments → Payment Gateway Account
        "party_type": "Customer",
        "party": booking.customer or booking.attendee,
        "reference_doctype": "Booking",
        "reference_name": booking.name,
        "currency": "INR",
        "grand_total": booking.total_amount,
        "message": f"Payment for Booking {booking.name}",
        "redirect_to": "/payment-success",  # Web page after successful payment
    })
    payment_request.insert(ignore_permissions=True)
    payment_request.submit()

    # ✅ Link back to Booking
    booking.db_set("payment_request", payment_request.name)

    # ✅ Return Payment URL
    return payment_request.get_payment_url()
