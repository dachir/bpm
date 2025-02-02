// Copyright (c) 2025, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on("BPM Sales Discount", {
    refresh: function (frm) {
        if (!frm.is_new() && frm.doc.customer && frm.doc.targets && frm.doc.targets.length > 0) {
            frm.add_custom_button(__('Fetch Payments'), function () {
                frappe.show_alert({ message: __('Fetching payments...'), indicator: 'blue' });

                // Call server-side method with parameters
                frm.call('fetch_payments')
                    .then(response => {
                        if (response.message) {
                            let payments = response.message;

                            // Clear existing tables
                            frm.clear_table("payment_usd");
                            frm.clear_table("payment_cdf");

                            // Populate the payment_usd grid
                            payments.payments_usd.forEach(payment => {
                                frm.add_child("payment_usd", {
                                    begin: payment.begin,
                                    end: payment.end,
                                    payment_entry: payment.payment_entry,
                                    date: payment.date,
                                    amount: payment.amount,
                                    currency: payment.currency
                                });
                            });

                            // Populate the payment_cdf grid
                            payments.payments_cdf.forEach(payment => {
                                frm.add_child("payment_cdf", {
                                    begin: payment.begin,
                                    end: payment.end,
                                    payment_entry: payment.payment_entry,
                                    date: payment.date,
                                    amount: payment.amount,
                                    currency: payment.currency
                                });
                            });

                            // Refresh the fields to display updated tables
                            frm.refresh_field("payment_usd");
                            frm.refresh_field("payment_cdf");
                            frm.refresh()
                            frappe.msgprint(__('Payments have been successfully fetched.'));
                        } else {
                            frappe.msgprint(__('No payments found.'));
                        }
                    })
                    .catch(error => {
                        frappe.msgprint(__('An error occurred: ') + error.message);
                        console.error('Error fetching payments:', error);
                    });
            });
        }
    }
});
