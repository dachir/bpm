// Copyright (c) 2025, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on("BPM Sales Discount", {
    refresh: function(frm) {
        // Show button only if required fields are filled
        if (!frm.is_new() && frm.doc.customer && frm.doc.targets && frm.doc.targets.length > 0) {
            frm.add_custom_button(__('Fetch Payments'), function() {
                // Indicate process initiation
                frappe.show_alert({ message: __('Fetching payments...'), indicator: 'blue' });

                // Call server-side method
                frm.call('fetch_payments')
                    .then(response => {
                        if (response.message === "Success") {
                            frappe.msgprint(__('Payments have been successfully fetched.'));
                            frm.reload_doc(); // Reload document to reflect changes
                        } else {
                            frappe.msgprint(__('Failed to fetch payments. Please check the server logs.'));
                        }
                    })
                    .catch(error => {
                        frappe.msgprint(__('An error occurred: ') + error.message);
                    });
            });
        }
    }
});
