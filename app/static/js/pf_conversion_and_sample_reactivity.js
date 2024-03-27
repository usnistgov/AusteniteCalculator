let conversion_select = document.getElementById("conversion-select");

conversion_select.addEventListener("change", function() {
    console.log("event triggered");
    let pf_plot = document.getElementById("pf-plot");

    console.log(this.selectedIndex)

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