
// fragile to missing commas, hang on 'running submission'


customColorScale = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd'
]

// Theoretical Intensities Table
//all_results[dataset_name]['Theo_n_int_html']


function create_Theo_Int_Table(all_results,div_id,dataset_name) {
    const Theo_Int_Table_html = all_results[dataset_name]['Theo_n_int_html'];
    document.getElementById('Theo-Int-table').innerHTML=Theo_Int_Table_html;


}
