# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from sage_integration.utils.soap_ws import create_sales_order, create_credit_note
from frappe.utils import flt, money_in_words
from bpm.utils.data_layer import share_doc_2
from erp_space import erpspace

class BPMMarketingSampling(Document):
	def validate(self):
		#share_doc_2(self)
		erpspace.share_doc(self)

	def on_submit(self):
		if self.mode == "Echantillon":
			code = create_credit_note(self.name)
			frappe.db.set_value(self.doctype,self.name,'note_credit',code)
		
		code = create_sales_order(self.name)
		frappe.db.set_value(self.doctype,self.name,'sage_order',code)
