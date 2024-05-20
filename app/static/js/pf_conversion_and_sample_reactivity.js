let conversion_select = document.getElementById("conversion-select");

conversion_select.addEventListener("change", function() {
    console.log("event triggered");
    let pf_plot = document.getElementById("pf-plot");

    //console.log(this.selectedIndex)

    if(this.selectedIndex==0) {
        pf_plot.src = results_storage.pf_plot_num_unit_cells;
    }

    if(this.selectedIndex==1) {
        pf_plot.src = results_storage.pf_plot_mass_frac;
    }

    if(this.selectedIndex==2) {
        pf_plot.src = results_storage.pf_plot_vol_frac;
    }
    
})

let intensity_plots_select = document.getElementById("intensity-plots-select");

intensity_plots_select.addEventListener("change", function() {

    let raw_intensity_plot_img = document.getElementById("raw-intensity-plot-img");
    let fitted_intensity_plot_img = document.getElementById("fitted-intensity-plot-img");

    raw_intensity_plot_img.src = results_storage.raw_intensity_plot[this.selectedIndex + 1];
    fitted_intensity_plot_img.src = results_storage.fitted_intensity_plot[this.selectedIndex + 1];
})

let normalized_intensities_plot_select = document.getElementById("normalized-intensity-plots-select");

normalized_intensities_plot_select.addEventListener("change",function() {

    let normalized_intensities_plot_img = document.getElementById("normalized-intensity-plot-img");
    console.log(this.selectedIndex);
    normalized_intensities_plot_img.src = results_storage.normalized_intensity_plot[this.selectedIndex + 1];

})