# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bpm.utils.data_layer import create_salary_withdrawal, share_doc, share_doc_2
from erpnext.setup.utils import get_exchange_rate
from frappe.utils import flt, money_in_words, nowdate
from erpnext.accounts.general_ledger import make_gl_entries

class BPMSalaryWithdrawals(Document):

	def before_save(self):
		self.amount_in_words = money_in_words(self.amount, self.currency)
		share_doc_2(self)
	
	def on_submit(self):
		#code = create_salary_withdrawal(self.name)
		#frappe.db.set_value(self.doctype,self.name,'sage_payment_number',code)
		self.create_gl_entries()

	def create_gl_entries(self):
		try:
			gl_entries = []
			posting_date = nowdate()
			total_amount = flt(self.amount)
			supplier = self.supplier
			debit_account = "66210000 - Salaries Expats - MCO"
			credit_account = '42110100 - Staff Salary Credit -Expat - MCO'
			currency = self.currency
			remarks = self.description
			company = self.company

			# Fetch account currencies
			debit_account_currency = frappe.db.get_value("Account", debit_account, "account_currency")
			credit_account_currency = frappe.db.get_value("Account", credit_account, "account_currency")

			# Determine exchange rates
			debit_exchange_rate = get_exchange_rate(currency, debit_account_currency)
			credit_exchange_rate = get_exchange_rate(currency, credit_account_currency)

			# Create credit GL entries for debit
			debit_entry = frappe._dict({
				"posting_date": posting_date,
				"account": debit_account,
				#"party_type": "Supplier",
				#"party": supplier,
				"debit": flt(self.amount,2),
				"credit": 0,
				"debit_in_transaction_currency": flt(self.amount,2),
				"credit_in_transaction_currency": 0,
				"debit_in_account_currency": flt(self.amount * debit_exchange_rate, 2),
				"credit_in_account_currency": 0,
				"remarks": remarks,
				"against": credit_account,
				"cost_center": self.cost_center,
				"branch": self.branch,
				"employee": self.employee,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"company": company,
				"currency": currency
			})
			gl_entries.append(debit_entry)

			# Create a single debit GL entry for credit
			gl_entries.append(frappe._dict({
				"posting_date": posting_date,
				"account": credit_account,
				"party_type": "Employee",
				"party": self.employee,
				"debit": 0,
				"credit": flt(self.amount,2),
				"debit_in_transaction_currency": -flt(self.amount,2),
				"credit_in_transaction_currency": 0,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": flt(self.amount * credit_exchange_rate, 2),
				"remarks": remarks,
				"against": debit_account,
				"cost_center": self.cost_center,
				"branch": self.branch,
				"employee": self.employee,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"company": company,
				"currency": currency
			}))

			#frappe.throw(str(gl_entries))

			# Make GL entries using the built-in function
			make_gl_entries(gl_entries, cancel=False, update_outstanding="No")

			frappe.msgprint(f"GL Entries created successfully for document: {self.name}")

		except Exception as e:
			frappe.log_error(message=str(e), title="GL Entry Creation Error")
			frappe.throw(f"An error occurred while creating GL entries: {str(e)}")
