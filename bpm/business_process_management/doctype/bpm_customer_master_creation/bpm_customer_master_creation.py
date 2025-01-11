# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bpm.utils.data_layer import share_doc_2

class BPMCustomerMasterCreation(Document):
	def before_save(self):
		share_doc_2(self)
