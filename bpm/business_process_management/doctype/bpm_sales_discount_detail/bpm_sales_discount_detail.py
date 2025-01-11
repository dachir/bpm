# Copyright (c) 2025, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bpm.utils.data_layer import share_doc_2

class BPMSalesDiscountDetail(Document):
	def before_save(self):
		share_doc_2(self)
