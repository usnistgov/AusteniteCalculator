data {
    int<lower=0> N;
    int<lower=0> N_phases;
    vector<lower=0>[N] Y;
    array[N] int phase;
    real<lower=0> prior_scale;
    real<lower=0> prior_exp_scale;
    vector<lower=0>[N_phases] prior_location;
    vector<lower=0>[N] u_int_fit;
    vector<lower=0>[N] u_int_count;
    vector<lower=0>[N] u_cryst_diff;
}

parameters {
    vector<lower=0>[N_phases] sigma_exp; 
    vector<lower=0>[N_phases] phase_mu; 
}

model {
    sigma_exp ~ student_t(4,0,prior_exp_scale); // half-t4
    phase_mu ~ normal(prior_location,prior_scale*2); // diffuse half-normal
    for(ii in 1:N) {
        Y[ii] ~ normal(phase_mu[ phase[ii] ],sqrt(sigma_exp[ phase[ii] ]^2 + u_int_count[ii]^2 + u_int_fit[ii]^2 + u_cryst_diff[ii]^2) );
    }
    
}