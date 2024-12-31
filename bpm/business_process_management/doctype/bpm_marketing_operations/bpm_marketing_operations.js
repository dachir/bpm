// Copyright (c) 2024, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on("BPM Marketing Operations", {
    refresh(frm) {
        // Iterate through the child table rows and change the label
        frm.fields_dict['details'].grid.header_row.columns.group_1.df.label = 'Marque';
        frm.fields_dict['details'].grid.header_row.columns.group_2.df.label = 'Type Action';

        // Refresh the child table to apply changes
        frm.refresh_field('details');
    },
    type_calcul: function(frm) {
        frm.fields_dict['details'].grid.toggle_enable('rate', cur_frm.doc.category === "Pourcentage");
        frm.fields_dict['details'].grid.toggle_enable('amount', cur_frm.doc.category === "Montant");
        if (cur_frm.doc.type_calcul === "Pourcentage"){
            frm.fields_dict['details'].grid.toggle_enable('rate', true);
            frm.fields_dict['details'].grid.toggle_enable('amount', false);
        }
        else{
            frm.fields_dict['details'].grid.toggle_enable('rate', false);
            frm.fields_dict['details'].grid.toggle_enable('amount', true);
        }
        frm.refresh_field('details');
    },

    payment_terms_template: function (frm) {
        if (frm.doc.payment_terms_template) {
            frappe.call({
                method: "erpnext.controllers.accounts_controller.get_payment_terms",
                args: {
                    terms_template: frm.doc.payment_terms_template,
                    posting_date: frm.doc.posting_date,
                    grand_total: frm.doc.grand_total,
                    base_grand_total: frm.doc.base_grand_total
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
        frm.set_df_property('doctype_1', 'label', 'Marque');
        frm.set_df_property('doctype_2', 'label', 'Action');

        // Refresh the fields to apply the label changes
        frm.refresh_field('doctype_1');
        frm.refresh_field('doctype_2');
    },
	details_add(frm, cdt, cdn) {
        var df = frappe.meta.get_docfield("BPM Expense Details","rate", frm.doc.name);
		var row = locals[cdt][cdn]; 
        row.doctype_1 = "Brand";
        row.doctype_2 = "BPM Type Action";
	},
    rate(frm, cdt, cdn) {
		var row = locals[cdt][cdn]; 
        if(frm.doc.type_calcul === "Pourcentage" &&  frm.doc.amount != null){
            row.amount = frm.doc.amount * row.rate / 100;
            frm.refresh_field('details');
        }
	},
    amount(frm, cdt, cdn) {
		var row = locals[cdt][cdn]; 
        if(frm.doc.type_calcul !== "Pourcentage" &&  frm.doc.amount != null){
            row.rate = row.amount / frm.doc.amount * 100;
            frm.refresh_field('details');
        }
	},
});
