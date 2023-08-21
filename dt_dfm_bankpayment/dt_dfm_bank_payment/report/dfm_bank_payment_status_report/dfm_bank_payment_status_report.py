# Copyright (c) 2023, Dipane Technologies Pvt Ltd and contributors
# For license information, please see license.txt


import datetime
import frappe
from frappe import _


def execute(filters=None):
    columns = [
        {
            "fieldname": "posting_date",
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "party_type",
            "label": _("Party Type"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "party",
            "label": _("Party"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 120
        },
        {
            "fieldname": "payable_account",
            "label": _("Payable Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 180
        },
        {
            "fieldname": "voucher_type",
            "label": _("Voucher Type"),
            "fieldtype": "Data",
            "width": 130
        },
        {
            "fieldname": "voucher_no",
            "label": _("Voucher No"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 180
        },
        {
            "fieldname": "due_date",
            "label": _("Due Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "invoiced_amount",
            "label": _("Invoiced Amount"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "paid_amount",
            "label": _("Paid Amount"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "outstanding_amount",
            "label": _("Outstanding Amount"),
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "fieldname": "transfer_date",
            "label": _("Transfer Date"),
            "fieldtype": "Date",
            "width": 130
        },
        {
            "fieldname": "transfer_file_name",
            "label": _("Transfer File Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "receive_date",
            "label": _("Receive Date"),
            "fieldtype": "Date",
            "width": 130
        },
        {
            "fieldname": "receive_file_name",
            "label": _("Receive File Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "payment_entry",
            "label": _("Payment Entry"),
            "fieldtype": "Link",
            "options": "Payment Entry",
            "width": 150
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 160
        },
        {
            "fieldname": "company",
            "label": _("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 180
        }
    ]

    data = []
    query = """
        SELECT 
            bpl.creation as posting_date,
            "Supplier" as party_type,
            bpld.supplier as party,
            bpl.account_paid_to as payable_account,
            "Purchase Invoice" as voucher_type,
            bpld.purchase_invoice as voucher_no,
            bpld.due_date as due_date,
            bpld.invoiced_amount as invoiced_amount,
            per.allocated_amount as paid_amount,
            CASE WHEN bpld.payment_entry IS NOT NULL THEN per.outstanding_amount ELSE bpld.outstanding_amount END as outstanding_amount,
            bpl.transfer_date as transfer_date,
            bpl.transfer_file_name as transfer_file_name,
            bpld.receive_date as receive_date,
            bpld.receive_file_name as receive_file_name,
            bpld.payment_entry as payment_entry,
            bpld.status as status,
            bpl.company as company
        FROM `tabDFM Bank Payment Log Detail` as bpld
        LEFT JOIN `tabDFM Bank Payment Log` as bpl ON bpl.name = bpld.parent
        LEFT JOIN `tabPayment Entry` as pe ON bpld.payment_entry = pe.name
        LEFT JOIN `tabPayment Entry Reference` as per ON pe.name = per.parent
    """

    if filters:
        # You can add any filters here based on your requirements
        pass

    data = frappe.db.sql(query, filters, as_dict=1)
    return columns, data
