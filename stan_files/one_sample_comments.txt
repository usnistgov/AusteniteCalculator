// N is the number of peaks
// data has the prior estimates
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

// these are posterior estimates
parameters {
    vector<lower=0>[N_phases] sigma_exp; // residual uncertainty in model, 
    vector<lower=0>[N_phases] phase_mu; // mean value in model
}

// looks backwards because of how Bayesian models with priors work
// Y is a fixed constant, and adjusting the phase mean (phase_mu) and sigma_exp to match?!?
// phase_mu is the unknown mean with unknown standard devation (sigma_exp)
// Stan makes this process easy to write (but harder to invert)

// model generates posterior estimates from the functional form of Y
// these are the priors, not a distribution to draw from
// additional uncertainty terms are included in the fitting of phase_mu, but 
// they are not included in the sigma_exp term directly

// Y ~ normal(...) is not sampling from a 'normal' distribution
// it is only specifying the relationship between the data (Y)
// and the posterior estimates

model {
    sigma_exp ~ student_t(4,0,prior_exp_scale); // half-t4
    phase_mu ~ normal(prior_location,prior_scale*2); // diffuse half-normal
    for(ii in 1:N) {
        Y[ii] ~ normal(phase_mu[ phase[ii] ],sqrt(sigma_exp[ phase[ii] ]^2 + u_int_count[ii]^2 + u_int_fit[ii]^2 + u_cryst_diff[ii]^2) );
    }
    
}