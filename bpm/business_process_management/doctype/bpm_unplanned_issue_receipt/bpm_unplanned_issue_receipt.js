// Copyright (c) 2024, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on('BPM Unplanned Issue Receipt', {
	// refresh: function(frm) {

	// }
});

const get_sage_item_cost_stu = function(frm, item) {
	return new Promise((resolve, reject) => {
		frappe.call({
			method: "sage_integration.utils.utils.get_sage_item_cost_stu",
			args: {
				"site": frm.doc.branch,
				"item": item,
			},
			callback: (r) => {
				//frm.refresh();
				if (r.message) resolve(r.message);
				else resolve(0);
			},
			error: (err) => {
				// Handle any errors here
				reject(err);
			},
		});
	});
}

frappe.ui.form.on('BPM Unplanned Issue Receipt Details', {
    product(frm, cdt, cdn) {
        var row = locals[cdt][cdn]; 
        
        get_sage_item_cost_stu(frm, row.product).then((result) => {
            if (result && result.length >= 2) { // Ensure result is valid and contains at least two values
                var cout_tn = result[0]; // Get the first value
                var conv = result[1]; // Get the second value

                row.rate = cout_tn;
                row.conversion_factor = conv;

                // Check if row.quantity is truthy before performing calculations
                if (row.quantity && row.uom === row.stock_uom) {
                    row.amount = row.quantity * row.rate;
                }
                if (row.quantity && row.uom !== row.stock_uom) {
                    row.amount = row.quantity * row.rate * row.conversion_factor;
                }
                frm.refresh_field("rate");
                frm.refresh_field("amount");
                frm.refresh();
            } else {
                console.error("Invalid result format:", result);
            }
        }).catch((error) => {
            // Handle errors if any
            console.error("Error fetching data:", error);
        });
    }
});


