# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, nowdate, getdate, money_in_words
from frappe.model.document import Document
import erpnext
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.accounts.party import get_party_account
from erpnext.setup.utils import get_exchange_rate
from bpm.utils.data_layer import share_doc_2


class BPMMotivationExpenseReport(Document):
	
	def before_save(self):
		self.amount_letter = money_in_words(self.amount, self.currency)
		share_doc_2(self)

	def on_submit(self):
		purchase_invoice_name = self.create_purchase_invoice()
		self.db_set("purchase_invoice", purchase_invoice_name)

	def create_purchase_invoice(self):
		try:
			due_date = nowdate()
			company_currency = erpnext.get_company_currency(self.company)
			# Initialize the Purchase Invoice
			purchase_invoice = frappe.get_doc(frappe._dict({
				"doctype": "Purchase Invoice",
				"supplier": "LCE99" + str(getdate().year)[2:],
				"posting_date": due_date,
				"bill_date": due_date,
				"company": self.company,
				"currency": self.currency,
				"branch": self.branch,
				"cost_center": self.cost_center
			}))


			account = "63280300 - Business expenses - MCO"
			item_name = f"{self.description} {self.direction} {self.ministry}"[:256]  # First 256 characters for item_name
			description = self.description  # Full description

			item_data = frappe._dict({
				"item_name": item_name,
				"description": description,
				"qty": 1,
				"rate": flt(self.amount, 2),
				"amount": flt(self.amount, 2),
				"conversion_factor": get_exchange_rate(self.currency, company_currency),
				"cost_center": self.cost_center,
				"branch": self.branch,
				"expense_account": account,
			})

			purchase_invoice.append("items", item_data)

			#max_due_date = max(
			#	[getdate(row.due_date) for row in self.payment_schedule if row.due_date],
			#	default=due_date
			#)

			purchase_invoice.update({ "due_date": due_date, })
			# Insert and Submit the Purchase Invoice
			purchase_invoice.insert()

			frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created successfully.")
			return purchase_invoice.name

		except Exception as e:
			frappe.log_error(message=str(e), title="Purchase Invoice Creation Error")
			frappe.throw(f"An error occurred while creating the Purchase Invoice: {str(e)}")
