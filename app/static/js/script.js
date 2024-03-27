let submit_button = document.getElementById('submit');
submit_button.addEventListener('click', fetchData);
submit_button.addEventListener('click',showLoading);

const xrdmlFiles = document.getElementById('xrdml-files');
xrdmlFiles.addEventListener('input',processFileContents);

const instprmFile = document.getElementById('instprm-file');
instprmFile.addEventListener('input',processFileContents);

// save version to this storage object
const results_storage = {data:undefined};
const fileUploads = [];

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
        fileUploads.push({
            [the_id]: reader.result
        });
    })




}

async function fetchData() {

    // Gather data to submit
    //const xrdmlFile = processFileContents('xrdml-file');
    const radioValue = document.querySelector('input[name="default-file-radio"]:checked'); 

    console.log(radioValue.value);

    const response = await fetch('/submit', {
        method:'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            radioValue:radioValue.value//,
            //xrdml_file:xrdml_file
        })
    });

    const all_results = await response.json();

    // raw intensities plot
    const ri_plot = document.createElement('img');
    ri_plot.src = all_results.encoded_plots.raw_intensity_plot;
    document.getElementById('raw-intensity-plot').appendChild(ri_plot);

    // fitted intensities plot
    const fi_plot = document.createElement('img');
    fi_plot.src = all_results.encoded_plots.fitted_intensity_plot;
    document.getElementById('fitted-intensity-plot').appendChild(fi_plot);

    // normalized intensities plot
    const ni_plot = document.createElement('img');
    ni_plot.src = all_results.encoded_plots.normalized_intensities_plot;
    document.getElementById('normalized-intensities-plot').appendChild(ni_plot);

    // phase fraction plot
    const pf_plot = document.createElement('img');
    pf_plot.id = "pf-plot"
    pf_plot.src = all_results.encoded_plots.phase_fraction_plot;
    document.getElementById('phase-fraction-plot').appendChild(pf_plot);

    // save the phase fraction plots to display as needed
    results_storage.pf_plot_num_unit_cells = all_results.encoded_plots.phase_fraction_plot;
    results_storage.pf_plot_mass_frac = all_results.encoded_plots.phase_fraction_plot_mass_frac;
    results_storage.pf_plot_vol_frac = all_results.encoded_plots.phase_fraction_plot_vol_frac;

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

