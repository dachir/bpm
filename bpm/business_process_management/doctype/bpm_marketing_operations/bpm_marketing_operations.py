# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, nowdate, getdate, money_in_words
from frappe.model.document import Document
import erpnext
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.accounts.party import get_party_account
from erpnext.setup.utils import get_exchange_rate
from bpm.utils.data_layer import share_doc


class BPMMarketingOperations(Document):

	def before_save(self):
		self.amount_letter = money_in_words(self.amount, self.currency)
		share_doc(self)
	
	def on_submit(self):
		purchase_invoice_name = self.create_purchase_invoice()
		self.db_set("purchase_invoice", purchase_invoice_name)


	def create_gl_entries(self):
		try:
			gl_entries = []
			posting_date = nowdate()
			total_amount = flt(self.amount)
			supplier = self.supplier
			debit_account = "62720700 - Marketing Expenses - MCO"
			credit_account = get_party_account("Supplier", supplier, self.company)
			currency = self.currency
			remarks = self.description
			company = self.company

			# Fetch account currencies
			debit_account_currency = frappe.db.get_value("Account", debit_account, "account_currency")
			credit_account_currency = frappe.db.get_value("Account", credit_account, "account_currency")

			# Determine exchange rates
			debit_exchange_rate = get_exchange_rate(currency, debit_account_currency)
			credit_exchange_rate = get_exchange_rate(currency, credit_account_currency)

			# Create credit GL entries for each line in the child table
			for line in self.details:
				debit_entry = frappe._dict({
					"posting_date": posting_date,
					"account": debit_account,
					#"party_type": "Supplier",
					#"party": supplier,
					"debit": flt(line.amount,2),
					"credit": 0,
					"debit_in_transaction_currency": flt(line.amount,2),
					"credit_in_transaction_currency": 0,
					"debit_in_account_currency": flt(line.amount * debit_exchange_rate, 2),
					"credit_in_account_currency": 0,
					"remarks": remarks,
					"against": credit_account,
					"cost_center": "CC013 - Marketing - MCO",
					"branch": self.branch,
					"brand": line.group_1,
					"bpm_type_action": line.group_2,
					"voucher_type": "BPM Marketing Operations",
					"voucher_no": self.name,
					"company": company,
					"currency": currency
				})
				gl_entries.append(debit_entry)

			# Create a single debit GL entry for the total amount
			gl_entries.append(frappe._dict({
				"posting_date": posting_date,
				"account": credit_account,
				"party_type": "Supplier",
				"party": supplier,
				"debit": 0,
				"credit": flt(total_amount,2),
				"debit_in_transaction_currency": -flt(total_amount,2),
				"credit_in_transaction_currency": 0,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": flt(total_amount * credit_exchange_rate, 2),
				"remarks": remarks,
				#"against": debit_account,
				"cost_center": "CC013 - Marketing - MCO",
				"branch": self.branch,
				"voucher_type": "BPM Marketing Operations",
				"voucher_no": self.name,
				"company": company,
				"currency": currency
			}))

			#frappe.throw(str(gl_entries))

			# Make GL entries using the built-in function
			make_gl_entries(gl_entries, cancel=False, update_outstanding="No")

			#frappe.msgprint(f"GL Entries created successfully for document: {self.name}")

		except Exception as e:
			frappe.log_error(message=str(e), title="GL Entry Creation Error")
			frappe.throw(f"An error occurred while creating GL entries: {str(e)}")


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
				"taxes_and_charges": "TVA ON PURCHASE - MCO",
				#"payment_terms_template": "50% after 7 Days - 50% after 30 Day",
				"branch": self.branch,
				"cost_center": "CC013 - Marketing - MCO",
			}))

			if self.payment_terms_template :
				purchase_invoice.update({ "payment_terms_template": "50% after 7 Days - 50% after 30 Day", })

			# Add child items from the `details` table
			for line in self.details:
				item_name = f"{line.group_1} {line.group_2} {self.description}"[:256]  # First 256 characters for item_name
				description = self.description  # Full description
				
				purchase_invoice.append("items", frappe._dict({
					"item_name": item_name,
					"description": description,
					"qty": 1,
					"rate": flt(line.amount, 2),
					"amount": flt(line.amount, 2),
					"conversion_factor": get_exchange_rate(self.currency, company_currency),
					"cost_center": "CC013 - Marketing - MCO",
					"brand": line.group_1,
					"bpm_type_action": line.group_2,
					"expense_account": "62720700 - Marketing Expenses - MCO",
				}))

			# Add taxes and charges if applicable\
			#tax_doc = frappe.get_doc("Purchase Taxes and Charges Template", "TVA ON PURCHASE - MCO")
			#for tax in tax_doc.taxes:
			#	purchase_invoice.append("taxes", frappe._dict({
			#		"charge_type": tax.charge_type,
			#		"account_head": tax.account_head,
			#		"description": tax.description,
			#		"rate": flt(tax.rate, 2),
			#		"tax_amount": flt(tax.rate * self.amount / 100, 2),
			#		"total": flt(self.amount, 2),
			#	}))

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

