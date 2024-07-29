let conversion_select = document.getElementById("conversion-select");

// below this needs to be changed
conversion_select.addEventListener("change", function() {
    console.log("event triggered");

    let cs = document.getElementById('conversion-select');
    let conversion_option = cs.options[cs.options.selectedIndex].innerText;

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

    createPhaseFractionPlot(all_results,'phase-fraction-plot',conversion_option);
    
})

let intensity_plots_select = document.getElementById("intensity-plots-select");

intensity_plots_select.addEventListener("change", function() {

    let raw_intensity_plot_img = document.getElementById("raw-intensity-plot-img");
    let fitted_intensity_plot_img = document.getElementById("fitted-intensity-plot-img");

    // plot the dataset based on which is selcted in this.selectedIndex

    // raw_intensity_plot_img.src = results_storage.raw_intensity_plot[this.selectedIndex + 1];
    // fitted_intensity_plot_img.src = results_storage.fitted_intensity_plot[this.selectedIndex + 1];
})

let normalized_intensities_plot_select = document.getElementById("normalized-intensity-plots-select");

normalized_intensities_plot_select.addEventListener("change",function() {

    let normalized_intensities_plot_img = document.getElementById("normalized-intensity-plot-img");
    console.log(this.selectedIndex);

    // same as above


})