# Copyright (c) 2023, Dipane Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DFMBankPaymentLog(Document):
	def before_save(self):
		total_allocated_amount = 0

		for detail in self.get("dfm_bank_payment_log_detail"):
			total_allocated_amount = total_allocated_amount + detail.allocated_amount

		# Set the total_allocated_amount in the main document
		self.total_allocated_amount = total_allocated_amount