// function will loop through all checkboxes for boroughs, service_types and pcns to create url string
function update_filter(baseUrl) {
    let counter = 0, // counter for checked checkboxes
        i = 0,       // loop variable
        url = '',    // final url string
        boroughCheckboxes = document.getElementsByName('borough'),
        boroughs = [],
        serviceTypeCheckboxes = document.getElementsByName('service_type'),
        serviceTypes = [],
        pcnCheckboxes = document.getElementsByName('pcn'),
        pcns = [];

    // loop through all collected objects and gather the checked boxes
    for (i = 0; i < boroughCheckboxes.length; i++) {
        if (boroughCheckboxes[i].checked) {
            counter++;
            boroughs.push(encodeURIComponent(boroughCheckboxes[i].value))
        }
    }

    for (i = 0; i < serviceTypeCheckboxes.length; i++) {
        if (serviceTypeCheckboxes[i].checked) {
            counter++;
            serviceTypes.push(encodeURIComponent(serviceTypeCheckboxes[i].value))
        }
    }

    for (i = 0; i < pcnCheckboxes.length; i++) {
        if (pcnCheckboxes[i].checked) {
            counter++;
            pcns.push(encodeURIComponent(pcnCheckboxes[i].value))
        }
    }

    url = ''
    if (boroughs.length > 0) {
        url += 'borough=[' + boroughs + ']'
    }
    if (serviceTypes.length > 0) {
        if (boroughs.length > 0) {
            url += '&'
        }
        url += 'service_type=[' + serviceTypes + ']'
    }

    if (pcns.length > 0) {
        if ((pcns.length > 0) || (serviceTypes.length > 0)) {
            url += '&'
        }
        url += 'pcn=[' + pcns + ']'
    }

    if (baseUrl.includes("sites"))
    {

        if (url != '')
        {
            url += '&';
        }

        if (typeof (date_range) != 'undefined') {
            url += 'date_range=' + date_range.value;
        }
    }

    if ((boroughs.length > 0)
        || (serviceTypes.length > 0)
        || (pcns.length > 0)
        || (baseUrl.includes("sites") && typeof (date_range) != 'undefined')){
        url = baseUrl + '?' + url
    } else {
        url = baseUrl
    }

    location.href = url
}

function date_range_onchange() {
    update_filter('/sites')
}


