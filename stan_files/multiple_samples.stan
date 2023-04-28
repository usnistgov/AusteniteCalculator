data {
    int<lower=0> N;
    int<lower=0> N_samples;
    int<lower=0> N_phases;
    int<lower=0> N_phase_samples;
    vector<lower=0>[N] Y;
    array[N] int phase;
    array[N] int group;
    array[N] int phase_sample_id;
    real<lower=0> prior_scale;
    real<lower=0> prior_sample_scale;
    real<lower=0> prior_exp_scale;
    vector<lower=0>[N_phases] prior_location;
    vector<lower=0>[N] u_int_fit;
    vector<lower=0>[N] u_int_count;
}

parameters {
    real<lower=0> sigma_sample; // variability from sample to sample for each phase
    vector<lower=0>[N_phases] sigma_exp; // experimental error, varies w/ phase
    vector<lower=0>[N_phases] phase_mu; // phase means
    real<lower=0> sample_effect[N_samples, N_phases]; // effect for each phase and sample combo
}

model {

    // priors
    // based on recommendations from https://github.com/stan-dev/stan/wiki/Prior-Choice-Recommendations 
    //sigma_sample ~ student_t(4,0,prior_sample_scale);
    sigma_sample ~ student_t(4,0,prior_sample_scale);
    sigma_exp ~ student_t(4,0,prior_exp_scale); // half-t4 or normal
    phase_mu ~ normal(prior_location,prior_scale*2); // truncated normals

    // likelihood

    // latent effects
    for (ii in 1:N_samples) {
        for (jj in 1:N_phases) {
            sample_effect[ii,jj] ~ normal(phase[jj],sigma_sample);
        }
    }
    
    // observed values
    for (ii in 1:N) {
        Y[ii] ~ normal(phase_mu[phase[ii]] + sample_effect[group[ii],phase[ii]],
                       sqrt(sigma_exp[phase[ii]]^2 + u_int_fit[ii]^2 + u_int_count[ii]^2 ));
    }

}