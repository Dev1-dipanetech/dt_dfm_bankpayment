// Copyright (c) 2023, Dipane Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('DFM Bank Payment Settings', {
	refresh: function(frm) {
        frm.add_custom_button('Manual Sync From FTP', function() {
            frappe.call({
                method: 'dt_dfm_bankpayment.dt_dfm_bank_payment.doctype.dfm_bank_payment_settings.dfm_bank_payment_settings.cron',
                callback: function(response) {
                    
                }
            });
        });
    }
});
