data {
    int<lower=0> N;
    int<lower=0> N_samples;
    int<lower=0> N_phases;
    vector<lower=0>[N] Y;
    array[N] int phase;
    array[N] int group;
    real<lower=0> prior_scale;
    real<lower=0> prior_location;
    vector<lower=0>[N] u_int_fit;
    vector<lower=0>[N] u_int_count;
}

parameters {
    real<lower=0> sigma_sample; // std dev of group effects
    vector<lower=0>[N_phases] sigma_exp; // experimental error, varies w/ phase
    vector<lower=0>[N_phases] phase_mu; // phase means
    vector[N_samples] group_effect; // latent group effects
}

model {

    // priors
    sigma_sample ~ student_t(4,0,prior_scale);
    sigma_exp ~ student_t(4,0,prior_scale); // half-t4
    phase_mu ~ normal(prior_location,prior_scale*5); // diffuse half-normal

    // likelihood
    for (ii in 1:N_samples ) {
        group_effect[ii] ~ normal(0,sigma_sample);
    }
    
    for (ii in 1:N) {
        Y[ii] ~ normal(phase_mu[phase[ii]] + group_effect[group[ii]],sqrt(sigma_exp[phase[ii]]**2 + u_int_fit[ii]**2 + u_int_count[ii]**2 ));
    }

}