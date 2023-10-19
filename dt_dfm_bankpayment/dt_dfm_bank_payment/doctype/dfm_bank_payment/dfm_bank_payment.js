// Copyright (c) 2023, Dipane Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('DFM Bank Payment', {
	refresh: function(frm) {
		frm.set_query('purchase_invoice', function() {
            return {
                filters: {
                    'status': ['in', ['Submitted', 'Unpaid', 'Overdue', 'Partly Paid']],
					'company': frm.doc.company,
					'supplier': frm.doc.supplier
                }
            };
        });


        frm.set_query('company_bank_account', function() {
            return {
                filters: {
					'company': frm.doc.company,
                    'is_company_account': 1
                }
            };
        });


        frm.set_query('account_paid_from', function() {
            return {
                filters: {
                    'account_type': ['in', ['Bank', 'Cash']],
					'company': frm.doc.company,
                    'is_group': 0,
					'disabled': 0,

                }
            };
        });


        frm.set_query('account_paid_to', function() {
            return {
                filters: {
                    'account_type': ['in', ['Payable']],
					'company': frm.doc.company,
                    'is_group': 0,
					'disabled': 0,

                }
            };
        });


        frm.fields_dict.dfm_bank_payment_detail.grid.get_field('purchase_invoice').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                filters: {
                    'status': ['in', ['Submitted', 'Unpaid', 'Overdue', 'Partly Paid']],
                    'company': frm.doc.company
                }
            };
        };
        

        frm.fields_dict.dfm_bank_payment_detail.grid.get_field('supplier_bank').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                filters: {
                    // 'is_company_account': 0,
					// 'company': child.company,
                    'party_type': "Supplier",
					'party': child.supplier
                }
            };
        };


        if (frm.doc.__islocal) {
            frm.toggle_reqd('dfm_bank_payment_detail', true);

            if (!frm.doc.dfm_bank_payment_detail || frm.doc.dfm_bank_payment_detail.length === 0) {
                // Add a blank row to the 'dfm_bank_payment_detail' table field
                frm.fields_dict['dfm_bank_payment_detail'].grid.add_new_row();
            }    
        } 
        else {
            if (frm.doc.docstatus == 0) {
                frm.toggle_reqd('dfm_bank_payment_detail', true);

                if (!frm.doc.dfm_bank_payment_detail || frm.doc.dfm_bank_payment_detail.length === 0) {
                    // Add a blank row to the 'dfm_bank_payment_detail' table field
                    frm.fields_dict['dfm_bank_payment_detail'].grid.add_new_row();
                }    
            } 
            else {
                frm.toggle_reqd('dfm_bank_payment_detail', false);
            }
        }

	},

    

	get_outstanding_invoices: function(frm) {
        frappe.call({
            method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.get_outstanding_invoices',
            args: {
                supplier: cur_frm.doc.supplier || '',
                due_date: cur_frm.doc.due_date,
                company: cur_frm.doc.company || '',
                purchase_invoice: cur_frm.doc.purchase_invoice || ''
            },
            callback: function(response) {
                var invoices = response.message.invoices;
                var bank_account_name = response.message.bank_account_name;
    
                var existing_invoice_names = frm.doc.dfm_bank_payment_detail.map(row => row.purchase_invoice);
    
                // Update existing rows with data from fetched invoices
                frm.doc.dfm_bank_payment_detail.forEach(row => {
                    var matching_invoice = invoices.find(invoice => invoice.name === row.purchase_invoice);
                    if (matching_invoice) {
                        row.company = matching_invoice.company;
                        row.supplier = matching_invoice.supplier;
                        row.due_date = matching_invoice.due_date;
                        row.invoiced_amount = matching_invoice.grand_total;
                        row.outstanding_amount = matching_invoice.outstanding_amount;
                        row.allocated_amount = matching_invoice.outstanding_amount;
                        row.supplier_address = matching_invoice.supplier_address;
                        row.supplier_bank = bank_account_name; // Set the bank account name
                    }
                });
    
                // Add new rows for invoices that are not already in the table
                var new_invoices = invoices.filter(invoice => !existing_invoice_names.includes(invoice.name));
                $.each(new_invoices, function(i, invoice) {
                    var row = frappe.model.add_child(cur_frm.doc, 'DFM Bank Payment Detail', 'dfm_bank_payment_detail');
                    row.purchase_invoice = invoice.name;
                    row.company = invoice.company;
                    row.supplier = invoice.supplier;
                    row.due_date = invoice.due_date;
                    row.invoiced_amount = invoice.grand_total;
                    row.outstanding_amount = invoice.outstanding_amount;
                    row.allocated_amount = invoice.outstanding_amount;
                    row.supplier_address = invoice.supplier_address;
                    row.supplier_bank = bank_account_name; // Set the bank account name
                });
    
                // Refresh child table and main form
                cur_frm.refresh_field('dfm_bank_payment_detail');
                cur_frm.refresh();


                // Make another frappe.call to fetch and set the bank account for each supplier
                frm.doc.dfm_bank_payment_detail.forEach(row => {
                    if (!row.supplier_bank) {
                        frappe.call({
                            method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.get_supplier_bank_account',
                            args: {
                                supplier: row.supplier || ''
                            },
                            callback: function(bank_response) {
                                var supplier_bank_account = bank_response.message;
                                row.supplier_bank = supplier_bank_account;
                                // cur_frm.refresh_field('dfm_bank_payment_detail');
                            }
                        });
                    }
                });

            }
        });
    },
    
	

	before_submit: function(frm) {
        var batches = splitIntoBatches(frm.doc.dfm_bank_payment_detail, 3000000); // Split into batches of 30 lacs
        var currentIndex = 0;

        function processNextBatch() {
            if (currentIndex >= batches.length) {
                frappe.msgprint("All batch files are sent to the FTP Server");
                return;
            }

            var batch = batches[currentIndex];
            var batchFileName = frm.doc.name + '_batch_' + (currentIndex + 1) + '.txt';
            var fileData = getBatchData(batch, batchFileName, frm.doc);

            // Download the text file
            var blob = new Blob([fileData], { type: 'text/plain' });
            var url = URL.createObjectURL(blob);
            var link = document.createElement('a');
            link.href = url;
            link.download = batchFileName;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

			setTimeout(function() {
				frappe.call({
					method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.generate_text',
					args: {
						file_name: batchFileName,
                        file_content: fileData 
					},
					callback: function(response) {
						if (response.message) {

                            setTimeout(function() {
                                frappe.call({
                                    method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.create_log_document',
                                    args: {
                                        dfm_bank_payment: frm.doc.name,
                                        transfer_file_name: batchFileName,
                                        batch_details: JSON.stringify(batch),
                                    },
                                    callback: function(log_response) {
                                        if (log_response.message) {
                                            frappe.msgprint("Log document created successfully");
                                        } else {
                                            frappe.msgprint("Error creating log document");
                                        }

                                        currentIndex++;
                                        processNextBatch(); // Process the next batch
                                    }
                                });
                            }, 1000);

						} else {
							frappe.msgprint("Error generating text file");
							currentIndex++;
							processNextBatch(); // Process the next batch
						}
					}
				});
			}, 3000);
        }

        // Start processing the first batch
        processNextBatch();
    }
});




