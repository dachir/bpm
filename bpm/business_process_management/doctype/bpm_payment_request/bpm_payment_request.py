# Copyright (c) 2025, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, nowdate, getdate, money_in_words
from frappe.model.document import Document
from erp_space import erpspace


class BPMPaymentRequest(Document):
	
	def validate(self):
		erpspace.share_doc(self)
		if self.branch != "Kinshasa":
			frappe.throw("Only kinshasa is allowed for Bon Rouge.")

	def before_save(self):
		self.amount_letter = money_in_words(self.amount, self.currency)
		if self.nature == "Motivation":
			frappe.throw("Invalid Nature")

	def on_submit(self):
		self.create_payment()

	def create_payment(self):
		data = frappe.db.sql(
			"""
			SELECT m.default_account, a.account_currency
			FROM `tabMode of Payment Account` m 
			INNER JOIN `tabAccount` a ON a.name = m.default_account
			WHERE m.parent = %s AND m.company = %s
			""",
			(self.mode_of_payment, self.company), 
			as_dict=True
		)

		# Ensure there is a valid account returned
		if not data:
			frappe.throw("No default account found for the selected Mode of Payment and Company.")

		account = data[0].default_account
		account_currency = data[0].account_currency

		if self.currency != account_currency:
			frappe.throw("The document currency is different from the cash register currency!")

		# Get current year
		current_year = getdate().year  
		year_suffix = str(current_year)[2:]  # Extract last two digits (e.g., "25")

		# Determine party value dynamically based on branch
		if self.branch == "Kinshasa":
			party = f"LCE99{year_suffix}"  # Example: "LCE9925"
		else:
			party = f"LCE{current_year}"  # Example: "LCE2025"


		credit_account = "58120000 - Bon A Justifier USD - Kinshasa - MCO" if self.currency == "USD" else "58110000 - Bon A Justifier CDF - Kinshasa - MCO"
		credit_account_currency = frappe.db.get_value("Account", credit_account, "account_currency")

		args = {
			"doctype": "Payment Entry",
			"payment_type": "Internal Transfer",
			"posting_date": getdate(),
			"mode_of_payment_type": "Cash",
			#"party_type": "Supplier",
			#"party": party,
			"paid_from": account,
			"paid_from_account_currency": account_currency,
			"paid_to": credit_account,
			"paid_to_account_currency": credit_account_currency,
			"paid_amount": self.amount,
			"received_amount": self.amount,
			#"source_exchange_rate": 1.0,
			#"target_exchange_rate": 1.0,
			"reference_no": self.name,
			"reference_date": self.date,
			"branch": self.branch,
			"mode_of_payment": self.mode_of_payment,
		}

		try:
			pay_doc = frappe.get_doc(args)
			pay_doc.insert()
			self.payment_entry = pay_doc.name
			# Uncomment the next line if you want to submit the document automatically
			# pay_doc.submit()
		except Exception as e:
			frappe.throw(f"Error while creating Payment Entry: {str(e)}")
			
