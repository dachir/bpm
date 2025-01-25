# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bpm.utils.data_layer import share_doc_2
from erp_space import erpspace

class BPMItemMasterCreation(Document):
	def validate(self):
		#share_doc_2(self)
		erpspace.share_doc(self)
