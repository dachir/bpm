# Copyright (c) 2025, Kossivi and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import (getdate, flt)
from frappe.model.document import Document
from erpnext.setup.utils import get_exchange_rate
from bpm.utils.data_layer import share_doc_2
from erp_space import erpspace


class BPMSalesDiscount(Document):
	def on_cancel(self):
		self.clear_payment_entries()

	def on_trash(self):
		self.clear_payment_entries()

	def validate(self):
		self.validate_period_overlap()
		erpspace.share_doc(self)

	def before_save(self):
		# Fetch USD and CDF rates from settings
		usd_rate = frappe.db.get_single_value('BPM Settings', 'usd_rate')
		cdf_rate = frappe.db.get_single_value('BPM Settings', 'cdf_rate')

		# Step 1: Sum up entries in payment_usd and payment_cdf
		payment_totals = {}
		for table in ['payment_usd', 'payment_cdf']:
			for payment in self.get(table, []):
				period_key = (payment.begin, payment.end)
				currency = payment.currency

				if period_key not in payment_totals:
					payment_totals[period_key] = {}
				
				payment_totals[period_key][currency] = (
					payment_totals[period_key].get(currency, 0) + payment.amount
				)

				frappe.db.set_value("Payment Entry",payment.payment_entry, "custom_discount_entry", self.name)
		
		# Step 2: Check targets and Step 3: Calculate discount
		self.details = []
		for target in self.targets:
			period_key = (target.begin, target.end)

			# Get total for each currency in the period
			total_usd = payment_totals.get(period_key, {}).get('USD', 0)
			total_cdf = payment_totals.get(period_key, {}).get('CDF', 0)
			exchange_rate = get_exchange_rate("CDF", "USD") or 1
			total = total_usd + (total_cdf * exchange_rate)

			# Check if target is met
			if total >= target.target:
				if total_usd > 0:
					discount = total_usd * usd_rate / 100  # Assuming rate is in percentage
					self.add_discount_row(target, total_usd, discount, usd_rate, 'USD')
				if total_cdf > 0:
					discount = total_cdf * cdf_rate / 100  # Assuming rate is in percentage
					self.add_discount_row(target, total_cdf, discount, cdf_rate, 'USD')

			
			#exchange_rate = get_exchange_rate("CDF", "USD") or 1
			#if total_cdf * exchange_rate >= target.target:
			#	discount = total_cdf * cdf_rate / 100  # Assuming rate is in percentage
			#	#exchange_rate = get_exchange_rate("CDF", "USD")
			#	self.add_discount_row(target, total_cdf, discount, cdf_rate, 'CDF')

		

	
	def on_submit(self):
		self.make_jv_entry()


	def add_discount_row(self, target, total, discount, rate, currency):
		"""Add a new row to the details table."""
		self.append('details', {
			'begin': target.begin,
			'end': target.end,
			'target': target.target,
			'total': total,
			'rate': rate,
			'discount': discount,
			'currency': currency
		})

	def clear_payment_entries(self):
		for table in ['payment_usd', 'payment_cdf']:
			for payment in self.get(table, []):
				frappe.db.set_value("Payment Entry",payment.payment_entry, "custom_discount_entry", None)


	@frappe.whitelist()
	def fetch_payments(self):
		payments_usd = []
		payments_cdf = []

		default_currency = frappe.db.get_single_value('Global Defaults', 'default_currency')

		for target in self.targets:
			payments = frappe.get_all(
				"Payment Entry",
				filters={
					"party": self.customer,
					"posting_date": ["between", [target.begin, target.end]],
					"docstatus": 1,
					"custom_discount_entry": ["is", "not set"] ,
				},
				fields=["name", "posting_date", "paid_amount", "paid_to_account_currency", "received_amount"]
			)

			for payment in payments:
				if payment['paid_to_account_currency'] == "USD":
					payments_usd.append({
						"begin": target.begin,
						"end": target.end,
						"payment_entry": payment['name'],
						"date": payment['posting_date'],
						"amount": payment['paid_amount'],
						"currency": payment['paid_to_account_currency']
					})
				elif payment['paid_to_account_currency'] == "CDF":
					payments_cdf.append({
						"begin": target.begin,
						"end": target.end,
						"payment_entry": payment['name'],
						"date": payment['posting_date'],
						"amount": payment['paid_amount'],
						"currency": payment['paid_to_account_currency'],
						"company_currency": default_currency,
						"payment_amount": payment['received_amount']
					})

		# Return results as a dictionary
		return {
			"payments_usd": payments_usd,
			"payments_cdf": payments_cdf
		}


	def make_jv_entry(self):
		default_currency = erpnext.get_company_currency(self.company)
		total_discount = 0
		for d in self.details:
			#discount = d.discount or 0
			
			# Get the exchange rate
			#exchange_rate = get_exchange_rate(d.currency, default_currency) or 1
			
			# Convert the discount to the default currency
			#converted_discount = discount * exchange_rate
			total_discount += d.discount or 0


		jv_name = ""

		journal_entry = frappe.new_doc("Journal Entry")
		journal_entry.voucher_type = "Credit Note"
		journal_entry.cheque_no = self.name
		journal_entry.cheque_date = self.date_request
		journal_entry.user_remark = _("Sales discounts for {0} from {1} to {2}").format(
			self.customer, self.begin, self.end
		)
		journal_entry.company = self.company
		journal_entry.posting_date = getdate()

		company_doc = frappe.get_doc("Company", self.company)

		journal_entry.append("accounts", {
			"account": company_doc.default_discount_account,  
			"debit_in_account_currency": flt(total_discount,2),
			"credit_in_account_currency": 0,
			"cost_center": "CC012 - Sales - MCO",
			"branch": self.branch,
			"currency": default_currency
		})
		
		journal_entry.append("accounts", {
			"account": company_doc.default_receivable_account,  
			"party_type": "Customer",
			"party": self.customer,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": flt(total_discount,2),
			"cost_center": "CC012 - Sales - MCO",
			"branch": self.branch,
			"currency": default_currency
		})
		
		# Save and submit the journal entry
		journal_entry.insert()
		journal_entry.submit()


	def validate_period_overlap(self):
		if not self.customer or not self.begin or not self.end:
			return

		# Query for overlapping periods
		overlapping_periods = frappe.db.sql(
			"""
				SELECT name, begin, end 
				FROM `tabBPM Sales Discount`
				WHERE customer = %(customer)s AND name != %(current_name)s AND docstatus = 1  -- Exclude the current document in the check
				AND (
					(begin <= %(end)s AND end >= %(begin)s)  -- Overlap condition
				)
			""", {"customer": self.customer,"begin": self.begin,"end": self.end,"current_name": self.name}, as_dict=True
		)

		# If any overlaps are found, raise a validation error
		if overlapping_periods:
			overlapping_entries = ", ".join([f"{entry['name']} (from {entry['begin']} to {entry['end']})" for entry in overlapping_periods])
			frappe.throw(f"The selected period overlaps with existing periods: {overlapping_entries}")
				
