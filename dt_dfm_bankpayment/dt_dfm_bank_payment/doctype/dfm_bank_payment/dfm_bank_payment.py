# Copyright (c) 2023, Dipane Technologies Pvt Ltd and contributors
# For license information, please see license.txt

from ftplib import FTP
import io
import json
import os
import frappe
from frappe.utils import now
from frappe.model.document import Document
import traceback

class DFMBankPayment(Document):
    def before_save(self):

        filter_company = self.company
        
        # List to store rows with different company values
        rows_with_different_company = []

        # Compare the company value in each row with the filter_company value
        for item in self.dfm_bank_payment_detail:
            if item.company != filter_company:
                rows_with_different_company.append(item.purchase_invoice)  # Add the purchase invoice to the list

        # If there are rows with different company values, raise an error
        if rows_with_different_company:
            error_message = "The following rows in dfm_bank_payment_detail have different company values: {}".format(
                ', '.join(rows_with_different_company)
            )
            frappe.throw(error_message)


        for amount in self.dfm_bank_payment_detail:
            if amount.allocated_amount is None or amount.allocated_amount <= 0:
                frappe.throw("Allocated amount must be greater than 0 for this invoice {}".format(amount.purchase_invoice))
            elif amount.allocated_amount > 5000000:
                frappe.throw("Allocated amount cannot be more than 5000000 for this invoice {}".format(amount.purchase_invoice))

        for item in self.dfm_bank_payment_detail:
            existing_bank_payment_logs = frappe.get_all('DFM Bank Payment Log Detail',
                filters={
                    'purchase_invoice': item.purchase_invoice,
                    'status': ['not in', ['Rejected by Bank']],
                },
                fields=['parent']
            )
            
            if existing_bank_payment_logs:
                bank_payment_log_docs = [bp.parent for bp in existing_bank_payment_logs]
                bank_payment_log_links = ', '.join(f'<a href="/app/dfm-bank-payment-log/{bp}" target="_blank">{bp}</a>' for bp in bank_payment_log_docs)
                frappe.throw(f"Line item {item.purchase_invoice} is already in process or completed in DFM Bank Payment Log(s): {bank_payment_log_links}")
                
    
    
    def before_submit(self):

        filter_company = self.company
        
        # List to store rows with different company values
        rows_with_different_company = []

        # Compare the company value in each row with the filter_company value
        for item in self.dfm_bank_payment_detail:
            if item.company != filter_company:
                rows_with_different_company.append(item.purchase_invoice)  # Add the purchase invoice to the list

        # If there are rows with different company values, raise an error
        if rows_with_different_company:
            error_message = "The following rows in dfm_bank_payment_detail have different company values: {}".format(
                ', '.join(rows_with_different_company)
            )
            frappe.throw(error_message)

        for amount in self.dfm_bank_payment_detail:
            if amount.allocated_amount is None or amount.allocated_amount <= 0:
                frappe.throw("Allocated amount must be greater than 0 for this invoice {}".format(amount.purchase_invoice))
            elif amount.allocated_amount > 5000000:
                frappe.throw("Allocated amount cannot be more than 5000000 for this invoice {}".format(amount.purchase_invoice))

        for item in self.dfm_bank_payment_detail:
            existing_bank_payment_logs = frappe.get_all('DFM Bank Payment Log Detail',
                filters={
                    'purchase_invoice': item.purchase_invoice,
                    'status': ['not in', ['Rejected by Bank']],
                },
                fields=['parent']
            )
            
            if existing_bank_payment_logs:
                bank_payment_log_docs = [bp.parent for bp in existing_bank_payment_logs]
                bank_payment_log_links = ', '.join(f'<a href="/app/dfm-bank-payment-log/{bp}" target="_blank">{bp}</a>' for bp in bank_payment_log_docs)
                frappe.throw(f"Line item {item.purchase_invoice} is already in process or completed in DFM Bank Payment Log(s): {bank_payment_log_links}")







# @frappe.whitelist()
# def get_outstanding_invoices(supplier, due_date, company, purchase_invoice):
#     filters = {
#         'due_date': ['<=', due_date],
#         'status': ['in', ['Submitted', 'Unpaid', 'Overdue', 'Partly Paid']],
#         'outstanding_amount': ['<=', 5000000]
#     }
    
#     if supplier:
#         filters['supplier'] = supplier
        
#     if company:
#         filters['company'] = company

#     if purchase_invoice:
#         filters['name'] = purchase_invoice
    
#     invoices = frappe.get_all('Purchase Invoice', 
#         filters=filters, 
#         fields=['name', 'company', 'supplier', 'due_date', 'grand_total', 'outstanding_amount','supplier_address']
#     )
    
#     # Fetch the list of Purchase Invoices already present in DFM Bank Payment Log Detail
#     existing_invoices = frappe.get_all('DFM Bank Payment Log Detail',
#         filters={
#              	'parenttype': 'DFM Bank Payment Log',
# 		     	'status': ['not in', ['Rejected by Bank']],
#             },
#         fields=['purchase_invoice']
#     )
    
