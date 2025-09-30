
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
        //x: all_results[dataset_name].Gaussian_fit_two_thetas,
        //y: all_results[dataset_name].Gaussian_fit,
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

    // Gaussian fit
    // need different positions due to only fitting over windows
    // Commented out for now to avoid confusion
//    data.push({
//            x: all_results[dataset_name].Gaussian_fit_two_thetas,
//            y: all_results[dataset_name].Gaussian_fit,
//            //x: all_results[dataset_name].two_thetas,
//            //y: all_results[dataset_name].Gaussian_fit,
//            mode: 'lines+markers',
//            type: 'scatter',
//            name: 'Single Gaussian Fit',
//            color: customColorScale[2]
//        });


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
        yaxis: {title: 'Normalized Intensity'},
        height: 400,
        width: 800
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

    if(which_conversion == 'Number of Unit Cells') {
        mcmc_res = all_results[dataset_name]["phase_fraction_number_plot_data"];
    
    } else if(which_conversion == 'Mass Fraction') {
        mcmc_res = all_results[dataset_name]["phase_fraction_mass_plot_data"];

    } else if(which_conversion == 'Volume Fraction') {
        mcmc_res = all_results[dataset_name]["phase_fraction_volume_plot_data"];
    } else {
        return(null)
    }
    
    let data = [];

    for(let i = 0; i < all_results.unique_phases.length; i++) {

    // Histogram
    // Changed to 100 bins from 80
        data.push({
            x:mcmc_res['phase_mu['.concat(i+1).concat(']')],
            type:'histogram',
            opacity:0.6,
            name: all_results.unique_phases[i],
            nbinsx: 100
        })

    // Add mean, sigma lines?  Need to pass data or recompute?

    }

    let layout = {
        barmode:'overlay',
        height:400,
        width:1000,
        xaxis: {range: [0, 1]},
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
function createZDepthPlot(all_results,div_id,dataset_name,peak_index) {
    
    // html has Select Dataset, Phase, Peak
    
    // info probably in all_results.results_table and all_results.crystallites_dict
    // all_results['cryst_ill_res'] just has the N layers, N illuminated, diffracting fraction, N_diffracted
    // graph_data_table
    
    //all_results['graph_data_table'][phase][index of peak list]
    
    //all_results['graph_data_table'][phase][index of peak list][0] or [1], both pandas dataframes.  [0] just x,y,Length, Intensity,
    // [1] is midpoints,
    
    var data = [{

        type: 'bar',
        x: all_results[dataset_name]["Z_Depth_plot_data"]['Escaped'][peak_index],
        y: all_results[dataset_name]["Z_Depth_plot_data"]['Z_Depth'][peak_index],
        orientation: 'h',
        marker: {
            color: 'rgb(0, 0, 0)'
            },
        name: 'X-rays escaped',

    }];

    data.push({
            x: [all_results[dataset_name]["Z_Depth_plot_data"]['Count_Bound'][0][peak_index], all_results[dataset_name]["Z_Depth_plot_data"]['Count_Bound'][1][peak_index]],
            y: [all_results[dataset_name]["Z_Depth_plot_data"]['95pct_Bound'][0][peak_index], all_results[dataset_name]["Z_Depth_plot_data"]['95pct_Bound'][1][peak_index]],
            name: '95% Bound',
            mode: 'lines',
            line: {dash: 'dashdot'},
            color: 'rgb(255, 0, 0)',
            
    });

    data.push({
            x: [all_results[dataset_name]["Z_Depth_plot_data"]['Count_Bound'][0][peak_index], all_results[dataset_name]["Z_Depth_plot_data"]['Count_Bound'][1][peak_index]],
            y: [all_results[dataset_name]["Z_Depth_plot_data"]['68pct_Bound'][0][peak_index], all_results[dataset_name]["Z_Depth_plot_data"]['68pct_Bound'][1][peak_index]],
            name: '68% Bound',
            mode: 'lines',
            line: {dash: 'dash'},
            color: 'rgb(0, 255, 0)',
            
    });
    
    data.push({
            x: [all_results[dataset_name]["Z_Depth_plot_data"]['Count_Bound'][0][peak_index], all_results[dataset_name]["Z_Depth_plot_data"]['Count_Bound'][1][peak_index]],
            y: [all_results[dataset_name]["Z_Depth_plot_data"]['50pct_Bound'][0][peak_index], all_results[dataset_name]["Z_Depth_plot_data"]['50pct_Bound'][1][peak_index]],
            name: '50% Bound',
            mode: 'lines',
            line: {dash: 'dot'},
            color: 'rgb(0, 0, 255)',
            
    });    


    var layout = {
        title: 'X-rays Escaped vs. Z Depth (assumed x-ray flux of 1 000 000)',
        xaxis: {title: 'X-rays Escaped [counts]'},
        yaxis: {title: 'Z [um]'},
        height: 400,
        width: 800,
        // Use a consistent Z range
        yaxis: {range: [all_results[dataset_name]["Z_Depth_plot_min"], 0 ]}
        // Shapes for bounding lines
//        shapes: [
//    {
//
//      type: 'line',
//      x0: all_results[dataset_name]["Z_Depth_plot_data"]['Count_Bound'][0][peak_index],
//      y0: all_results[dataset_name]["Z_Depth_plot_data"]['95pct_Bound'][0][peak_index],
//      x1: all_results[dataset_name]["Z_Depth_plot_data"]['Count_Bound'][1][peak_index],
//      y1: all_results[dataset_name]["Z_Depth_plot_data"]['95pct_Bound'][1][peak_index],
//      line: {
//        color: 'rgb(255, 0, 0)',
//        width: 3,
//        dash: 'dashdot'
//      }
//    },

//    {
//      type: 'line',
//      x0: 2,
//      y0: 2,
//      x1: 5,
//      y1: 2,
//      line: {
//        color: 'rgb(50, 171, 96)',
//        width: 4,
//        dash: 'dashdot'
//      }
//    },
//
//
//    //Line Diagonal
//    {
//      type: 'line',
//      x0: 4,
//      y0: 0,
//      x1: 6,
//      y1: 2,
//      line: {
//        color: 'rgb(128, 0, 128)',
//        width: 4,
//        dash: 'dot'
//      }
//    }
//  ]
        
        
      };
    
    Plotly.newPlot(div_id, data, layout);

    
    
}


/**
 * Return the Incident Xrays in an X vs Z depth as a plotly object
 *
 * @param [dict] all_results : dictionary with data
 * @param [str] div_id : ID for which division?
 * @param [num] dataset_name :
 * @param [num] peak_index : Index of the peak to plot
 *
 * @returns {Plotly.newPlot()} Types and descriptions are both supported.
 */
function createIncidentAnglePlot(all_results,div_id,dataset_name,peak_index) {
    // Show the incident beam and the angle into the surface
    // info probably in all_results.results_table and all_results.crystallites_dict
    var trace1 = {
        x: all_results[dataset_name]["Incident_Angle_plot_data"]['I_X_Endpoints'][peak_index],
        y: all_results[dataset_name]["Incident_Angle_plot_data"]['I_Z_Endpoints'][peak_index],
        type: 'scatter',
        mode: 'lines',
        line: {dash: 'solid'},
        name: 'Line of Incident X-rays',
        marker: {
            color: 'rgb(0, 0, 0)',
                }
    };
    // Penetrating X-rays
    var trace2 = {
        x: all_results[dataset_name]["Incident_Angle_plot_data"]['P_X_Endpoints'][peak_index],
        y: all_results[dataset_name]["Incident_Angle_plot_data"]['P_Z_Endpoints'][peak_index],
        type: 'scatter',
        mode: 'lines',
        line: {dash: 'dash'},
        name: 'Line of Penetrating X-rays',
        marker: {
            color: 'rgb(128, 128, 128)',
                }
    };
    // Diffracted X-rays
    var trace3 = {
        x: all_results[dataset_name]["Incident_Angle_plot_data"]['D_X_Endpoints'][peak_index],
        y: all_results[dataset_name]["Incident_Angle_plot_data"]['D_Z_Endpoints'][peak_index],
        type: 'scatter',
        mode: 'lines',
        line: {dash: 'dot'},
        name: 'Line of Diffracting X-rays',
        marker: {
            color: 'rgb(190, 190, 190)',
                }
    };
    // Need a consistent box, otherwise plot autoscales
    var trace4 = {
        x: all_results[dataset_name]["Incident_Angle_plot_data"]['X_Bounds'],
        y: all_results[dataset_name]["Incident_Angle_plot_data"]['Z_Bounds'],
        type: 'scatter',
        mode: 'markers',
        name: '',
        marker: {
            color: 'rgb(255, 255, 255)',
                }
    };

    var data = [trace1,trace2,trace3,trace4 ];

    var layout = {
        title: 'Incident X-ray and ',
        xaxis: {title: 'X [um]'},
        yaxis: {title: 'Z [um]'},
        aspectmode: "cube",
        width: 600,
        height: 600,
        showlegend: true,
        legend: {
            x: 0,
            xanchor: 'left',
            y: 0
                }
      };
    
    Plotly.newPlot(div_id, data, layout);

}