// function splitIntoBatches(data, batchSize) {
//     var batches = [];
//     var currentBatch = [];
//     var currentBatchAmount = 0;

//     data.sort(function(a, b) {
//         return (a.allocated_amount || 0) - (b.allocated_amount || 0);
//     });

//     data.forEach(function(row) {
//         var allocatedAmount = row.allocated_amount || 0;

//         if ((currentBatchAmount + allocatedAmount) <= batchSize) {
//             // Add to the current batch
//             currentBatch.push(row);
//             currentBatchAmount += allocatedAmount;
//         } else {
//             // Push the current batch and start a new one
//             batches.push(currentBatch);
//             currentBatch = [row];
//             currentBatchAmount = allocatedAmount;
//         }
//     });

//     if (currentBatch.length > 0) {
//         batches.push(currentBatch);
//     }

//     return batches;
// }





// new coding
function splitIntoBatches(data, batchSize) {
    var batches = [];
    var currentBatch = [];
    var currentBatchAmount = 0;

    // Sort the data first by supplier, then by allocated amount
    data.sort(function(a, b) {
        if (a.supplier !== b.supplier) {
            return a.supplier.localeCompare(b.supplier);
        }
        return (a.allocated_amount || 0) - (b.allocated_amount || 0);
    });

    data.forEach(function(row) {
        var allocatedAmount = row.allocated_amount || 0;

        if ((currentBatchAmount + allocatedAmount) <= batchSize) {
            // Add to the current batch
            currentBatch.push(row);
            currentBatchAmount += allocatedAmount;
        } else {
            // Push the current batch and start a new one
            batches.push(currentBatch);
            currentBatch = [row];
            currentBatchAmount = allocatedAmount;
        }
    });

    if (currentBatch.length > 0) {
        batches.push(currentBatch);
    }

    return batches;
}





// function getBatchData(batch, fileName, doc) {
    
//     console.log(batch, fileName)
//     var batchData = '';
//     var batch_amount = getTotalAllocatedAmount(batch);
//     var batch_length = batch.length;

//     batchData += 'H~DUMMY~~~~' + fileName + '~' + '\n' +
//         'B~' + batch_length + '~' + batch_amount + '~' + '20130625_HAS03' + '~' +
//         (frappe.datetime.str_to_user(doc.due_date).replace(/-/g, '/') || '') +
//         '~NETPAY' + '\n';

