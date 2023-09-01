frappe.listview_settings['DFM Bank Payment Log'] = {
    onload: function(listview) {
        // Triggers once before the list is loaded
        console.log("loaded", listview);
        
        
        $('.primary-action').hide();
    }
};