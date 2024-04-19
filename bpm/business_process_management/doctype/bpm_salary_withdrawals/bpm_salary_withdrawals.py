# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bpm.utils.data_layer import create_salary_withdrawal

class BPMSalaryWithdrawals(Document):
	
	def on_submit(self):
		create_salary_withdrawal(self.name)
