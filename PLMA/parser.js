csv = 'Title,Company ID,Location,Phone,Fax,Email,Website,Products,Contact Fullname,Contact Role\n';

pages = parseInt(document.querySelector('[class="pager-last last active"]').innerHTML.match(/(\d+)/)[0]) + 1

for (let i = 0; i < pages; i++){
    fetch(`https://members.plma.com/trade-show-directory?page=${i}`)
    .then(data => data.text())
    .then(html => {
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, 'text/html');
        
        var nodeList = doc.querySelectorAll('.view-content td');

        var fieldClasses = [
            "views-field views-field-title", 
            "views-field views-field-field-exhibitor-location",
            "views-field views-field-field-exhibitor-phone",
            "views-field views-field-field-exhibitor-fax",
            "views-field views-field-field-exhibitor-email",
            "views-field views-field-field-exhibitor-website",
            "views-field views-field-field-exhibitor-products",
            "views-field views-field-field-exhibitor-contact-fullname"
        ]

        for (let j = 0; j < nodeList.length; j++) {
            var verifyList = fieldClasses.map(field => nodeList[j].getElementsByClassName(field));
            var row = '';

            for (let k = 0; k < 8; k++) {
                if (!verifyList[k][0]){
                    row += ",";
                }
                else{
                    var text = verifyList[k][0].getElementsByClassName('field-content')[0].innerText.trim().replace( /[\r\n]+/gm, "" );
                    
                    // delete the cases of " or ' since there are only 8 total
                    if (text.includes(`"`)) text = text.replaceAll(`"`, ""); 
                    if (text.includes(`'`)) text = text.replaceAll(`'`, ""); 

                    if (k === 0 || k === 7){
                        last = text.split(",").slice(-1)[0];
                        row += `"${text.slice(0,text.length-last.length-1)}"` + ',';
                        row += `"${last.trim()}"` + ',';
                    }
                    else row += `"${text}"` + ',';
                }
            }
            
            row = row.slice(0,-1)
            row += '\n';
            
            csv += row;
        }
    })
}

// Run this after the first part finishes executing (takes 5-10 seconds) 

jQuery(document).ready(function($){
    $('head').append('<a download="trade_show.csv"></a>')
    $('a[download="trade_show.csv"]').attr('href', window.URL.createObjectURL(new Blob([csv], {type: 'text/csv'})))
  });
