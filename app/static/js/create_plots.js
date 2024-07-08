
function createRawIntensityPlot(all_results,div_id,dataset_name) {

    var trace1 = {
        x: all_results.two_thetas[dataset_name],
        y: all_results.fit_points[dataset_name][0],
        type: 'scatter'
    };
      
    var data = [trace1];

    var layout = {
        title: 'Raw Intensities',
        xaxis: {title: 'Two Theta'},
        yaxis: {title: 'Intensity'}
      };
    
    Plotly.newPlot(div_id, data, layout);

}

function createFittedIntensityPlot(all_results,div_id,dataset_name) {

    var trace1 = {
        x: all_results.two_thetas[dataset_name],
        y: all_results.fit_points[dataset_name][0],
        type: 'scatter'
    };

    var trace2 = {
        x: all_results.two_thetas[dataset_name],
        y: all_results.fit_points[dataset_name][2],
        type: 'scatter'
    };
      
    var data = [trace1,trace2];

    var layout = {
        title: 'Fitted Intensities',
        xaxis: {title: 'Two Theta'},
        yaxis: {title: 'Intensity'}
    };
    
    Plotly.newPlot(div_id, data, layout);

}

function createNormalizedIntensityPlot(all_results,div_id,dataset_name) {
    
    var data = [];

    let t_x = [];
    let t_y = [];

    for(let i = 0; i < all_results.unique_phases.length; i++) {

        for(let j = 0; j < all_results.results_table.Phase.length; j++) {
            
            if(all_results.results_table.Phase[j] == all_results.unique_phases[i]) {
                t_x.push(all_results.results_table.pos_fit[j]);
                t_y.push(all_results.results_table.n_int[j]);
            }

        }

        data.push({
            x: t_x,
            y: t_y,
            mode:'markers',
            type: 'scatter'
        });

        t_x = [];
        t_y = [];

    }

    var layout = {
        title: 'Normalized Intensities',
        xaxis: {title: 'Two Theta'},
        yaxis: {title: 'Normalized Intensity'}
    };

    Plotly.newPlot(div_id, data, layout);
}

function createPhaseFractionPlot(all_results,div_id) {

    let data = [];

    for(let i = 0; i < all_results.unique_phases.length; i++) {

        data.push({
            x:all_results.mcmc_df['phase_mu['.concat(i+1).concat(']')],
            type:'histogram',
            opacity:0.6
        })

    }

    Plotly.newPlot(div_id, data);

};