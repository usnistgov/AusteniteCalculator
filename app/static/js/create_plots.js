
// fragile to missing commas, hang on 'running submission'


customColorScale = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd'
]

/**
 * Return the Raw Intenisty Plot as a plotly object
 *
 * @param [dict] all_results : dictionary with data
 * @param [str] div_id : ID for division index.html
 * @param [num] dataset_name : variable for the dataset number
 *
 * @returns {Plotly.newPlot()} Types and descriptions are both supported.
 */
function createRawIntensityPlot(all_results,div_id,dataset_name) {

    var trace1 = {
        x: all_results[dataset_name].two_thetas,
        y: all_results[dataset_name].raw_intensity_data,
        type: 'scatter',
        mode: 'markers',
        name: 'Data',
        marker: {
            color: 'rgb(0, 0, 0)',
                }
    };
      
    var data = [trace1];

    var layout = {
        title: 'Raw Intensities',
        xaxis: {title: 'Two Theta'},
        yaxis: {title: 'Intensity'}
      };
    
    Plotly.newPlot(div_id, data, layout);

}

/**
 * Return the Raw Intenisty and Fitted Data Plot as a plotly object
 *
 * @param [dict] all_results : dictionary with data
 * @param [str] div_id : ID for division index.html
 * @param [num] dataset_name : variable for the dataset number
 *
 * @returns {Plotly.newPlot()} Types and descriptions are both supported.
 */
function createFittedIntensityPlot(all_results,div_id,dataset_name) {
    // Raw data
    var trace1 = {
        x: all_results[dataset_name].two_thetas,
        y: all_results[dataset_name].raw_intensity_data,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Data',
        marker: {
            color: 'rgb(0, 0, 0)',
                }
    };
    // Le Bail fit
    var trace2 = {
        x: all_results[dataset_name].two_thetas,
        y: all_results[dataset_name].Le_Bail_fit,
        type: 'scatter',
        name: 'Le Bail Fit',
        color: customColorScale[0]
    };

    // Peak fit
    var trace3 = {
        x: all_results[dataset_name].two_thetas,
        y: all_results[dataset_name].Peak_fit,
        type: 'scatter',
        name: 'Peak Fit',
        color: customColorScale[1]
    };
      
    var data = [trace1,trace2,trace3];

    var layout = {
        title: 'Fitted Intensities',
        xaxis: {title: 'Two Theta'},
        yaxis: {title: 'Intensity'}
    };
    
    Plotly.newPlot(div_id, data, layout);

}

/**
 * Return the Normalized Intensity Plot as a plotly object
 *
 * @param [dict] all_results : dictionary with data
 * @param [str] div_id : ID for which division?
 * @param [num] dataset_name :
 *
 * @returns {Plotly.newPlot()} Types and descriptions are both supported.
 */
