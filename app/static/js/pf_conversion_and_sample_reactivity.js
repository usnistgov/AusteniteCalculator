/*  **************************
 Intensity Plots Tab - Form Selection for Dataset
 Events also called in script.js
****************************  */
let intensity_plots_select = document.getElementById("intensity-plots-dataset-select");

intensity_plots_select.addEventListener("change", function() {

    // This function plots the dataset based on which is selcted in this.selectedIndex
    // This uses the same pattern as script.js
    let dsetName = 'Dataset_'.concat(this.selectedIndex+1)

    createFittedIntensityPlot(all_results,'fitted-intensity-plot',dsetName);
    createRawIntensityPlot(all_results,'raw-intensity-plot',dsetName);
})

/*  **************************
 Normalized Intensity Tab - Form Selection for Dataset
 Events also called in script.js to set inital values
****************************  */

// Normalized Itensities Plot
let normalized_intensities_plot_select = document.getElementById("normalized-intensity-plots-select");

normalized_intensities_plot_select.addEventListener("change", function() {

    // This function plots the dataset based on which is selcted in this.selectedIndex
    // This uses the same pattern as script.js

    createNormalizedIntensityPlot(all_results,'normalized-intensities-plot',this.selectedIndex+1);
    
    // Theoretical Intensities Table
    //all_results[dataset_name]['Theo_n_int_html']
    create_Theo_Int_Table(all_results,'normalized-intensities-plot',this.selectedIndex+1);
    
    // Fit values Table
    // all_results[dataset_name]['Fit_n_int_html']
    create_Theo_Int_table(all_results,'normalized-intensities-plot',this.selectedIndex+1);

    // Uncertainty metrics Table
    // all_results[dataset_name]['Uncertainties_n_int_html']
    
})




/*  **************************
 Phase Fraction Tab - Form Selection for Conversion Type
 Events also called in script.js
****************************  */
let phase_fraction_plots_dataset_select = document.getElementById("phase-fraction-plots-dataset-select");
let conversion_select = document.getElementById("conversion-select");


// below this needs to be changed
phase_fraction_plots_dataset_select.addEventListener("change", function() {
    dataset_name=this.selectedIndex+1
    
    //    let dsetName = 'Dataset_'.concat(this.selectedIndex+1)
    
    createPhaseFractionPlot(all_results,'phase-fraction-plot',conversion_option,dataset_name);
    create_uncert_source_summary_table(all_results,'uncert-table',dataset_name);
})

conversion_select.addEventListener("change", function() {
    console.log("event triggered");

    let cs = document.getElementById('conversion-select');
    let conversion_option = cs.options[cs.options.selectedIndex].innerText;
    
    let dataset_name = 'Dataset_'.concat(phase_fraction_plots_dataset_select.selectedIndex+1)
    
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
    createPhaseFractionPlot(all_results,'phase-fraction-plot',conversion_option,dataset_name);
    create_phase_fraction_value_table(all_results,'pf-table',conversion_option,dataset_name);
})




 // update form selects for peak
 let cryst_illum_phase_select = document.getElementById('cryst-illum-select-phase');
 
 cryst_illum_phase_select.addEventListener("change", function() {

    let cryst_illum_peak_select = document.getElementById('cryst-illum-select-peak');

    // currently just updates the table, need to add similar structure from above to update plots

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
