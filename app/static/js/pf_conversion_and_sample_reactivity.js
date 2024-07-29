let conversion_select = document.getElementById("conversion-select");

// below this needs to be changed
conversion_select.addEventListener("change", function() {
    console.log("event triggered");
    let pf_plot = document.getElementById("pf-plot");

    // put function to create new plot based on conversion
    
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