#     existing_invoice_names = [invoice.purchase_invoice for invoice in existing_invoices]
    
#     # Filter out the Purchase Invoices that are already present in DFM Bank Payment Log Detail
#     invoices_to_consider = [invoice for invoice in invoices if invoice.name not in existing_invoice_names]
    
#     # Fetch the name of the Bank Account based on filters
#     bank_account_name = frappe.db.get_value('Bank Account',
#         filters={
#             'is_company_account': 0,
#             # 'company': company,
#             'party_type': "Supplier",
#             'party': supplier,
#             'is_default': 1
#         },
#         fieldname='name'
#     )
    
#     # Return invoices to consider along with bank_account_name
#     return {'invoices': invoices_to_consider, 'bank_account_name': bank_account_name}









@frappe.whitelist()
def get_outstanding_invoices(supplier, due_date, company, purchase_invoice):
    filters = {
        'due_date': ['<=', due_date],
        'status': ['in', ['Submitted', 'Unpaid', 'Overdue', 'Partly Paid']],
        'outstanding_amount': ['<=', 5000000]
    }
    
    if supplier:
        filters['supplier'] = supplier
        
    if company:
        filters['company'] = company

    if purchase_invoice:
        filters['name'] = purchase_invoice
    
    invoices = frappe.get_all('Purchase Invoice', 
        filters=filters, 
        fields=['name', 'company', 'supplier', 'due_date', 'grand_total', 'outstanding_amount','supplier_address']
    )
    
    # Fetch the list of Purchase Invoices already present in DFM Bank Payment Log Detail
    existing_invoices = frappe.get_all('DFM Bank Payment Log Detail',
        filters={
             	'parenttype': 'DFM Bank Payment Log',
		     	'status': ['not in', ['Rejected by Bank']],
            },
        fields=['purchase_invoice']
    )
    
    existing_invoice_names = [invoice.purchase_invoice for invoice in existing_invoices]
    
    # Filter out the Purchase Invoices that are already present in DFM Bank Payment Log Detail
    invoices_to_consider = [invoice for invoice in invoices if invoice.name not in existing_invoice_names]
    
    # Fetch the name of the Bank Account based on filters
    bank_account_name = None  # Initialize with None
    
    # Check if the supplier has a default bank account, if not, pick any one
    if supplier:
        bank_account_name = frappe.db.get_value('Bank Account',
            filters={
                # 'is_company_account': 0,
                'party_type': "Supplier",
                'party': supplier,
                'is_default': 1
            },
            fieldname='name'
        )
    
    # If a default bank account is not found, pick any one
    if not bank_account_name:
        bank_account = frappe.get_all('Bank Account',
            filters={
                # 'is_company_account': 0,
                'party_type': "Supplier",
                'party': supplier
            },
            fields=['name'],
            limit=1  # Limit to 1 record
        )
        if bank_account:
            bank_account_name = bank_account[0].name
    
    # Return invoices to consider along with bank_account_name
    return {'invoices': invoices_to_consider, 'bank_account_name': bank_account_name}







@frappe.whitelist()
def get_supplier_bank_account(supplier):
    # Check if there is a default bank account for the supplier
    default_bank_account_name = frappe.get_value('Bank Account',
        filters={
            'party_type': "Supplier",
            'party': supplier,
            'is_default': 1  # Check for default bank account
        },
        fieldname='name'
    )

    if default_bank_account_name:
        return default_bank_account_name

    # If no default bank account is set, pick any available bank account for the supplier
    bank_account_name = frappe.db.sql("""
        SELECT name
        FROM `tabBank Account`
        WHERE party_type = 'Supplier'
        AND party = %s
        LIMIT 1
    """, supplier, as_dict=True)

    if bank_account_name:
        return bank_account_name[0].name

    # If no bank account is found, return None or raise an exception based on your requirements
    return None  # You can customize this based on your needs











# @frappe.whitelist()
# def generate_text(file_name, filters=None):
#     try:
#         # Fetch settings from DFM Bank Payment Settings doctype
#         settings = frappe.get_single("DFM Bank Payment Settings")
#         file_path = settings.file_path
#         server_address = settings.ftp_server_address
#         user = settings.ftp_user
#         password = settings.ftp_password

#         # Construct the full file path
#         file_path = os.path.join(file_path, file_name)

#         # Upload the file to the FTP server
#         ftp = FTP(server_address)
#         ftp.login(user=user, passwd=password)

#         with open(file_path, 'rb') as file:
#             ftp.storbinary('STOR ' + file_name, file)

#         ftp.quit()

#         # Read the contents of the file
#         with open(file_path, 'r') as file:
#             file_content = file.read()

#         # Create a new File record in Frappe
#         file_doc = frappe.get_doc({
#             "doctype": "File",
#             "file_name": file_name,
#             "content": file_content,
#             "is_private": 1,  # Adjust this based on your requirement
#             "folder": "Home"  # Specify the folder where you want to store the file
#         })
#         file_doc.insert()

