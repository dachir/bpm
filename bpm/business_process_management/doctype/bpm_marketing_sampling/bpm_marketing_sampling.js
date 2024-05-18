// Copyright (c) 2024, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on('BPM Marketing Sampling', {
	mode: function(frm) {
		frm.doc.details.forEach(e => {
			if(e.item){
				if(frm.doc.mode == "Echantillon"){
					get_sage_selling_price(frm,e.item).then((result)=> {
						e.rate = result;
						if(e.qty){
							e.amount = e.qty * e.rate;
						}
						frm.refresh_field('rate');
						frm.refresh_field('amount');
						frm.refresh();
					}); 
				}
				else{
					get_sage_cm29_price(frm,e.item).then((result)=> {
						e.rate = result;
						if(e.qty){
							e.amount = e.qty * e.rate;
						}
						frm.refresh_field('rate');
						frm.refresh_field('amount');
						frm.refresh();
					}); 
				}
				
			}
		});
		if(frm.doc.details.length > 0){
			frm.refresh_field('amount');
			frm.refresh();
		}
	},
});




frappe.ui.form.on("BPM Marketing Sampling'","onload", function(frm, cdt, cdn) {
    var df = frappe.meta.get_docfield("BPM Sampling Details","amount", cur_frm.doc.name);
    df.read_only = 1;
});

const get_sage_selling_price = function(frm, item) {
	return new Promise((resolve, reject) => {
		frm.call({
			method: "sage_integration.utils.utils.get_sage_selling_price",
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

const get_sage_cm29_price = function(frm, item) {
	return new Promise((resolve, reject) => {
		frappe.call({
			method: "sage_integration.utils.utils.get_sage_cm29_price",
			args: {
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

const on_row_change = (frm, row) =>{
	if(row.qty && row.rate){
		row.amount = row.qty * row.rate;
	}
	else{
		row.amount = 0;
	}
	frm.refresh_field('amount');
	frm.refresh();
}


frappe.ui.form.on('BPM Sampling Details', {
	
    item(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.item){
			if(frm.doc.mode == "Echantillon"){
				get_sage_selling_price(frm,row.item).then((result)=> row.rate = result); 
			}
			else{
				get_sage_cm29_price(frm,row.item).then((result)=> row.rate = result);
			}

			if(row.qty && row.rate){
				row.amount = row.qty * row.rate;
			}
			else{
				row.amount = 0;
			}
			frm.refresh_field('amount');
			frm.refresh();
		}
        
    },
	qty(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
        on_row_change(frm, row);
    },
	rate(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
        on_row_change(frm, row);
    },

});
