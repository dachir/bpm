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
    refresh: function(frm) { 
        // Background when expense_report is filled (very light yellow)
        let filled_bg = '#FFFEF0'; 
        // Header background when expense_report is filled (slightly thicker yellow)
        let filled_header_bg = '#FFF7E6'; 

        // Check if expense_report is filled
        if (frm.doc.payment_request) {
            $('.form-page').css('background-color', filled_bg); // Apply yellow background
            $('.page-head-content').css('background-color', filled_header_bg); // Thicker yellow header 
            $('.layout-side-section').css('background-color', filled_header_bg);
        }
        else {
            $('.form-page').css('background-color', ""); 
            $('.page-head-content').css('background-color', ""); 
            $('.layout-side-section').css('background-color', "");
        }

        // Adjust header title color for better contrast
        $('.page-title').css('color', '#990000'); 
    },
    // Also apply color changes when the expense_report field is updated
    payment_request: function(frm) {
        frm.trigger('refresh');
    },
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

// Function to reset styles when leaving the form
function resetFormStyles() {
    $('.form-page').css('background-color', '');
    $('.page-head-content').css('background-color', '');
}

// Reset colors when navigating away using Frappe's routing system
frappe.router.on('change', function() {
    resetFormStyles();
});

// Reset colors when the page is reloaded or before leaving
$(window).on('beforeunload', function() {
    resetFormStyles();
});
