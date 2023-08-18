// Copyright (c) 2023, Dipane Technologies Pvt Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on('DFM Bank Payment', {
    get_outstanding_invoices: function(frm) {

			

        frappe.call({
            method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.get_outstanding_invoices',
            args: {
                supplier: cur_frm.doc.supplier || '',
                date: cur_frm.doc.date
            },
            callback: function(response) {
                var invoices = response.message;

                // Clear existing child table rows
                frm.clear_table('dfm_bank_payment_detail');

                // Populate child table with fetched invoices
                $.each(invoices, function(i, invoice) {
                    var row = frappe.model.add_child(cur_frm.doc, 'DFM Bank Payment Detail', 'dfm_bank_payment_detail');
                    row.purchase_invoice = invoice.name;
                    row.supplier = invoice.supplier;
					row.due_date = invoice.due_date;
                    row.invoiced_amount = invoice.grand_total;
                    row.outstanding_amount = invoice.outstanding_amount;
					row.allocated_amount = invoice.outstanding_amount;
					row.supplier_address = invoice.supplier_address;
                });

                // Refresh child table and main form
                cur_frm.refresh_field('dfm_bank_payment_detail');
                cur_frm.refresh();
            }
        });
    },


	// before_submit: function(frm) {
    //     var batches = splitIntoBatches(frm.doc.dfm_bank_payment_detail, 3000000); // Split into batches of 30 lacs

    //     var successCount = 0;
    //     var errorCount = 0;

    //     batches.forEach(function(batch, index) {
    //         var fileData = getBatchData(batch);
    //         var batchFileName = frm.doc.name + '_batch_' + (index + 1) + '.txt';

    //         // Download the text file
    //         var blob = new Blob([fileData], { type: 'text/plain' });
    //         var url = URL.createObjectURL(blob);
    //         var link = document.createElement('a');
    //         link.href = url;
    //         link.download = batchFileName;
    //         link.style.display = 'none';
    //         document.body.appendChild(link);
    //         link.click();
    //         document.body.removeChild(link);

    //         setTimeout(function() {
    //             frappe.call({
    //                 method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.generate_text',
    //                 args: {
    //                     file_name: batchFileName
    //                 },
    //                 callback: function(response) {
    //                     if (response.message) {
    //                         successCount++;
	// 						console.log(batch)


	// 						setTimeout(function() {
	// 							// Create a new document in DFM Bank Payment Log
	// 							frappe.call({
	// 								method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.create_log_document',
	// 								args: {
	// 									dfm_bank_payment: frm.doc.name,
	// 									transfer_file_name: batchFileName,
	// 									batch_details: batch
	// 								},
	// 								callback: function(log_response) {
	// 									if (log_response.message) {
	// 										// Log document created successfully
	// 										frappe.msgprint("Log document created successfully");
	// 									} else {
	// 										// Error creating log document
	// 										frappe.msgprint("Error creating log document");
	// 									}

	// 								}
	// 							});
	// 						}, 2000);


    //                     } else {
    //                         errorCount++;
    //                     }


	// 					// Check if all batches are processed
	// 					if (successCount + errorCount === batches.length) {
	// 						if (errorCount === 0) {
	// 							frappe.msgprint("All batch files are sent to the FTP Server");
	// 						} else {
	// 							frappe.msgprint(`Sent ${successCount} batch files to the FTP Server. ${errorCount} batch files failed.`);
	// 						}
	// 					}
    //                 }
    //             });
    //         }, 3000);
    //     });
    // }






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
						file_name: batchFileName
					},
					callback: function(response) {
						if (response.message) {
							frappe.call({
								method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.create_log_document',
								args: {
									dfm_bank_payment: frm.doc.name,
									transfer_file_name: batchFileName,
									batch_details: batch
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




function splitIntoBatches(data, batchSize) {
    var batches = [];
    var currentBatch = [];
    var currentBatchAmount = 0;

    data.sort(function(a, b) {
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





function getBatchData(batch, fileName, doc) {

    var batchData = '';
    var batch_amount = getTotalAllocatedAmount(batch);
    var batch_length = batch.length;

    batchData += 'H~DUMMY~~~~' + fileName + '~' + '\n' +
        'B~' + batch_length + '~' + batch_amount + '~' + '20130625_HAS03' + '~' +
        (frappe.datetime.str_to_user(doc.date).replace(/-/g, '/') || '') +
        '~NETPAY' + '\n';

    batch.forEach(function(row) {
        batchData += 'D~~' +
            'NEFT~' +
            (row.allocated_amount || '') +
            '~' +
            (frappe.datetime.str_to_user(doc.date).replace(/-/g, '/') || '') +
            '~' +
            (frappe.datetime.str_to_user(doc.date).replace(/-/g, '/') || '') +
            '~~~~~~' +
            'M~~' +
            (row.supplier || '') +
            '~' +
            (row.supplier_bank || '') +
            '~' +
            (row.supplier_bank_ifsc_code || '') +
            '~' +
            (row.supplier_account_no || '') +
            '~~~' +
            (row.supplier_address_1 || '') +
            '~' +
            (row.supplier_address_2 || '') +
            '~~~~' +
            (row.supplier_city || '') +
            '~' +
            (row.supplier_zipcode || '') +
            '~' +
            (row.supplier_state || '') +
            '~' +
            (row.supplier_email || '') +
            '~' +
            (row.supplier_mobile || '') +
            '~' +
            (row.purchase_invoice || '') +
            '~~~~' +
            '\n';
    });

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
