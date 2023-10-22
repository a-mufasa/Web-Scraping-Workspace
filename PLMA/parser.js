// Initialize CSV header
let csv = 'Title,Company ID,Location,Phone,Fax,Email,Website,Products,Contact Fullname,Contact Role\n';

// Calculate the number of pages to scrape
const totalPages = parseInt(document.querySelector('[class="pager-last last active"]').innerHTML.match(/(\d+)/)[0]) + 1;

// Loop through each page
for (let i = 0; i < totalPages; i++) {
    // Fetch HTML content of the current page
    fetch(`https://members.plma.com/trade-show-directory?page=${i}`)
    .then(data => data.text())
    .then(html => {
        // Parse HTML content
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Select all the table cells containing information
        const nodeList = doc.querySelectorAll('.view-content td');

        // Define classes for each field
        const fieldClasses = [
            "views-field views-field-title", 
            "views-field views-field-field-exhibitor-location",
            "views-field views-field-field-exhibitor-phone",
            "views-field views-field-field-exhibitor-fax",
            "views-field views-field-field-exhibitor-email",
            "views-field views-field-field-exhibitor-website",
            "views-field views-field-field-exhibitor-products",
            "views-field views-field-field-exhibitor-contact-fullname"
        ];

        // Loop through each table cell
        for (let j = 0; j < nodeList.length; j++) {
            const verifyList = fieldClasses.map(field => nodeList[j].getElementsByClassName(field));
            let row = '';

            // Loop through each field
            for (let k = 0; k < 8; k++) {
                if (!verifyList[k][0]){
                    // If the field is empty, add a comma
                    row += ",";
                }
                else {
                    // Extract text content, trim, and remove line breaks
                    let text = verifyList[k][0].getElementsByClassName('field-content')[0].innerText.trim().replace(/[\r\n]+/gm, "");

                    // Remove quotes from text
                    text = text.replaceAll(/["']/g, "");

                    if (k === 0 || k === 7) {
                        // Handle cases for the first and last fields (Title and Contact Fullname)
                        const last = text.split(",").slice(-1)[0];
                        row += `"${text.slice(0, text.length - last.length - 1)}"` + ',';
                        row += `"${last.trim()}"` + ',';
                    }
                    else {
                        // For other fields, add quotes around the text
                        row += `"${text}"` + ',';
                    }
                }
            }
            
            // Remove the trailing comma, add a newline character
            row = row.slice(0, -1)
            row += '\n';
            
            // Add the row to the CSV
            csv += row;
        }
    });
}

// Run this after the first part finishes executing (takes 5-10 seconds) 
jQuery(document).ready(function($) {
    // Add a download link for the CSV file
    $('head').append('<a download="trade_show.csv"></a>');
    // Set the href attribute of the link to a Blob containing the CSV data
    $('a[download="trade_show.csv"]').attr('href', window.URL.createObjectURL(new Blob([csv], { type: 'text/csv' })))
});
