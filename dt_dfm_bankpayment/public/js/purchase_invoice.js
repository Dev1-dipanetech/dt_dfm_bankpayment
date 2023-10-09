
frappe.ui.form.on('Purchase Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus != 0) {
            frm.add_custom_button('De-Link DFM Bank Payment', function() {
                frappe.call({
                    method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.get_linked_payments',
                    args: {
                        purchase_invoice: frm.doc.name
                    },
                    callback: function(response) {
                        if (response.message) {
                            var child_table_html = `
                                <table class="table table-bordered">
                                    <thead>
                                        <tr>
                                            <th>DFM Bank Payment</th>
                                            <th>Purchase Invoice</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                            `;

                            for (let payment of response.message) {
                                child_table_html += `
                                    <tr>
                                        <td><a href="${frappe.urllib.get_full_url(`/app/dfm-bank-payment/${payment.parent}`)}">${payment.parent}</a></td>
                                        <td>${payment.purchase_invoice}</td>
                                    </tr>
                                `;
                            }

                            child_table_html += `
                                    </tbody>
                                </table>
                            `;

                            var dialog = new frappe.ui.Dialog({
                                title: 'Linked DFM Bank Payment',
                                fields: [
                                    {
                                        fieldtype: 'HTML',
                                        fieldname: 'child_table_html',
                                        options: child_table_html,
                                        read_only: true
                                    }
                                ],
                                primary_action_label: 'De-Link',

                                primary_action: function() {
                                    for (let payment of response.message) {
                                        frappe.call({
                                            method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment.dfm_bank_payment.delete_linked_rows',
                                            args: {
                                                purchase_invoice: payment.purchase_invoice,
                                                parent: payment.parent
                                            },
                                            callback: function(response) {
                                                if (response.message) {
                                                    frappe.msgprint(`Linked rows deleted for parent: ${payment.parent}`);
                                                    // Refresh the form or update UI if needed
                                                } else {
                                                    frappe.msgprint(`No linked rows found for parent: ${payment.parent}`);
                                                }
                                            }
                                        });
                                    }
                                }
                                
                            });
                            dialog.show();
                        }
                    }
                });
            });
        }
    }
});


