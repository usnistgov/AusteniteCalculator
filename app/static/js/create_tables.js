
// fragile to missing commas, hang on 'running submission'

// Why are we passing div_id, doesn't seem like we use it?

customColorScale = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd'
]

// Flags for users Table
//all_results[dataset_name]["flags_html"]
function create_flags_table(all_results,div_id,dataset_name) {
    const flags_table_html = all_results[dataset_name]["flags_html"];
    document.getElementById('user-flags-table').innerHTML=flags_table_html;
}

// Theoretical Intensities Table
//all_results[dataset_name]['Theo_n_int_html']
function create_Theo_Int_table(all_results,div_id,dataset_name) {
    const Theo_Int_Table_html = all_results[dataset_name]['Theo_n_int_html'];
    document.getElementById('Theo-Int-table').innerHTML=Theo_Int_Table_html;
}

// Fit normalized Intensities Table
//all_results[dataset_name]['Theo_n_int_html']
function create_Fit_n_int_table(all_results,div_id,dataset_name) {
    const Fit_n_int_Table_html = all_results[dataset_name]['Fit_n_int_html'];
    document.getElementById('Fit-n-int-table').innerHTML=Fit_n_int_Table_html;
}


// Phase Fraction Table
//all_results[dataset_name]["phase_fraction_mass_html"]
function create_phase_fraction_value_table(all_results,div_id,conversion_type,dataset_name) {
    //const phase_fraction_value = all_results[dataset_name]["phase_fraction_number_html"];
    
    switch(conversion_type) {
        case "number":
            phase_fraction_value_html = all_results[dataset_name]["phase_fraction_number_html"];
            break;
        
        case "mass":
            phase_fraction_value_html = all_results[dataset_name]["phase_fraction_mass_html"];
            break;

        case "volume":
            phase_fraction_value_html = all_results[dataset_name]["phase_fraction_volume_html"];
            break;
    }
    
    
    document.getElementById('pf-table').innerHTML=phase_fraction_value_html;
}

// Uncertainty Sources Summary
//all_results[dataset_name]["uncertainty_summary_html"]
function create_uncert_source_summary_table(all_results,div_id,dataset_name) {
    const uncert_source_summary_table_html = all_results[dataset_name]["uncertainty_summary_html"];
    document.getElementById('uncert-table').innerHTML=uncert_source_summary_table_html;
}


// Interaction Volume Table
// all_results[dataset_name]['Interaction_Volume_html']
function create_interaction_volume_table(all_results,div_id,dataset_name) {
    const interaction_volume_table_html = all_results[dataset_name]['Interaction_Volume_html'];
    document.getElementById('interaction-volume-table').innerHTML=interaction_volume_table_html;
}
