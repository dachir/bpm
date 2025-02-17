// Copyright (c) 2025, Kossivi and contributors
// For license information, please see license.txt

frappe.ui.form.on("BPM Payment Request", {
    setup: function (frm) {
        /*frm.set_query('category', function () {
            return {
                filters: {
                    description: ['not in', ['Santé et Frais Sanitaires', 'Rémunérations et Avantages', 'Transport et Véhicules', 'Marketing et Promotion', 'Motivation']]
                }
            };
        });*/
        frm.set_query('nature', function () {
            return {
                filters: {
                    categorie: frm.doc.category,
                    nature: ['not in', ['Motivation']]
                }
            };
        });
        frm.refresh_field("nature");
    },
    refresh: function(frm) {
        // Default form background (very light red)
        let default_bg = '#FFF5F5'; 

        // Background when expense_report is filled (very light yellow)
        let filled_bg = '#FFFEF0'; 

        // Default header background (soft red)
        let default_header_bg = '#FFECEC'; 

        // Header background when expense_report is filled (slightly thicker yellow)
        let filled_header_bg = '#FFF7E6'; 

        /*// Check if expense_report is filled
        if (frm.doc.expense_report) {
            $('.form-page').css('background-color', filled_bg); // Apply yellow background
            $('.page-head-content').css('background-color', filled_header_bg); // Thicker yellow header 
            $('.layout-side-section').css('background-color', filled_header_bg);
        } else {
            $('.form-page').css('background-color', default_bg); // Default red background
            $('.page-head-content').css('background-color', default_header_bg); // Soft red header
            $('.layout-side-section').css('background-color', default_header_bg);
            $('input, select, textarea, .form-control').css('background-color', '#FFFFFF'); // Ensure form controls remain white 
        }*/
        $('.form-page').css('background-color', default_bg); // Default red background
        $('.page-head-content').css('background-color', default_header_bg); // Soft red header
        $('.layout-side-section').css('background-color', default_header_bg);
        $('input, select, textarea, .form-control').css('background-color', '#FFFFFF'); // Ensure form controls remain white 

        // Adjust header title color for better contrast
        $('.page-title').css('color', '#990000'); 
    },
});

// Function to reset styles when leaving the form
function resetFormStyles() {
    $('.form-page').css('background-color', '');
    $('.page-head-content').css('background-color', '');
}

// Reset colors when navigating away using Frappe's routing system
frappe.router.on('change', function() {
    resetFormStyles();
});

// Reset colors when the page is reloaded or before leaving
$(window).on('beforeunload', function() {
    resetFormStyles();
});
