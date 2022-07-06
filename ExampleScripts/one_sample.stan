data {
    int<lower=0> N;
    int<lower=0> N_phases;
    vector<lower=0>[N] Y;
    int phase[N];
    real<lower=0> prior_scale;
    real<lower=0> prior_location;
}

parameters {
    vector<lower=0>[N_phases] sigma_exp;
    vector<lower=0>[N_phases] phase_mu;
}

model {
    sigma_exp ~ student_t(4,0,prior_scale); // half-t4
    phase_mu ~ normal(prior_location,prior_scale*5); // diffuse half-normal
    Y ~ normal(phase_mu[phase],sigma_exp[phase]);
}