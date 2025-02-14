// Copyright (c) 2025, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on("BPM Payment Request", {
    setup: function (frm) {
        /*frm.set_query('category', function () {
            return {
                filters: {
                    description: ['not in', ['Santé et Frais Sanitaires', 'Rémunérations et Avantages', 'Transport et Véhicules', 'Marketing et Promotion', 'Motivation']]
                }
            };
        });*/
        frm.set_query('nature', function () {
            return {
                filters: {
                    categorie: frm.doc.category,
                    nature: ['not in', ['Motivation']]
                }
            };
        });
        frm.refresh_field("nature");
    },
});
