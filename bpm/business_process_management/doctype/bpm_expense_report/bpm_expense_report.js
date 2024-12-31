// Copyright (c) 2024, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on("BPM Expense Report", {
    setup: function (frm) {
        frm.set_query('category', function () {
            return {
                filters: {
                    description: ['not in', ['Santé et Frais Sanitaires', 'Rémunérations et Avantages', 'Transport et Véhicules', 'Marketing et Promotion', 'Motivation']]
                }
            };
        });
        frm.set_query('nature', function () {
            return {
                filters: {
                    categorie: frm.doc.category
                }
            };
        });
        frm.refresh_field("nature");
    },
 	//refresh(frm) {

 	//},
    payment_terms_template: function (frm) {
        if (frm.doc.payment_terms_template) {
            frappe.call({
                method: "erpnext.controllers.accounts_controller.get_payment_terms",
                args: {
                    terms_template: frm.doc.payment_terms_template,
                    posting_date: frm.doc.date,
                    grand_total: frm.doc.amount,
                    base_grand_total: frm.doc.amount
                },
                callback: function (r) {
                    if (r.message) {
                        // Clear the existing payment schedule
                        frm.clear_table('payment_schedule');

                        // Populate the payment schedule with the fetched terms
                        r.message.forEach(term => {
                            frm.add_child('payment_schedule', {
                                due_date: term.due_date,
                                invoice_portion: term.invoice_portion,
                                payment_amount: term.invoice_portion > 0 ? frm.doc.amount * term.invoice_portion / 100 : 0,
                                discount: term.discount,
                                discount_date: term.discount_date,
                                description: term.description,
                                mode_of_payment: term.mode_of_payment
                            });
                        });

                        // Refresh the field to reflect changes
                        frm.refresh_field('payment_schedule');
                    }
                }
            });
        }
    },
});
