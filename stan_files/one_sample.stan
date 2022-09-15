data {
    int<lower=0> N;
    int<lower=0> N_phases;
    vector<lower=0>[N] Y;
    int phase[N];
    real<lower=0> prior_scale;
    real<lower=0> prior_exp_scale;
    vector<lower=0>[N_phases] prior_location;
    vector<lower=0>[N] u_int_fit;
    vector<lower=0>[N] u_int_count;
}

parameters {
    vector<lower=0>[N_phases] sigma_exp;
    vector<lower=0>[N_phases] phase_mu;
}

model {
    sigma_exp ~ student_t(4,0,prior_exp_scale); // half-t4
    phase_mu ~ normal(prior_location,prior_scale*2); // diffuse half-normal
    Y ~ normal(phase_mu[phase],sqrt(sigma_exp[phase]^2 + u_int_count^2 + u_int_fit^2) );
}