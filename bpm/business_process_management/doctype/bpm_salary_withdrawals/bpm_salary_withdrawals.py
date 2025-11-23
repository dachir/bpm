# Copyright (c) 2024, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bpm.utils.data_layer import create_salary_withdrawal, share_doc, share_doc_2
from erpnext.setup.utils import get_exchange_rate
from frappe.utils import flt, money_in_words, nowdate
from erpnext.accounts.general_ledger import make_gl_entries
from erp_space import erpspace

class BPMSalaryWithdrawals(Document):

	def before_save(self):
		self.amount_in_words = money_in_words(self.amount, self.currency)
		#share_doc_2(self)
		erpspace.share_doc(self)
	
	def on_submit(self):
		#code = create_salary_withdrawal(self.name)
		#frappe.db.set_value(self.doctype,self.name,'sage_payment_number',code)
		self.create_payment_entry_draft()

	def create_payment_entry_draft(self):
		"""
		À la soumission du BPM Salary Withdrawals, on crée un Payment Entry en brouillon
		pour que la compta puisse le contrôler et le soumettre plus tard.
		"""
		try:
			posting_date = nowdate()
			total_amount = flt(self.amount, 2)

			pe = frappe.new_doc("Payment Entry")

			# Ici on utilise un Internal Transfer : on reproduit ton écriture
			pe.payment_type = "Pay"
			pe.company = frappe.defaults.get_global_default("company")
			pe.posting_date = posting_date
			pe.party_type = "Employee"
			pe.party = self.employee
			pe.paid_from_account_currency = self.currency
			pe.paid_to_account_currency = self.currency

			# Si tu as un champ mode_of_payment sur ton doctype, tu peux le réutiliser
			# sinon, on met une valeur par défaut
			pe.mode_of_payment = self.mode_of_payment 

			# On transfère du compte crédit vers le compte débit
			#pe.paid_from = credit_account      # sera crédité
			#pe.paid_to = debit_account         # sera débité

			pe.paid_amount = total_amount
			pe.received_amount = total_amount

			pe.reference_no = self.name
			pe.reference_date = posting_date
			pe.remarks = f"Salary {self.type} {self.pay_period} from {self.doctype}: {self.name}"

			# Dimensions si elles existent sur Payment Entry
			if pe.meta.has_field("cost_center") and getattr(self, "cost_center", None):
				pe.cost_center = self.cost_center

			if pe.meta.has_field("branch") and getattr(self, "branch", None):
				pe.branch = self.branch

			

			# IMPORTANT : on n'appelle PAS pe.submit(), donc il reste en Draft
			pe.insert(ignore_permissions=True)
			pe.submit()

			frappe.db.set_value(self.doctype, self.name, "payment_entry", pe.name)

			frappe.msgprint(
				_("Payment Entry <b>{0}</b> créé depuis {1} {2}.")
				.format(pe.name, self.doctype, self.name),
				alert=True
			)

		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "BPM Salary Withdrawals – Payment Entry Creation Error")
			frappe.throw(_("Une erreur est survenue lors de la création du Payment Entry : {0}").format(str(e)))


	def create_gl_entries(self):
		try:
			gl_entries = []
			posting_date = nowdate()
			total_amount = flt(self.amount)
			#supplier = self.supplier
			debit_account = "66210000 - Salaries Expats - MCO"
			credit_account = '42110100 - Staff Salary Credit -Expat - MCO'
			currency = self.currency
			remarks = f"Salary {self.type} {self.pay_period}"
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
