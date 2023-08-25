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
            "width": 130
        },
        {
            "fieldname": "dfm_bank_payment_log",
            "label": _("DFM Bank Payment Log"),
            "fieldtype": "Link",
            "options": "DFM Bank Payment Log",
            "width": 180
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
            "width": 150
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
            "label": _("E2B Transfer Date"),
            "fieldtype": "Date",
            "width": 130
        },
        {
            "fieldname": "transfer_file_name",
            "label": _("E2B Transfer File Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "transfer_file_url",
            "label": _("E2B Transfer File URL"),
            "fieldtype": "HTML",
            "width": 200
        },
        {
            "fieldname": "receive_date",
            "label": _("B2E Receive Date"),
            "fieldtype": "Date",
            "width": 130
        },
        {
            "fieldname": "receive_file_name",
            "label": _("B2E Receive File Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "receive_file_url",
            "label": _("B2E Receive File URL"),
            "fieldtype": "HTML",
            "width": 200
        },
        {
            "fieldname": "payment_entry",
            "label": _("Payment Entry"),
            "fieldtype": "Link",
            "options": "Payment Entry",
            "width": 180
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
            bpl.name as dfm_bank_payment_log,
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
            CONCAT('<a href="', bpl.transfer_file, '" target="_blank">', bpl.transfer_file, '</a>') as transfer_file_url,
            bpld.receive_date as receive_date,
            bpld.receive_file_name as receive_file_name,
            CONCAT('<a href="', bpld.receive_file, '" target="_blank">', bpld.receive_file, '</a>') as receive_file_url,
            bpld.payment_entry as payment_entry,
            bpld.status as status,
            bpl.company as company
        FROM `tabDFM Bank Payment Log Detail` as bpld
        LEFT JOIN `tabDFM Bank Payment Log` as bpl ON bpl.name = bpld.parent
        LEFT JOIN `tabPayment Entry` as pe ON bpld.payment_entry = pe.name
        LEFT JOIN `tabPayment Entry Reference` as per ON pe.name = per.parent
    """

    if filters:
        query += " WHERE 1=1"  # Start with a valid WHERE clause

        if filters.get("company"):
            query += f" AND bpl.company = '{filters.get('company')}'"

        if filters.get("posting_date"):
            query += f" AND DATE(bpl.creation) <= '{filters.get('posting_date')}'"

        if filters.get("dfm_bank_payment_log"):
            query += f" AND bpl.name = '{filters.get('dfm_bank_payment_log')}'"

        if filters.get("supplier"):
            query += f" AND bpld.supplier = '{filters.get('supplier')}'"

        if filters.get("purchase_invoice"):
            query += f" AND bpld.purchase_invoice = '{filters.get('purchase_invoice')}'"

        if filters.get("payment_entry"):
            query += f" AND bpld.payment_entry = '{filters.get('payment_entry')}'"

        if filters.get("payable_account"):
            query += f" AND bpl.account_paid_to = '{filters.get('payable_account')}'"

        if filters.get("status"):
            query += f" AND bpld.status = '{filters.get('status')}'"


    data = frappe.db.sql(query, filters, as_dict=1)
    return columns, data
