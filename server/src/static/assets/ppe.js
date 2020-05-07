// function will loop through all checkboxes for boroughs, service_types and pcns to create url string
function update_filter() {
    let counter = 0, // counter for checked checkboxes
        i = 0,       // loop variable
        url = '',    // final url string
        boroughCheckboxes = document.getElementsByName('borough'),
        boroughCheckedBoxes = {},
        boroughs = [],
        serviceTypeCheckboxes = document.getElementsByName('service_type'),
        serviceTypeCheckedBoxes = {},
        serviceTypes = [],
        pcnCheckboxes = document.getElementsByName('pcn'),
        pcnCheckedBoxes = {},
        pcns = [];
    console.log(boroughCheckboxes)
    console.log(serviceTypeCheckboxes)
    console.log(pcnCheckboxes)

    // loop through all collected objects and gather the checked boxes
    for (i = 0; i < boroughCheckboxes.length; i++) {
        if (boroughCheckboxes[i].checked) {
            counter++;
            boroughCheckedBoxes[boroughCheckboxes[i].value] = 1; // update later w/ real qty
            boroughs.push(encodeURIComponent(boroughCheckboxes[i].value))
        }
    }
    console.log(boroughs)

    for (i = 0; i < serviceTypeCheckboxes.length; i++) {
        if (serviceTypeCheckboxes[i].checked) {
            counter++;
            serviceTypeCheckedBoxes[serviceTypeCheckboxes[i].value] = 1; // update later w/ real qty
            serviceTypes.push(encodeURIComponent(serviceTypeCheckboxes[i].value))
        }
    }
    console.log(serviceTypes)

    for (i = 0; i < pcnCheckboxes.length; i++) {
        if (pcnCheckboxes[i].checked) {
            counter++;
            pcnCheckedBoxes[pcnCheckboxes[i].value] = 1; // update later w/ real qty
            pcns.push(encodeURIComponent(pcnCheckboxes[i].value))
        }
    }
    console.log(pcns)

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

    if ((boroughs.length > 0) || (serviceTypes.length > 0) || (pcns.length > 0)) {
        url = 'sites?' + url
    } else {
        url = 'sites'
    }



    location.href = url


    // url = url.replace(/\|$/, ''); // remove trailing |

// display url string or message if there is no checked checkboxes
    if (counter > 100) {
        alert(url)
        location.href = url
        console.log(url)
    }
}

