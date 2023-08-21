
import os
import frappe
import time
from ftplib import FTP
from io import BytesIO
from datetime import datetime
from frappe.utils.data import format_datetime



def cron():
    settings = frappe.get_single("DFM Bank Payment Settings")

    # Retrieve the FTP server details from the settings document
    server_address = settings.ftp_server_address
    user = settings.ftp_user
    password = settings.ftp_password

    ftp = FTP(server_address)
    ftp.login(user=user, passwd=password)

    # List all files in the FTP server directory
    file_list = ftp.nlst()

    # Specify the local directory where files will be downloaded
    local_directory = settings.file_path  # Change to your local directory path

    # Get the list of existing file names in DFM Bank Payment Log
    existing_file_names = frappe.get_all("DFM Bank Payment Log", filters={}, fields=["transfer_file_name"])
    existing_file_names = [file["transfer_file_name"] for file in existing_file_names]

    # Download each file from the FTP server to the local directory
    for file_name in file_list:
        if file_name in existing_file_names:
            print("File name {} already exists in DFM Bank Payment Log. Skipping file...".format(file_name))
            continue

        local_file_path = os.path.join(local_directory, file_name)
        try:
            with open(local_file_path, 'wb') as local_file:
                ftp.retrbinary('RETR ' + file_name, local_file.write)
            print("Downloaded file: {}".format(file_name))

            # Read the file content from the downloaded file
            with open(local_file_path, 'r') as file:
                file_content = file.readlines()

            print("File name: {}".format(file_name))
            for line in file_content:
                parts = line.strip().split('~')

                if parts[0] == 'D':
                    purchase_invoice = parts[29]
                    supplier = parts[13]
                    paid_amount = float(parts[3])

                    # Check if the purchase invoice is in the DFM Bank Payment Log Detail
                    dfm_bank_payment_detail_row = frappe.get_value("DFM Bank Payment Log Detail",
                                                                {"purchase_invoice": purchase_invoice,
                                                                    "status": "In Process at Bank"},
                                                                ["parent", "name"])
                    

                    if dfm_bank_payment_detail_row[1]:
                        parent_doc = frappe.get_doc("DFM Bank Payment Log", dfm_bank_payment_detail_row[0])
                        company = parent_doc.company
                        company_bank_account = parent_doc.company_bank_account
                        account_paid_from = parent_doc.account_paid_from
                        account_paid_to = parent_doc.account_paid_to

                        # Create a new Payment Entry document
                        payment_entry = frappe.new_doc("Payment Entry")
                        payment_entry.payment_type = "Pay"
                        payment_entry.posting_date = frappe.utils.nowdate()
                        payment_entry.party_type = "Supplier"
                        payment_entry.party = supplier
                        payment_entry.company = company  # Set the company from the DFM Bank Payment Log Detail
                        payment_entry.bank_account = company_bank_account
                        payment_entry.paid_from = account_paid_from
                        payment_entry.paid_to = account_paid_to
                        payment_entry.paid_amount = paid_amount
                        payment_entry.received_amount = paid_amount
                        payment_entry.reference_no = "1"
                        payment_entry.reference_date = frappe.utils.nowdate()

                        payment_entry.append("references", {
                            "reference_doctype": "Purchase Invoice",
                            "reference_name": purchase_invoice,
                            "allocated_amount": paid_amount
                        })

                        # Save the Payment Entry document
                        payment_entry.insert(ignore_permissions=True)

                        file_in_erp = frappe.get_all("File", filters={"file_name": file_name})

                         # Check if the file_name already exists in File doctype
                        if file_name not in file_in_erp:
                            try:
                                with open(local_file_path, 'rb') as file:
                                    file_content = file.read()

                                # Create a new File record in Frappe
                                file_doc = frappe.get_doc({
                                    "doctype": "File",
                                    "file_name": file_name,
                                    "content": file_content,
                                    "is_private": 1,  # Adjust this based on your requirement
                                    "folder": "Home"  # Specify the folder where you want to store the file
                                })
                                file_doc.insert()

                            except Exception as e:
                                print("Error uploading file: {}".format(str(e)))
                                continue


                        if dfm_bank_payment_detail_row:
                            dfm_bank_payment_detail_doc = frappe.get_doc("DFM Bank Payment Log Detail", dfm_bank_payment_detail_row[1])
                            dfm_bank_payment_detail_doc.status = "Transferred by Bank"
                            dfm_bank_payment_detail_doc.payment_entry = payment_entry.name
                            dfm_bank_payment_detail_doc.receive_file = file_doc.file_url
                            dfm_bank_payment_detail_doc.receive_file_name = file_name
                            dfm_bank_payment_detail_doc.receive_date = frappe.utils.now_datetime()
                            dfm_bank_payment_detail_doc.save()
                        

                        payment_entry.submit()


                        frappe.delete_doc("File", file_name)

                        frappe.db.commit()
                    
                    
                    print("Created Payment Entry for Purchase Invoice: {}, Supplier: {}".format(purchase_invoice, supplier))

        except Exception as e:
            print("Error occurred while processing file {}. Error: {}".format(file_name, str(e)))
            continue

    ftp.quit()
    print("All files have been downloaded and processed.")