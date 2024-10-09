let submit_button = document.getElementById('submit');
submit_button.addEventListener('click', fetchData);
submit_button.addEventListener('click',showLoading);

// save version to this storage object
let all_results = Object();
const fileUploads = Object();

function changeTab() {
    document.getElementById('intensity-plots-tab-button').click();
}

function showLoading() {
    document.getElementById('loading-indicator').style.display='block';
    document.getElementById('submit').disabled=true;
}

function hideLoading() {
    document.getElementById('loading-indicator').style.display='none';
    document.getElementById('submit').disabled=false;
}

function processFileContents() {
    const file = this.files[0];
    const the_id = this.id;

    let reader = new FileReader();
    reader.readAsText(file);

    reader.addEventListener('load',() => {
        fileUploads[the_id] = reader.result;
    })
}

const xrdmlFiles = document.getElementById('xrdml-files');
xrdmlFiles.addEventListener('input',processFileContents);

const instprmFile = document.getElementById('instprm-file');
instprmFile.addEventListener('input',processFileContents);

const cifFile = document.getElementById('cif-file');
cifFile.addEventListener('input',processFileContents);

const crystIllumFile = document.getElementById('cryst-illum-file');
crystIllumFile.addEventListener('input',processFileContents);


// main function
async function fetchData() {

    // Gather data to submit
    const radioValue = document.querySelector('input[name="default-file-radio"]:checked'); 

    console.log(radioValue.value);

    const response = await fetch('/submit', {
        method:'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            radioValue:radioValue.value,
            fileUploads:fileUploads
        })
    });

    all_results = await response.json();

    // update form selects for dataset number
    let intensity_plots_select = document.getElementById("intensity-plots-select");
    let normalized_intensity_plot_select = document.getElementById("normalized-intensity-plots-select");
    let cryst_illum_data_select = document.getElementById("cryst-illum-select-dataset");

    const n_dsets = all_results.n_dsets;
    let dset_select_arr = [intensity_plots_select, normalized_intensity_plot_select, cryst_illum_data_select];

    for(let i = 0; i < n_dsets; i++) {

        for(let j = 0; j < dset_select_arr.length; j++) {
            
            let new_option = document.createElement("option");
            new_option.value = i + 1;
            new_option.textContent = (i + 1).toString();
            dset_select_arr[j].appendChild(new_option);

        }

    }

    // update form selects for phase
    let cryst_illum_phase_select = document.getElementById('cryst-illum-select-phase');
    const n_phases = all_results.unique_phases.length;
    
    for(let i = 0; i < n_phases; i++) {
        let new_option = document.createElement("option");
        new_option.textContent = all_results.unique_phases[i];
        cryst_illum_phase_select.appendChild(new_option);
    }

    // update form selects for peak
    let cryst_illum_peak_select = document.getElementById('cryst-illum-select-peak');
    let n_peaks = all_results.results_table.Phase.length;

    for(let i = 0; i < n_peaks; i++) {
        if(all_results.results_table.Phase[i] == cryst_illum_phase_select.options[cryst_illum_phase_select.options.selectedIndex].innerText) {
            let new_option = document.createElement("option");
            new_option.textContent = (i + 1).toString();
            cryst_illum_peak_select.appendChild(new_option);
        }

    }

    // intensities plots
    let dsetName = 'Dataset_'.concat(intensity_plots_select.selectedIndex+1)
    createRawIntensityPlot(all_results,'raw-intensity-plot',dsetName);
    createFittedIntensityPlot(all_results,'fitted-intensity-plot',dsetName);
    createNormalizedIntensityPlot(all_results,'normalized-intensities-plot',intensity_plots_select.selectedIndex+1);
    createPhaseFractionPlot(all_results,'phase-fraction-plot','number');

    // cryst illum table
    createCrystIllumTable()

    // tables
    // ??? Why call these 'table' if they are html?  Confusing with app.py

    // version summary table
    const version_table_html = all_results.version_html;
    document.getElementById('version-table').innerHTML=version_table_html;


    // User Flags table
    // const user_flags_html = all_results.user_flags_html;
    // document.getElementById('user-flags-table').innerHTML=user_flags_html;

    // results table
    const results_table_html = all_results.results_table_html;
    document.getElementById('results-table').innerHTML=results_table_html;

    // uncertainties table
    const uncert_table_html = all_results.param_table_html;
    document.getElementById('uncert-table').innerHTML=uncert_table_html;

    // pf table
    const pf_table_html = all_results.pf_table_html;
    document.getElementById('pf-table').innerHTML=pf_table_html;

    changeTab();
    hideLoading();
    
}

