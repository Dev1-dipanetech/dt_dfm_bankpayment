// Copyright (c) 2023, Dipane Technologies Pvt Ltd and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["DFM Bank Payment Status Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_default("company")
		},
		{
			"fieldname":"posting_date",
			"label": __("Posting Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "dfm_bank_payment_log",
			"label": __("DFM Bank Payment Log"),
			"fieldtype": "Link",
			"options": "DFM Bank Payment Log",
			"width": 150,
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150,
		},
		{
			"fieldname": "purchase_invoice",
			"label": __("Purchase Invoice"),
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 150
		},
		{
			"fieldname": "payment_entry",
			"label": __("Payment Entry"),
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 150
		},
		{
			"fieldname": "payable_account",
			"label": __("Payable Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 150,
			"get_query": function() {
                return {
                    "filters": [
                        ["company", "=", frappe.query_report.get_filter_value('company')],
						["account_type", "=", "Payable"],
						["is_group", "=", 0]
                    ]
                };
            }
		},
		{
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nIn Process at Bank\nTransferred by Bank\nRejected by Bank",
            "width": 150
        }
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);


		if (column.fieldname == "status" && data && data.status  === "In Process at Bank") {
			value = "<span style='color:orange; font-weight:bold'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status  === "Transferred by Bank") {
			value = "<span style='color:green; font-weight:bold'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status  === "Rejected by Bank") {
			value = "<span style='color:red; font-weight:bold'>" + value + "</span>";
		}

	
		return value;
	}
	
};
