// Copyright (c) 2024, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on('BPM Marketing Sampling', {
	refresh: function(frm) {
		on_mode_change(frm)
	},
	mode: function(frm) {
		on_mode_change(frm)
	}
});

const on_mode_change = (frm) =>{
	var ratio = frappe.meta.get_docfield("BPM Sampling Details","ratio", frm.doc.name);
	var amount = frappe.meta.get_docfield("BPM Sampling Details","amount", frm.doc.name);
	if(frm.doc.mode == "Valeur"){
		ratio.read_only = 1;
		amount.read_only = 0;
	}
	else{
		ratio.read_only = 0;
		amount.read_only = 1;
	}
}


frappe.ui.form.on("BPM Marketing Sampling'","onload", function(frm, cdt, cdn) {
    var df = frappe.meta.get_docfield("BPM Sampling Details","amount", cur_frm.doc.name);
    df.read_only = 1;
});

