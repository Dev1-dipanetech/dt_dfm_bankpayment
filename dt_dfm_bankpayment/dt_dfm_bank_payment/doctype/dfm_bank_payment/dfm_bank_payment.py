# Copyright (c) 2023, Dipane Technologies Pvt Ltd and contributors
# For license information, please see license.txt

from ftplib import FTP
import json
import os
import frappe
from frappe.utils import now
from frappe.model.document import Document

class DFMBankPayment(Document):
    def before_save(self):
        for amount in self.dfm_bank_payment_detail:
            if amount.allocated_amount > 5000000:
                frappe.throw("Allocated amount cannot be more than 5000000 for this invoice {}".format(amount.purchase_invoice))


        for item in self.dfm_bank_payment_detail:
            existing_bank_payment_logs = frappe.get_all('DFM Bank Payment Log Detail',
                filters={
                    'purchase_invoice': item.purchase_invoice,
                    'status': ['not in', ['Cancelled']],
                },
                fields=['parent']
            )
            
            if existing_bank_payment_logs:
                bank_payment_log_docs = [bp.parent for bp in existing_bank_payment_logs]
                bank_payment_log_links = ', '.join(f'<a href="/app/dfm-bank-payment-log/{bp}" target="_blank">{bp}</a>' for bp in bank_payment_log_docs)
                frappe.throw(f"Line item {item.purchase_invoice} is already in process or completed in DFM Bank Payment Log(s): {bank_payment_log_links}")








@frappe.whitelist()
def get_outstanding_invoices(supplier, date):
    filters = {
        'due_date': ['<=', date],
        'status': ['in', ['Submitted', 'Unpaid', 'Overdue', 'Partly Paid']],
		'outstanding_amount': ['<=', 5000000]
    }
    
    if supplier:
        filters['supplier'] = supplier
    
    invoices = frappe.get_all('Purchase Invoice', 
        filters=filters, 
        fields=['name', 'supplier', 'due_date', 'grand_total', 'outstanding_amount','supplier_address']
    )
    
    # Fetch the list of Purchase Invoices already present in DFM Bank Payment Log Detail
    existing_invoices = frappe.get_all('DFM Bank Payment Log Detail',
        filters={
             	'parenttype': 'DFM Bank Payment Log',
		     	'status': ['not in', ['Cancelled']],
            },
        fields=['purchase_invoice']
    )
    
    existing_invoice_names = [invoice.purchase_invoice for invoice in existing_invoices]
    
    # Filter out the Purchase Invoices that are already present in DFM Bank Payment Log Detail
    invoices_to_consider = [invoice for invoice in invoices if invoice.name not in existing_invoice_names]
    
    return invoices_to_consider






@frappe.whitelist()
def generate_text(file_name, filters=None):
    # Fetch settings from DFM Bank Payment Settings doctype
    settings = frappe.get_single("DFM Bank Payment Settings")
    file_path = settings.file_path
    server_address = settings.ftp_server_address
    user = settings.ftp_user
    password = settings.ftp_password

    # Construct the full file path
    file_path = os.path.join(file_path, file_name)

    # Upload the file to the FTP server
    ftp = FTP(server_address)
    ftp.login(user=user, passwd=password)

    with open(file_path, 'rb') as file:
        ftp.storbinary('STOR ' + file_name, file)

    ftp.quit()

    # Read the contents of the file
    with open(file_path, 'r') as file:
        file_content = file.read()

    return True







@frappe.whitelist()
def create_log_document(dfm_bank_payment, transfer_file_name, batch_details):
    try:
        batch_details_json = json.loads(batch_details)
                              
        log_doc = frappe.new_doc("DFM Bank Payment Log")
        log_doc.dfm_bank_payment = dfm_bank_payment
        log_doc.transfer_file_name = transfer_file_name
        log_doc.transfer_date = frappe.utils.now_datetime()
        log_doc.insert()

        for detail in batch_details_json:
            log_detail = log_doc.append("dfm_bank_payment_log_detail", {})
            log_detail.purchase_invoice = detail["purchase_invoice"]
            log_detail.supplier = detail["supplier"]
            log_detail.invoiced_amount = detail["invoiced_amount"]
            log_detail.outstanding_amount = detail["outstanding_amount"]
            log_detail.allocated_amount = detail["allocated_amount"]
            log_detail.status = "In Process"
        log_doc.save()

        frappe.msgprint(f"Log document created for batch {transfer_file_name}")
        return True

    except Exception as e:
        frappe.msgprint(f"Error creating log document: {e}")
        return False