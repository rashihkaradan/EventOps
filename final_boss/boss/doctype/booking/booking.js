// Copyright (c) 2025, Rashih and contributors
// For license information, please see license.txt

// Add a custom button if used in Desk form view
frappe.ui.form.on("Booking", {
  refresh(frm) {
    if (frm.doc.sales_order) {
      frm.add_custom_button("View Sales Order", () => {
        frappe.set_route("Form", "Sales Order", frm.doc.sales_order);
      });
    }
  },
});

// ----------------------------------------------------------
// Razorpay integration on web form submit
// ----------------------------------------------------------
/*frappe.web_form.after_submit = () => {
  const booking = frappe.web_form.doc;

  // Step 1: Create Sales Order and Payment Request
  frappe.call({
    method: "final_boss.boss.api.booking.make_sales_order",
    args: { source_name: booking.name },
    callback: function (r) {
      if (!r.message) {
        frappe.msgprint("❌ Failed to create Sales Order");
        return;
      }

      const sales_order = r.message;
      frappe.call({
        method: "final_boss.boss.api.payment.create_invoice_and_payment",
        args: { so_name: sales_order.name },
        callback: function (res) {
          if (!res.message || !res.message.payment_request) {
            frappe.msgprint("✅ Sales Order created: " + sales_order.name);
            return;
          }

          // Step 2: Create Razorpay order
          frappe.call({
            method: "final_boss.boss.doctype.booking.payment_razorpay.create_razorpay_order",
            args: { booking_name: booking.name },
            callback: function (razor_res) {
              if (!razor_res.message) {
                frappe.msgprint("Payment initialization failed");
                return;
              }

              const data = razor_res.message;

              // Step 3: Load Razorpay checkout script
              $.getScript("https://checkout.razorpay.com/v1/checkout.js", function () {
                const options = {
                  key: data.key_id,
                  amount: Math.round(data.amount * 100),
                  currency: data.currency,
                  name: "EventOps",
                  description: "Ticket Payment",
                  order_id: data.order_id,
                  handler: function (response) {
                    // Step 4: Verify and capture
                    frappe.call({
                      method: "final_boss.boss.doctype.payment_razorpay.verify_and_capture",
                      args: {
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_signature: response.razorpay_signature,
                        booking_name: booking.name,
                      },
                      callback: function (verify_res) {
                        if (verify_res.message && verify_res.message.success) {
                          frappe.msgprint("✅ Payment successful!");

                          // Redirect to Thank You page
                          window.location.href = "/thank-you";
                        } else {
                          frappe.msgprint("❌ Payment verification failed.");
                        }
                      },
                    });
                  },
                  modal: {
                    ondismiss: function () {
                      frappe.msgprint("Payment window closed by user.");
                    },
                  },
                };

                const rzp = new Razorpay(options);
                rzp.open();
              });
            },
          });
        },
      });
    },
  });
};
*/
