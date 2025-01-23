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


class BPMHRExpenses(Document):
	
	def before_save(self):
		self.amount_letter = money_in_words(self.amount, self.currency)
		if self.nature == "Motivation":
			frappe.throw("Invalid Nature")
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
				"supplier": self.supplier,
				"posting_date": due_date,
				"bill_date": due_date,
				"company": self.company,
				"currency": self.currency,
				#"taxes_and_charges": "TVA ON PURCHASE - MCO",
				#"payment_terms_template": "50% after 7 Days - 50% after 30 Day",
				"branch": self.branch,
				"wf_user": frappe.session.user,
			}))

			#if self.category != "Rémunérations et Avantages":
			#	purchase_invoice.update({ "taxes_and_charges": "TVA ON PURCHASE - MCO" })

			if self.category == "Transport et Véhicules":
				purchase_invoice.update({ "vehicle": self.vehicle })


			account = frappe.db.get_value("Expense Nature", self.nature, "account")
			if len(self.details) > 0:
				purchase_invoice.update({ "cost_center": self.cost_center })
				# Add child items from the `details` table
				for line in self.details:
					item_name = f"{self.description} {line.group_2} {line.group_1}"[:100]  # First 256 characters for item_name
					description = self.description  # Full description
					
					purchase_invoice.append("items", frappe._dict({
						"item_name": item_name,
						"description": description,
						"qty": 1,
						"rate": flt(line.amount, 2),
						"amount": flt(line.amount, 2),
						"conversion_factor": get_exchange_rate(self.currency, company_currency),
						"cost_center": line.group_1,
						"employee": line.group_2,
						"branch": self.branch,
						"expense_account": account,
					}))
			else:
				purchase_invoice.update({ "cost_center": self.cost_center, "employee": self.employee, })
				item_name = self.description[:256]  # First 256 characters for item_name
				description = self.description  # Full description

				item_data = frappe._dict({
					"item_name": item_name,
					"description": description,
					"qty": 1,
					"rate": flt(self.amount, 2),
					"amount": flt(self.amount, 2),
					"conversion_factor": get_exchange_rate(self.currency, company_currency),
					"cost_center": self.cost_center,
					"employee": self.employee,
					"branch": self.branch,
					"expense_account": account,
				})

				if self.vehicle:
					item_data.update({"vehicle": self.vehicle})

				purchase_invoice.append("items", item_data)

			max_due_date = max(
				[getdate(row.due_date) for row in self.payment_schedule if row.due_date],
				default=due_date
			)

			purchase_invoice.update({ "due_date": max_due_date, })
			# Insert and Submit the Purchase Invoice
			purchase_invoice.insert()

			frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created successfully.")
			return purchase_invoice.name

		except Exception as e:
			frappe.log_error(message=str(e), title="Purchase Invoice Creation Error")
			frappe.throw(f"An error occurred while creating the Purchase Invoice: {str(e)}")
