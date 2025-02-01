# Copyright (c) 2025, Kossivi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.setup.utils import get_exchange_rate
from bpm.utils.data_layer import share_doc_2
from erp_space import erpspace


class BPMSalesDiscount(Document):
	#def validate(self):
		#share_doc_2(self)
		#erpspace.share_doc(self)

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
		
		# Step 2: Check targets and Step 3: Calculate discount
		for target in self.targets:
			period_key = (target.begin, target.end)

			# Get total for each currency in the period
			total_usd = payment_totals.get(period_key, {}).get('USD', 0)
			total_cdf = payment_totals.get(period_key, {}).get('CDF', 0)

			# Check if target is met
			if total_usd >= target.target:
				discount = total_usd * usd_rate  # Assuming rate is in percentage
				self.add_discount_row(self, target, total_usd, discount, usd_rate, 'USD')
			
			if total_cdf >= target.target:
				discount = total_cdf * cdf_rate  # Assuming rate is in percentage
				exchange_rate = get_exchange_rate("USD", "CDF")
				self.add_discount_row(self, target, total_cdf, discount, cdf_rate, 'CDF')


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


	@frappe.whitelist()
	def fetch_payments(self):
		# Clear existing data in payment tables
		self.payment_usd = []
		self.payment_cdf = []

		total_usd = 0
		total_cdf = 0

		# Loop through targets and fetch payments for each period
		for target in self.targets:
			payments = frappe.get_all(
				"Payment Entry", 
				filters={
					"party": self.customer,
					"posting_date": ["between", [target.begin, target.end]]
				},
				fields=["name", "posting_date", "paid_amount", "paid_to_account_currency"]
			)

			if not payments:
				frappe.msgprint(_("No payments found for the target period from {0} to {1}.").format(target.begin, target.end))
				continue

			for payment in payments:
				if payment.paid_to_account_currency == "USD":
					self.append("payment_usd", {
						"begin": target.begin,
						"end": target.end,
						"payment_entry": payment.name,
						"date": payment.posting_date,
						"amount": payment.base_paid_amount,
						"currency": payment.paid_to_account_currency
					})
				elif payment.paid_to_account_currency == "CDF":
					self.append("payment_cdf", {
						"begin": target.begin,
						"end": target.end,
						"payment_entry": payment.name,
						"date": payment.posting_date,
						"amount": payment.paid_amount,
						"currency": payment.paid_to_account_currency
					})

		# Log the process for debugging or auditing
		frappe.logger().info(f"Payments fetched for customer {self.customer}: USD={self.total_usd}, CDF={self.total_cdf}")

		return "Success"

