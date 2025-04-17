// Copyright (c) 2024, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on("BPM Motivation Expense Report", {
    setup: function (frm) {
        frm.set_query('nature', function () {
            return {
                filters: {
                    account: ['LIKE', '63280%']
                }
            };
        });
        frm.refresh_field("nature");
    },
});
