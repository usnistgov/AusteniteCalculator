let conversion_select = document.getElementById("conversion-select");

// below this needs to be changed
conversion_select.addEventListener("change", function() {
    console.log("event triggered");

    let cs = document.getElementById('conversion-select');
    let conversion_option = cs.options[cs.options.selectedIndex].innerText;

    switch(conversion_option) {
        case "Number of Unit Cells":
            conversion_option = 'number';
            break;
        
        case "Mass Fraction":
            conversion_option = 'mass';
            break;

        case "Volume Fraction":
            conversion_option = 'volume';
            break;
    }

    createPhaseFractionPlot(all_results,'phase-fraction-plot',conversion_option);
    
})

let intensity_plots_select = document.getElementById("intensity-plots-select");

intensity_plots_select.addEventListener("change", function() {

    let raw_intensity_plot_img = document.getElementById("raw-intensity-plot-img");
    let fitted_intensity_plot_img = document.getElementById("fitted-intensity-plot-img");

    // plot the dataset based on which is selcted in this.selectedIndex

    // raw_intensity_plot_img.src = results_storage.raw_intensity_plot[this.selectedIndex + 1];
    // fitted_intensity_plot_img.src = results_storage.fitted_intensity_plot[this.selectedIndex + 1];
})

let normalized_intensities_plot_select = document.getElementById("normalized-intensity-plots-select");

normalized_intensities_plot_select.addEventListener("change",function() {

    let normalized_intensities_plot_img = document.getElementById("normalized-intensity-plot-img");
    console.log(this.selectedIndex);

    // same as above


})


 // update form selects for peak
 let cryst_illum_phase_select = document.getElementById('cryst-illum-select-phase');
 
 cryst_illum_phase_select.addEventListener("change", function() {

    let cryst_illum_peak_select = document.getElementById('cryst-illum-select-peak');

    for (p in cryst_illum_peak_select) { 
        cryst_illum_peak_select.options.remove(0); 
    }

    let n_peaks = all_results.results_table.Phase.length;

    for(let i = 0; i < n_peaks; i++) {
        if(all_results.results_table.Phase[i] == cryst_illum_phase_select.options[cryst_illum_phase_select.options.selectedIndex].innerText) {
            let new_option = document.createElement("option");
            new_option.textContent = (i).toString();
            new_option.value = i;
            cryst_illum_peak_select.appendChild(new_option);
        }

    }

 })
 
// add in cryst illum table
// note, this currently looks only in Dataset 1, since cryst_illum_res does not seem to have a dataset attribute
function createCrystIllumTable() {

    let div = document.getElementById("cryst-illum-table-div");
    div.innerHTML = '';

    let selected_dset = document.getElementById('cryst-illum-select-dataset');
    let selected_phase = document.getElementById('cryst-illum-select-phase');
    let selected_peak = document.getElementById('cryst-illum-select-peak');

    selected_phase = selected_phase.options[selected_phase.options.selectedIndex].innerText;
    selected_peak = selected_peak.options.selectedIndex; // only need the index

    let cryst_array = all_results.cryst_ill_res[selected_phase][selected_peak];

    let table_data = {
        'Number of Layers':cryst_array[0],
        'Number Illuminated':cryst_array[1],
        'Diffracting Fraction':cryst_array[2],
        'Number Diffracting':cryst_array[3],
        'Centroid of Z Depth':''
    };

    let tbl = document.createElement('table');
    let thead = document.createElement('thead');
    let hrow = document.createElement('tr');

    for(let i = 0; i < 5; i++) {

        let cell = document.createElement("th");
        let cellText = document.createTextNode(Object.keys(table_data)[i]);
        cell.appendChild(cellText);
        hrow.appendChild(cell);

    }

    thead.appendChild(hrow);
    tbl.appendChild(thead);

    let tblBody = document.createElement("tbody");
    let row = document.createElement("tr");
    
    for(let i = 0; i < 5; i++) {

        let cell = document.createElement("td");
        let cellText = document.createTextNode(table_data[Object.keys(table_data)[i]]);
        cell.appendChild(cellText);
        row.appendChild(cell);

    }

    tblBody.appendChild(row);
    tbl.appendChild(tblBody);
    tbl.classList.add("table");

    div.appendChild(tbl);


}

document.getElementById('cryst-illum-select-dataset').addEventListener("change",createCrystIllumTable);
document.getElementById('cryst-illum-select-phase').addEventListener("change",createCrystIllumTable);
document.getElementById('cryst-illum-select-peak').addEventListener("change",createCrystIllumTable);