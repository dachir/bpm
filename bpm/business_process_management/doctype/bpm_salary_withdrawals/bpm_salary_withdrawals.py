# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bpm.utils.data_layer import create_salary_withdrawal
from frappe.utils import flt, money_in_words

class BPMSalaryWithdrawals(Document):

	def before_save(self):
		self.amount_in_words = money_in_words(self.amount, self.currency)
	
	def on_submit(self):
		code = create_salary_withdrawal(self.name)
		self.sage_payment_number = code