function createNormalizedIntensityPlot(all_results,div_id,dataset_name) {
    
    var data = [];


    // loop through fit types
    // use different marker styles for fit type and phase?
    // would be good be consistent for phase
    
    let t_2theta = [];
    let t_LB = [];
    let t_fit = [];
    
    let phase_mean = 0;

    // loop through unique phases
    
    for(let i = 0; i < all_results['unique_phases'].length; i++) {

        // loop through Phase column for matches to current phase
        // Also loop through all datasets?[j]
        for(let j = 0; j < all_results[dataset_name]['n_int_plot_data']['Phase'].length; j++) {
 
            // CHECK - May only work for single dataset
             if(all_results[dataset_name]['n_int_plot_data']['Phase'][j] == all_results['unique_phases'][i])  {
                t_2theta.push(all_results[dataset_name]['n_int_plot_data']['pos_TI'][j]);
                t_LB.push(all_results[dataset_name]['n_int_plot_data']['n_int_LB'][j]);
                t_fit.push(all_results[dataset_name]['n_int_plot_data']['n_int_fit'][j]);
            }
 
            //if( (all_results['n_int_plot_data']['Phase'][j] == all_results['unique_phases'][i]) &&
             //   (all_results['n_int_plot_data'].sample_index[j] == dataset_num) ) {
             //   t_x.push(all_results['n_int_plot_data'].pos_fit[j]);
             //   t_y.push(all_results['n_int_plot_data'].n_int[j]);
           // }

        }

        data.push({
            x: t_2theta,
            y: t_LB,
            mode:'markers',
            type: 'scatter',
            name: all_results['unique_phases'][i]+' Le Bail',
            marker: {
                color: customColorScale[i],
                symbol: "circle"
            }
        });

        data.push({
            x: t_2theta,
            y: t_fit,
            mode:'markers',
            type: 'scatter',
            name: all_results['unique_phases'][i]+' Peak Fit',
            marker: {
                color: customColorScale[i],
                symbol: "square"
            }
        });

        phase_mean_LB = math.sum(t_LB)/t_LB.length;
        phase_mean_fit = math.sum(t_fit)/t_fit.length;


        data.push({
            x: [math.min(all_results[dataset_name]['n_int_plot_data']['pos_TI']),math.max(all_results[dataset_name]['n_int_plot_data']['pos_TI'])],
            y: [phase_mean_LB, phase_mean_LB],
            name: all_results['unique_phases'][i]+' Le Bail',
            mode: 'lines',
            line: {dash: 'solid'},
            marker: {
                color: customColorScale[i]
            }
        });
        
        data.push({
            x: [math.min(all_results[dataset_name]['n_int_plot_data']['pos_TI']),math.max(all_results[dataset_name]['n_int_plot_data']['pos_TI'])],
            y: [phase_mean_fit, phase_mean_fit],
            name: all_results['unique_phases'][i]+' Peak Fit',
            mode: 'lines',
            line: {dash: 'dash'},
            marker: {
                color: customColorScale[i]
            }
        });
        

        t_2theta = [];
        t_LB = [];
        t_fit = [];
    }
    
    // Add mean lines
    // ? from uncertainty table, if it has the mean?
    // Array.from({length: 10}, () => 5)
    // let text1 = "sea";
    // text1.concat(" ", text2);
    

    var layout = {
        title: 'Normalized Intensities',
        xaxis: {title: 'Two Theta'},
        yaxis: {title: 'Normalized Intensity'}
    };

    Plotly.newPlot(div_id, data, layout);
}

/**
 * Return the Phase Fraction Plot as a plotly object
 * CHECK - do we want to pass the 8000 MCMC runs, or bin ahead of time?
 *
 * @param [dict] all_results : dictionary with data
 * @param [str] div_id : ID for which division?
 *
 * @returns {Plotly.newPlot()} Types and descriptions are both supported.
 */
function createPhaseFractionPlot(all_results,div_id,which_conversion,dataset_name) {

    let mcmc_res = null;

    if(which_conversion == 'number') {
        mcmc_res = all_results[dataset_name]["phase_fraction_number_plot_data"];
    
    } else if(which_conversion == 'mass') {
        mcmc_res = all_results[dataset_name]["phase_fraction_mass_plot_data"];

    } else if(which_conversion == 'volume') {
        mcmc_res = all_results[dataset_name]["phase_fraction_volume_plot_data"];
    } else {
        return(null)
    }
    
    let data = [];

    for(let i = 0; i < all_results.unique_phases.length; i++) {

    // Changed to 100 bins from 80
        data.push({
            x:mcmc_res['phase_mu['.concat(i+1).concat(']')],
            type:'histogram',
            opacity:0.6,
            name: all_results.unique_phases[i],
            nbinsx: 100
        })

    }

    let layout = {
        barmode: 'overlay'
    }

    Plotly.newPlot(div_id, data, layout);

};

/**
 * Return the Diffracted Counts vs Z depth as a plotly object
 *
 * @param [dict] all_results : dictionary with data
 * @param [str] div_id : ID for which division?
 * @param [num] dataset_name :
 *
 * @returns {Plotly.newPlot()} Types and descriptions are both supported.
 */
function createZDepthPlot(all_results) {
    
    // html has Select Dataset, Phase, Peak
    
    // info probably in all_results.results_table and all_results.crystallites_dict
    // all_results['cryst_ill_res'] just has the N layers, N illuminated, diffracting fraction, N_diffracted
    // graph_data_table
    
    //all_results['graph_data_table'][phase][index of peak list]
    
    //all_results['graph_data_table'][phase][index of peak list][0] or [1], both pandas dataframes.  [0] just x,y,Length, Intensity,
    // [1] is midpoints,
    
}

function incidentAnglePlot(all_results) {

    // info probably in all_results.results_table and all_results.crystallites_dict

}


