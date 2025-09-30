
let instprm_download_btn = document.getElementById("button-instprm-json");

//instprm_download_btn.addEventListener('click',getInstprmJsonFile);

async function getCrystFile() {
    // gather info to send to server for request
    const response = await fetch('/cryst', {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            var: 'Gimme my cryst file'
        })
    });

    console.log(response);
}

async function getInstprmJsonFile() {
    // gather info to send to server for request
    const response = await fetch('/instprm_json', {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            var: 'Gimme my instprm and json files'
        })
    });

    console.log(response);
}

// the function below takes in an html table element ID and
// downloads the table as a .csv file. we may not need to use
// it depending on how we decide to download contents.
function tableToCSV(table_id,file_name) {
    // table id is a string of the html element

    let csv_data = [];

    // loop through each row 
    let rows = document.getElementById(table_id).rows;
    for (let i = 0; i < rows.length; i++) {

        let cols = rows[i].querySelectorAll('td,th');

        let csvrow = [];
        for (let j = 0; j < cols.length; j++) {
            csvrow.push(cols[j].innerHTML);
        }

        // join the array cvrow with commas,
        // and add this to the csv_data array
        csv_data.push(csvrow.join(","));
    }

    // join rows together with newline
    csv_data = csv_data.join('\n');

    downloadCSVFile(csv_data,file_name);

}

function downloadCSVFile(csv_data,file_name) {
    // this function is called from tableToCSV() above
    // file_name argument should have format like "data.csv"

    CSVFile = new Blob([csv_data], {
        type: "text/csv"
    });

    // create to temporary link 
    let temp_link = document.createElement('a');

    // Download csv file
    temp_link.download = file_name;
    let url = window.URL.createObjectURL(CSVFile);
    temp_link.href = url;
    temp_link.style.display = "none"; // hide link
    document.body.appendChild(temp_link);

    temp_link.click(); // trigger the download

    document.body.removeChild(temp_link); // remove the link
}


document.getElementById('button-download-json').addEventListener('click', () => {
    // Collect values from inputs
    // ADD cif file name to the form
    const get = id => document.getElementById(id).value.trim();

    const data = {
        austenite_values: get('json-austenite'),
        ferrite_values:   get('json-ferrite'),
        beam_shape:       get('json-beam-shape'),
        beam_size:        Number(get('json-beam-size')),
        raster_x:         Number(get('json-raster-x')),
        raster_y:         Number(get('json-raster-y')),
        sample_displacement: Number(get('json-sample-displacement')),
        L:                Number(get('json-l')),
        W_F:               Number(get('json-wf')),
        H_F:               Number(get('json-hf')),
        H_R:               Number(get('json-hr'))
    };

    data.austenite_values = get('json-austenite').split(',').map(s => s.trim()).map(Number);
    data.ferrite_values   = get('json-ferrite').split(',').map(s => s.trim()).map(Number);

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'params.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
});
