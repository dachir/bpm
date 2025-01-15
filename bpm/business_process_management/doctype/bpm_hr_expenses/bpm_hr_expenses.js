// Copyright (c) 2024, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on("BPM HR Expenses", {
    setup: function (frm) {
        frm.set_query('category', function () {
            return {
                filters: {
                    description: ['in', ['Santé et Frais Sanitaires', 'Rémunérations et Avantages', 'Transport et Véhicules', 'Voyages et Déplacements']]
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

        /*frm.toggle_display("details_section",false);
        if (frm.doc.category == "Transport et Véhicules"){
            frm.set_df_property('vehicle', 'read_only', 0);
        }
        else{
            frm.set_df_property('vehicle', 'read_only', 1);
        }*/
    },
    refresh(frm) {
        // Iterate through the child table rows and change the label
        frm.fields_dict['details'].grid.header_row.columns.group_1.df.label = 'Cost Center';
        frm.fields_dict['details'].grid.header_row.columns.group_2.df.label = 'Employee';
        // Hide the 'rate' column in the grid of the child table 'items'
        frm.fields_dict['details'].grid.set_column_disp('rate', false);
        // Disable the 'items' grid (child table)
        frm.fields_dict['details'].grid.set_read_only(true);

        // Refresh the child table to apply changes
        frm.refresh_field('details');
    },
    category: function (frm) {
        frm.set_query('nature', function () {
            return {
                filters: {
                    categorie: frm.doc.category
                }
            };
        });

        if (frm.doc.category == "Transport et Véhicules"){
            frm.set_df_property('vehicle', 'read_only', 0);
        }
        else{
            frm.set_df_property('vehicle', 'read_only', 1);
            frm.set_value('vehicle', null);
        }
    },
    nature: function (frm) {
        if (frm.doc.nature == "Transport Staff"){
            frm.toggle_display("details_section",true);
        }
        else{
            frm.toggle_display("details_section",false);
            frm.clear_table('details');
            frm.refresh_field('details');
        }
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
    }
});

frappe.ui.form.on('BPM Expense Details', {
	setup(frm) {
        // Rename the column labels for 'doctype_1' and 'doctype_2'
        frm.set_df_property('doctype_1', 'label', 'Cost Center');
        frm.set_df_property('doctype_2', 'label', 'Employee');

        // Refresh the fields to apply the label changes
        frm.refresh_field('doctype_1');
        frm.refresh_field('doctype_2');
    },
	details_add(frm, cdt, cdn) {
		var row = locals[cdt][cdn]; 
        row.doctype_1 = "Cost Center";
        row.doctype_2 = "Employee";
        if(frm.doc.cost_center != null){
            row.group_1 = frm.doc.cost_center;
            frm.refresh_field('group_1');
        }
        
	},
});

frappe.ui.form.on("BPM HR Expenses","refresh", function(frm, cdt, cdn) { 
	df = frappe.meta.get_docfield("BPM Expense Details","rate", frm.doc.name);
	df.hidden = 1;
});

