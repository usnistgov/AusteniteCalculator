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

function showErrorTab() {
    document.getElementById('error-tab').display='block';
    document.getElementById('error-tab-button').click();
}

function processFileContents() {

    const n_files = Object.keys(this.files).length; // number of files uploaded
    const file_obj = {}; // object to store files

    for(let i = 0; i < n_files; i++) {

        let file = this.files[i];
        let reader = new FileReader();

        if(this.id == 'xrdml-files' && !(/(xrdml$)|(csv$)/).test(this.files[i].name) ) {
            alert("This file type not accepted; please upload only .csv or .xrdml files.");
            return;
        }

        if(this.id == 'instprm-files' && !(/instprm$/).test(this.files[i].name) ) {
            alert("This file type not accepted; please upload an .instprm file.");
            return;
        }

        if(this.id == 'cif-file' && !(/cif$/).test(this.files[i].name) ) {
            alert("This file type not accepted; please upload only .cif files.");
            return;
        }

        if(this.id == 'cryst-illum-file' && !(/json$/).test(this.files[i].name) ) {
            alert("This file type not accepted; please upload a .json file.");
            return;
        }

        reader.readAsText(file);

        // once the file has loaded, save
        reader.onload = function(e) {
            file_obj[file.name] = reader.result;
        };

    }

    fileUploads[this.id] = file_obj; // global scope file container


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
    const sum_files = document.getElementById('sum_checkbox').checked

    // FIX - add button for sum files
    // currently returns 'on' even when the box is not checked...
    //const SumCheck = document.querySelector('input[name="sum_checkbox"]');

    console.log(radioValue.value);

    const response = await fetch('/submit', {
        method:'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            radioValue:radioValue.value,
            sumFiles:sum_files,
            fileUploads:fileUploads
        })
    });

    // json response from app.py 'submit()'
    // called the same variable 'all_results', but not defined that way
    all_results = await response.json();

    if(all_results.errors) {

        hideLoading();
        showErrorTab();

        const error_log = all_results.error_dict;
        const error_keys = Object.keys(error_log);
        const error_vals = Object.values(error_log);

        const the_ul = document.getElementById("error-list");
        let newLi = null;

        for(let i = 0; i < error_keys.length; i++) {

            // if no errors, continue along
            if(!error_vals[i]) {
                continue
            }

            newLi = document.createElement("li");
            newLi.textContent = error_keys[i] + ': ' + error_vals[i]

            // Append the <li> element to the <ul> element
            the_ul.appendChild(newLi);


        }


    } else {

      // update form selects for dataset number
      let intensity_plots_select = document.getElementById("intensity-plots-dataset-select");
      let normalized_intensity_plot_select = document.getElementById("normalized-intensity-plots-select");
      let phase_fraction_dataset_plot_select = document.getElementById("phase-fraction-plots-dataset-select");
      let cryst_illum_data_select = document.getElementById("cryst-illum-select-dataset");

      const n_dsets = all_results.n_datasets;
      let dset_select_arr = [intensity_plots_select, normalized_intensity_plot_select,phase_fraction_dataset_plot_select, cryst_illum_data_select];

        for(let i = 0; i < n_dsets; i++) {

            for(let j = 0; j < dset_select_arr.length; j++) {

                let new_option = document.createElement("option");
                new_option.value = i + 1;
                //new_option.textContent = (i + 1).toString();
                new_option.textContent = all_results.dataset_names[i].toString();
                dset_select_arr[j].appendChild(new_option);
          }

        }

        // ***** About Tab
        // version summary table
        const version_table_html = all_results.version_html;
        document.getElementById('version-table').innerHTML=version_table_html;

        // ***** Intensity Plots Tab Initialization
        // Choose dataset
        //let dsetName_IntPlotTab = 'Dataset_'.concat(intensity_plots_select.selectedIndex+1)
        let dsetName_IntPlotTab = all_results.dataset_names[intensity_plots_select.selectedIndex].toString()

        // Create plots
        createRawIntensityPlot(all_results,'raw-intensity-plot',dsetName_IntPlotTab);
        createFittedIntensityPlot(all_results,'fitted-intensity-plot',dsetName_IntPlotTab);
        // Create User Flags table
        create_flags_table(all_results,'user-flags-table',dsetName_IntPlotTab);


        // ***** Normalized Intensity Tab Initialization
        // CHECK - do we want one for each type of fitting, or combined?
        //let dsetName_NormIntTab = 'Dataset_'.concat(normalized_intensity_plot_select.selectedIndex+1)
        let dsetName_NormIntTab = all_results.dataset_names[normalized_intensity_plot_select.selectedIndex].toString();
        createNormalizedIntensityPlot(all_results,'normalized-intensities-plot',dsetName_NormIntTab);

        create_Theo_Int_table(all_results,'normalized-intensities-plot',dsetName_NormIntTab)
        create_Fit_n_int_table(all_results,'normalized-intensities-plot',dsetName_NormIntTab)

        // ***** Phase Fraction Tab Initialization
        //let dsetName_PhaseFracTab = 'Dataset_'.concat(phase_fraction_dataset_plot_select.selectedIndex+1)
        let dsetName_PhaseFracTab = all_results.dataset_names[phase_fraction_dataset_plot_select.selectedIndex].toString();

        createPhaseFractionPlot(all_results,'phase-fraction-plot','number',dsetName_PhaseFracTab);
        create_phase_fraction_value_table(all_results,'pf-table','number',dsetName_PhaseFracTab);
        create_uncert_source_summary_table(all_results,'uncert-table',dsetName_PhaseFracTab);
        create_uncert_source_peak_table(all_results,'uncert-table',dsetName_PhaseFracTab);

        // *****  Crystallites Illuminated Tab Initialization
        // createCrystIllumTable()

        // Crystallites Illuminated Tab
        // Select by dataset
        //let dsetName_CrysIllTab = 'Dataset_'.concat(cryst_illum_data_select.selectedIndex+1);
        let dsetName_CrysIllTab = all_results.dataset_names[cryst_illum_data_select.selectedIndex].toString();

        create_interaction_volume_table(all_results,'interaction-volume-table',dsetName_CrysIllTab);


        // update form selects for phase
        //let cryst_illum_phase_select = document.getElementById('cryst-illum-select-phase');
        let cryst_illum_peak_select = document.getElementById('cryst-illum-select-peak-index');

        //i<all_results[dsetName_CrysIllTab]['Interaction_Volume_html']["Peak Index"].length
        for(let i = 0; i < all_results[dsetName_CrysIllTab]["Peak_index_list"].length; i++){

            let peak_option = document.createElement("option");
            //new_option.textContent = (i + 1).toString();
            //["Peak Index"][i]
            peak_option.textContent = all_results[dsetName_CrysIllTab]["Peak_index_list"][i].toString();
            cryst_illum_peak_select.appendChild(peak_option);

        }

        createIncidentAnglePlot(all_results,'incident-angle-plot',dsetName_CrysIllTab,0);
        createZDepthPlot(all_results,'z-depth-histogram-plot',dsetName_CrysIllTab,0);

        // update form selects for peak

        //let n_peaks = all_results.n_peaks;

    // FIX - when we get crystallites illuinated
        // for(let i = 0; i < n_peaks; i++) {
        //     if(all_results.Dataset_1.Phase[i] == cryst_illum_phase_select.options[cryst_illum_phase_select.options.selectedIndex].innerText) {
        //         let new_option = document.createElement("option");
        //         new_option.textContent = (i + 1).toString();
        //         cryst_illum_peak_select.appendChild(new_option);
        //     }

        // }

        // tables
        // ??? Why call these 'table' if they are html?  Confusing with app.py





        // results table
        //const results_table_html = all_results.results_table_html;
        //document.getElementById('results-table').innerHTML=results_table_html;

        // uncertainties table
        //const uncert_table_html = all_results.param_table_html;
        //document.getElementById('uncert-table').innerHTML=uncert_table_html;

        // pf table
        //const pf_table_html = all_results.pf_table_html;
        //document.getElementById('pf-table').innerHTML=pf_table_html;

        changeTab();
        hideLoading();
    }

}