#         return True

#     except Exception as e:
#         frappe.msgprint(f"Error generating or uploading file: {e}")
#         return False




@frappe.whitelist()
def generate_text(file_name, file_content, filters=None):
    try:
        # Fetch settings from DFM Bank Payment Settings doctype
        settings = frappe.get_single("DFM Bank Payment Settings")
        server_address = settings.ftp_server_address
        user = settings.ftp_user
        password = settings.ftp_password

        # Upload the file content to the FTP server
        ftp = FTP(server_address)
        ftp.login(user=user, passwd=password)
        ftp.set_pasv(False)

        file_data = io.BytesIO(file_content.encode('utf-8'))
        ftp.storbinary('STOR ' + file_name, file_data)

        ftp.quit()

        # Create a new File record in Frappe (you may want to adjust this part)
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "content": file_content,
            "is_private": 1,  # Adjust this based on your requirement
            "folder": "Home"  # Specify the folder where you want to store the file
        })
        file_doc.insert()

        return True

    except Exception as e:
        traceback.print_exc()
        frappe.msgprint(f"Error generating or uploading file: {e}")
        return False










@frappe.whitelist()
def create_log_document(dfm_bank_payment, transfer_file_name, batch_details):
    try:
        batch_details_json = json.loads(batch_details)

        dfm_bank_payment_doc = frappe.get_doc("DFM Bank Payment", dfm_bank_payment)
        company = dfm_bank_payment_doc.company
        company_bank_account = dfm_bank_payment_doc.company_bank_account
        account_paid_from = dfm_bank_payment_doc.account_paid_from
        account_paid_to = dfm_bank_payment_doc.account_paid_to
                              
        log_doc = frappe.new_doc("DFM Bank Payment Log")
        log_doc.dfm_bank_payment = dfm_bank_payment
        log_doc.posting_date = frappe.utils.nowdate()
        log_doc.company = company
        log_doc.company_bank_account = company_bank_account
        log_doc.account_paid_from = account_paid_from
        log_doc.account_paid_to = account_paid_to
        log_doc.transfer_file_name = transfer_file_name
        log_doc.transfer_date = frappe.utils.now_datetime()
        
        # Attach the file if it exists in the File doctype
        existing_file = frappe.get_doc("File", {"file_name": transfer_file_name})
        if existing_file:
            file_name = "/private/files/" + existing_file.file_name
            log_doc.set("transfer_file", file_name)
            frappe.db.commit()  # Commit the changes to ensure attachment is saved
        
        log_doc.insert()

        for detail in batch_details_json:
            log_detail = log_doc.append("dfm_bank_payment_log_detail", {})
            log_detail.purchase_invoice = detail["purchase_invoice"]
            log_detail.company = detail["company"]
            log_detail.supplier = detail["supplier"]
            log_detail.due_date = detail["due_date"]
            log_detail.invoiced_amount = detail["invoiced_amount"]
            log_detail.outstanding_amount = detail["outstanding_amount"]
            log_detail.allocated_amount = detail["allocated_amount"]
            log_detail.supplier_bank = detail["supplier_bank"]
            log_detail.supplier_address = detail["supplier_address"]
            log_detail.status = "In Process at Bank"
        log_doc.save()

        frappe.msgprint(f"Log document created for batch {transfer_file_name}")

        # Delete the stored temporary file
        temp_file_path = os.path.join("/private/files/temp", transfer_file_name)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return True

    except Exception as e:
        frappe.msgprint(f"Error creating log document: {e}")
        return False








@frappe.whitelist()
def get_linked_payments(purchase_invoice):
    linked_payments = []

    # Query linked payments based on purchase_invoice in the child table
    dfm_payments = frappe.get_all("DFM Bank Payment Detail", filters={"purchase_invoice": purchase_invoice}, fields=["parent", "purchase_invoice"])
    
    for payment in dfm_payments:
        linked_payments.append({"parent": payment.parent, "purchase_invoice": payment.purchase_invoice})

    return linked_payments






@frappe.whitelist()
def delete_linked_rows(purchase_invoice, parent):
    try:
        # Find the parent DFM Bank Payment document
        dfm_bank_payment = frappe.get_doc("DFM Bank Payment", parent)

        # Check if the parent DFM Bank Payment is submitted
        if dfm_bank_payment.docstatus == 1:
            # Create a list to store rows to be removed
            rows_to_remove = []

            # Identify rows to be removed and add to the list
            for row in dfm_bank_payment.dfm_bank_payment_detail:
                if row.purchase_invoice == purchase_invoice:
                    rows_to_remove.append(row)

            # Remove identified rows from the child table
            for row in rows_to_remove:
                dfm_bank_payment.dfm_bank_payment_detail.remove(row)

            # Save the parent document
            dfm_bank_payment.save()
            return True
        else:
            frappe.msgprint("Parent DFM Bank Payment document is not submitted. Cannot delete linked rows.")
            return False

    except Exception as e:
        frappe.log_error(e)
        return False
