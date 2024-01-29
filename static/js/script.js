let submit_button = document.getElementById('submit');
submit_button.addEventListener('click', fetchData);
submit_button.addEventListener('click',showLoading);

// save version to this storage object
const results_storage = {data:undefined};

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

async function fetchData() {

    const radio_value = document.querySelector('input[name="default-file-radio"]:checked'); 

    console.log(radio_value.value);

    const response = await fetch('/submit', {
                                    method:'POST',
                                    body:{
                                        radio_value:radio_value.value
                                    }
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
    pf_plot.src = all_results.encoded_plots.phase_fraction_plot;
    document.getElementById('phase-fraction-plot').appendChild(pf_plot);

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

