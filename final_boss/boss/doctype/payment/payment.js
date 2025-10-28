// Copyright (c) 2025, rashih and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Payment", {
// 	refresh(frm) {

// 	},
// });
/*$.getScript("https://checkout.razorpay.com/v1/checkout.js", function () {
  const options = {
    key: data.key_id,
    amount: Math.round(data.amount * 100),
    currency: data.currency,
    name: "EventOps",
    description: "Ticket Payment",
    order_id: data.order_id,

    // ✅ Your handler must be defined here
    handler: function (response) {
      frappe.call({
        method: "final_boss.api.payment.verify_payment",
        args: {
          razorpay_payment_id: response.razorpay_payment_id,
          razorpay_order_id: response.razorpay_order_id,
          razorpay_signature: response.razorpay_signature,
          booking_name: frappe.web_form.doc.name
        },
        callback: function (res) {
          if (res.message && res.message.success) {
            frappe.msgprint("✅ Payment successful!");
            window.location.href = "/thank-you";
          } else {
            frappe.msgprint("❌ Payment verification failed.");
          }
        }
      });
    },

    modal: {
      ondismiss: function () {
        frappe.msgprint("Payment popup closed.");
      }
    }
  };

  const rzp = new Razorpay(options);
  rzp.open();
});
*/