//     batch.forEach(function(row) {
//         batchData += 'D~~' +
//             'NEFT~' +
//             (row.allocated_amount.toFixed(2)  || '') +
//             '~' +
//             (frappe.datetime.str_to_user(doc.due_date).replace(/-/g, '/') || '') +
//             '~' +
//             (frappe.datetime.str_to_user(doc.due_date).replace(/-/g, '/') || '') +
//             '~~~~~~' +
//             'M~~' +
//             (row.supplier || '') +
//             '~' +
//             (row.supplier_bank || '') +
//             '~' +
//             (row.supplier_bank_ifsc_code || '') +
//             '~' +
//             (row.supplier_account_no || '') +
//             '~~~' +
//             (row.supplier_address_line_1 || '') +
//             '~' +
//             (row.supplier_address_line_2 || '') +
//             '~~~~' +
//             (row.supplier_city || '') +
//             '~' +
//             (row.supplier_zipcode || '') +
//             '~' +
//             (row.supplier_state || '') +
//             '~' +
//             (row.supplier_email || '') +
//             '~' +
//             (row.supplier_mobile || '') +
//             '~' +
//             // (row.purchase_invoice || '') +
//             '~~~~' +
//             '\n';
        
//         batchData += 'E~' + (row.purchase_invoice || '') + '~~~~~~~~~' + '\n';
//     });

//     batchData += 'T~' + batch_length + '~' + batch_amount;

//     return batchData;
// }





// new coding
function getBatchData(batch, fileName, doc) {
    var batchData = '';
    var supplierGroups = {};
    
    batch.forEach(function(row) {
        var supplier = row.supplier;
        
        if (supplier in supplierGroups) {
            supplierGroups[supplier].push(row);
        } else {
            supplierGroups[supplier] = [row];
        }
    });
    

    var batch_length = Object.keys(supplierGroups).length; 

    var batch_amount = batch.reduce(function(sum, row) {
        return sum + (parseFloat(row.allocated_amount) || 0);
    }, 0);
    
    
    batchData += 'H~DUMMY~~~~' + fileName + '~' + '\n' +
    'B~' + batch_length + '~' + batch_amount + '~' + '20130625_HAS03' + '~' +
    (frappe.datetime.str_to_user(doc.due_date).replace(/-/g, '/') || '') +
    '~NETPAY' + '\n';

    for (var supplier in supplierGroups) {
        var supplierRows = supplierGroups[supplier];

        var totalAllocatedAmount = supplierRows.reduce(function(sum, row) {
            return sum + (parseFloat(row.allocated_amount) || 0);
        }, 0);

        batchData += 'D~~' +
            'NEFT~' +
            totalAllocatedAmount.toFixed(2) +
            '~' +
            (frappe.datetime.str_to_user(doc.due_date).replace(/-/g, '/') || '') +
            '~' +
            (frappe.datetime.str_to_user(doc.due_date).replace(/-/g, '/') || '') +
            '~~~~~~' +
            'M~~' +
            (supplierRows[0].supplier || '') +
            '~' +
            (supplierRows[0].supplier_bank || '') +
            '~' +
            (supplierRows[0].supplier_bank_ifsc_code || '') +
            '~' +
            (supplierRows[0].supplier_account_no || '') +
            '~~~' +
            (supplierRows[0].supplier_address_line_1 || '') +
            '~' +
            (supplierRows[0].supplier_address_line_2 || '') +
            '~~~~' +
            (supplierRows[0].supplier_city || '') +
            '~' +
            (supplierRows[0].supplier_zipcode || '') +
            '~' +
            (supplierRows[0].supplier_state || '') +
            '~' +
            (supplierRows[0].supplier_email || '') +
            '~' +
            (supplierRows[0].supplier_mobile || '') +
            '~' +
            // (supplierRows[0].purchase_invoice || '') +
            '~~~~' +
            '\n';

        supplierRows.forEach(function(row, index) {
            var purchaseInvoice = row.purchase_invoice || '';
            var allocatedAmount = parseFloat(row.allocated_amount) || 0;

            batchData += 'E~' + (index + 1) + '~' + purchaseInvoice + '~' + allocatedAmount.toFixed(2) + '~' + fileName +'~~~~~~' + '\n';
        });
    }

    batchData += 'T~' + batch_length + '~' + batch_amount;

    return batchData;
}




function getTotalAllocatedAmount(batch) {
    var totalAmount = 0;
    batch.forEach(function(row) {
        totalAmount += parseFloat(row.allocated_amount) || 0;
    });
    return totalAmount.toFixed(2);
}




frappe.ui.form.on('DFM Bank Payment Detail', {
    supplier: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        
        // Fetch the supplier_bank field
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Bank Account",
                filters: {
                    'is_company_account': 0,
					'company': child.company,
                    'party_type': "Supplier",
					'party': child.supplier,
                    'is_default': 1
                },
                fieldname: "name"
            },
            callback: function(response) {
                var name = response.message.name;
                
                // Update the supplier_bank field in the child table
                frappe.model.set_value(cdt, cdn, "supplier_bank", name);
            }
        });
    }
});
