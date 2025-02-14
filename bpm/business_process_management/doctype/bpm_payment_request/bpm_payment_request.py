# Copyright (c) 2025, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, nowdate, getdate, money_in_words
from frappe.model.document import Document
from erp_space import erpspace


class BPMPaymentRequest(Document):
	
	def validate(self):
		erpspace.share_doc(self)

	def before_save(self):
		self.amount_letter = money_in_words(self.amount, self.currency)
		if self.nature == "Motivation":
			frappe.throw("Invalid Nature")

	def on_submit(self):
		self.create_payment()

	def create_payment():
		data = frappe.db.sql(
			"""
			SELECT m.default_account,a.account_currency
			FROM `tabMode of Payment Account` m INNER JOIN tabAccount a ON a.name = m.default_account
			WHERE m.parent = %s AND m.company = %s
			""",(self.mode_of_payment,self.company), as_dict = 1
		)

		account = data[0].default_account
		account_currency = data[0].account_currency

		if self.currency != account_currency:
			frappe.throw("The document currency is different from the cash register currency!")

		args = {
			"doctype": "Payment Entry",
			"party_type": "Supplier",
			"party": "LCE99"str(frappe.utils.getdate().year)[2:] if self.branch ="Kinshasa" else "LCE"str(frappe.utils.getdate().year),
			"paid_amount": self.amount,
			"received_amount": self.amount,
			"target_exchange_rate": 1.0,
			"paid_to": account,
			"paid_to_account_currency": account_currency,
			"reference_no": self.name,
			"reference_date": self.date,
			"branch": self.branch
		}

		pay_doc = frappe.get_doc(args)
		pay_doc.insert()
		#pay_doc.submit()
			
