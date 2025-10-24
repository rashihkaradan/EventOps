// Copyright (c) 2025, rashih and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Booking", {
// 	refresh(frm) {

// 	},
// });
frm.add_custom_button("View Sales Order", () => {
    frappe.set_route("Form", "Sales Order", frm.doc.sales_order);
});
