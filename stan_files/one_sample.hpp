// Code generated by stanc v2.33.1
#include <stan/model/model_header.hpp>
namespace one_sample_model_namespace {
using stan::model::model_base_crtp;
using namespace stan::math;
stan::math::profile_map profiles__;
static constexpr std::array<const char*, 26> locations_array__ =
  {" (found before start of program)",
  " (in 'one_sample.stan', line 15, column 4 to column 40)",
  " (in 'one_sample.stan', line 16, column 4 to column 39)",
  " (in 'one_sample.stan', line 20, column 4 to column 47)",
  " (in 'one_sample.stan', line 21, column 4 to column 52)",
  " (in 'one_sample.stan', line 23, column 8 to column 137)",
  " (in 'one_sample.stan', line 22, column 19 to line 24, column 5)",
  " (in 'one_sample.stan', line 22, column 4 to line 24, column 5)",
  " (in 'one_sample.stan', line 2, column 4 to column 19)",
  " (in 'one_sample.stan', line 3, column 4 to column 26)",
  " (in 'one_sample.stan', line 4, column 20 to column 21)",
  " (in 'one_sample.stan', line 4, column 4 to column 25)",
  " (in 'one_sample.stan', line 5, column 10 to column 11)",
  " (in 'one_sample.stan', line 5, column 4 to column 23)",
  " (in 'one_sample.stan', line 6, column 4 to column 30)",
  " (in 'one_sample.stan', line 7, column 4 to column 34)",
  " (in 'one_sample.stan', line 8, column 20 to column 28)",
  " (in 'one_sample.stan', line 8, column 4 to column 45)",
  " (in 'one_sample.stan', line 9, column 20 to column 21)",
  " (in 'one_sample.stan', line 9, column 4 to column 33)",
  " (in 'one_sample.stan', line 10, column 20 to column 21)",
  " (in 'one_sample.stan', line 10, column 4 to column 35)",
  " (in 'one_sample.stan', line 11, column 20 to column 21)",
  " (in 'one_sample.stan', line 11, column 4 to column 36)",
  " (in 'one_sample.stan', line 15, column 20 to column 28)",
  " (in 'one_sample.stan', line 16, column 20 to column 28)"};
class one_sample_model final : public model_base_crtp<one_sample_model> {
 private:
  int N;
  int N_phases;
  Eigen::Matrix<double,-1,1> Y_data__;
  std::vector<int> phase;
  double prior_scale;
  double prior_exp_scale;
  Eigen::Matrix<double,-1,1> prior_location_data__;
  Eigen::Matrix<double,-1,1> u_int_fit_data__;
  Eigen::Matrix<double,-1,1> u_int_count_data__;
  Eigen::Matrix<double,-1,1> u_cryst_diff_data__;
  Eigen::Map<Eigen::Matrix<double,-1,1>> Y{nullptr, 0};
  Eigen::Map<Eigen::Matrix<double,-1,1>> prior_location{nullptr, 0};
  Eigen::Map<Eigen::Matrix<double,-1,1>> u_int_fit{nullptr, 0};
  Eigen::Map<Eigen::Matrix<double,-1,1>> u_int_count{nullptr, 0};
  Eigen::Map<Eigen::Matrix<double,-1,1>> u_cryst_diff{nullptr, 0};
 public:
  ~one_sample_model() {}
  one_sample_model(stan::io::var_context& context__, unsigned int
                   random_seed__ = 0, std::ostream* pstream__ = nullptr)
      : model_base_crtp(0) {
    int current_statement__ = 0;
    // suppress unused var warning
    (void) current_statement__;
    using local_scalar_t__ = double;
    boost::ecuyer1988 base_rng__ =
      stan::services::util::create_rng(random_seed__, 0);
    // suppress unused var warning
    (void) base_rng__;
    static constexpr const char* function__ =
      "one_sample_model_namespace::one_sample_model";
    // suppress unused var warning
    (void) function__;
    local_scalar_t__ DUMMY_VAR__(std::numeric_limits<double>::quiet_NaN());
    // suppress unused var warning
    (void) DUMMY_VAR__;
    try {
      int pos__ = std::numeric_limits<int>::min();
      pos__ = 1;
      current_statement__ = 8;
      context__.validate_dims("data initialization", "N", "int",
        std::vector<size_t>{});
      N = std::numeric_limits<int>::min();
      current_statement__ = 8;
      N = context__.vals_i("N")[(1 - 1)];
      current_statement__ = 8;
      stan::math::check_greater_or_equal(function__, "N", N, 0);
      current_statement__ = 9;
      context__.validate_dims("data initialization", "N_phases", "int",
        std::vector<size_t>{});
      N_phases = std::numeric_limits<int>::min();
      current_statement__ = 9;
      N_phases = context__.vals_i("N_phases")[(1 - 1)];
      current_statement__ = 9;
      stan::math::check_greater_or_equal(function__, "N_phases", N_phases, 0);
      current_statement__ = 10;
      stan::math::validate_non_negative_index("Y", "N", N);
      current_statement__ = 11;
      context__.validate_dims("data initialization", "Y", "double",
        std::vector<size_t>{static_cast<size_t>(N)});
      Y_data__ = Eigen::Matrix<double,-1,1>::Constant(N,
                   std::numeric_limits<double>::quiet_NaN());
      new (&Y) Eigen::Map<Eigen::Matrix<double,-1,1>>(Y_data__.data(), N);
      {
        std::vector<local_scalar_t__> Y_flat__;
        current_statement__ = 11;
        Y_flat__ = context__.vals_r("Y");
        pos__ = 1;
        for (int sym1__ = 1; sym1__ <= N; ++sym1__) {
          stan::model::assign(Y, Y_flat__[(pos__ - 1)],
            "assigning variable Y", stan::model::index_uni(sym1__));
          pos__ = (pos__ + 1);
        }
      }
      current_statement__ = 11;
      stan::math::check_greater_or_equal(function__, "Y", Y, 0);
      current_statement__ = 12;
      stan::math::validate_non_negative_index("phase", "N", N);
      current_statement__ = 13;
      context__.validate_dims("data initialization", "phase", "int",
        std::vector<size_t>{static_cast<size_t>(N)});
      phase = std::vector<int>(N, std::numeric_limits<int>::min());
      current_statement__ = 13;
      phase = context__.vals_i("phase");
      current_statement__ = 14;
      context__.validate_dims("data initialization", "prior_scale", "double",
        std::vector<size_t>{});
      prior_scale = std::numeric_limits<double>::quiet_NaN();
      current_statement__ = 14;
      prior_scale = context__.vals_r("prior_scale")[(1 - 1)];
      current_statement__ = 14;
      stan::math::check_greater_or_equal(function__, "prior_scale",
        prior_scale, 0);
      current_statement__ = 15;
      context__.validate_dims("data initialization", "prior_exp_scale",
        "double", std::vector<size_t>{});
      prior_exp_scale = std::numeric_limits<double>::quiet_NaN();
      current_statement__ = 15;
      prior_exp_scale = context__.vals_r("prior_exp_scale")[(1 - 1)];
      current_statement__ = 15;
      stan::math::check_greater_or_equal(function__, "prior_exp_scale",
        prior_exp_scale, 0);
      current_statement__ = 16;
      stan::math::validate_non_negative_index("prior_location", "N_phases",
        N_phases);
      current_statement__ = 17;
      context__.validate_dims("data initialization", "prior_location",
        "double", std::vector<size_t>{static_cast<size_t>(N_phases)});
      prior_location_data__ = Eigen::Matrix<double,-1,1>::Constant(N_phases,
                                std::numeric_limits<double>::quiet_NaN());
      new (&prior_location)
        Eigen::Map<Eigen::Matrix<double,-1,1>>(prior_location_data__.data(),
        N_phases);
      {
        std::vector<local_scalar_t__> prior_location_flat__;
        current_statement__ = 17;
        prior_location_flat__ = context__.vals_r("prior_location");
        pos__ = 1;
        for (int sym1__ = 1; sym1__ <= N_phases; ++sym1__) {
          stan::model::assign(prior_location, prior_location_flat__[(pos__ -
            1)], "assigning variable prior_location",
            stan::model::index_uni(sym1__));
          pos__ = (pos__ + 1);
        }
      }
      current_statement__ = 17;
      stan::math::check_greater_or_equal(function__, "prior_location",
        prior_location, 0);
      current_statement__ = 18;
      stan::math::validate_non_negative_index("u_int_fit", "N", N);
      current_statement__ = 19;
      context__.validate_dims("data initialization", "u_int_fit", "double",
        std::vector<size_t>{static_cast<size_t>(N)});
      u_int_fit_data__ = Eigen::Matrix<double,-1,1>::Constant(N,
                           std::numeric_limits<double>::quiet_NaN());
      new (&u_int_fit)
        Eigen::Map<Eigen::Matrix<double,-1,1>>(u_int_fit_data__.data(), N);
      {
        std::vector<local_scalar_t__> u_int_fit_flat__;
        current_statement__ = 19;
        u_int_fit_flat__ = context__.vals_r("u_int_fit");
        pos__ = 1;
        for (int sym1__ = 1; sym1__ <= N; ++sym1__) {
          stan::model::assign(u_int_fit, u_int_fit_flat__[(pos__ - 1)],
            "assigning variable u_int_fit", stan::model::index_uni(sym1__));
          pos__ = (pos__ + 1);
        }
      }
      current_statement__ = 19;
      stan::math::check_greater_or_equal(function__, "u_int_fit", u_int_fit,
        0);
      current_statement__ = 20;
      stan::math::validate_non_negative_index("u_int_count", "N", N);
      current_statement__ = 21;
      context__.validate_dims("data initialization", "u_int_count", "double",
        std::vector<size_t>{static_cast<size_t>(N)});
      u_int_count_data__ = Eigen::Matrix<double,-1,1>::Constant(N,
                             std::numeric_limits<double>::quiet_NaN());
      new (&u_int_count)
        Eigen::Map<Eigen::Matrix<double,-1,1>>(u_int_count_data__.data(), N);
      {
        std::vector<local_scalar_t__> u_int_count_flat__;
        current_statement__ = 21;
        u_int_count_flat__ = context__.vals_r("u_int_count");
        pos__ = 1;
        for (int sym1__ = 1; sym1__ <= N; ++sym1__) {
          stan::model::assign(u_int_count, u_int_count_flat__[(pos__ - 1)],
            "assigning variable u_int_count", stan::model::index_uni(sym1__));
          pos__ = (pos__ + 1);
        }
      }
      current_statement__ = 21;
      stan::math::check_greater_or_equal(function__, "u_int_count",
        u_int_count, 0);
      current_statement__ = 22;
      stan::math::validate_non_negative_index("u_cryst_diff", "N", N);
      current_statement__ = 23;
      context__.validate_dims("data initialization", "u_cryst_diff",
        "double", std::vector<size_t>{static_cast<size_t>(N)});
      u_cryst_diff_data__ = Eigen::Matrix<double,-1,1>::Constant(N,
                              std::numeric_limits<double>::quiet_NaN());
      new (&u_cryst_diff)
        Eigen::Map<Eigen::Matrix<double,-1,1>>(u_cryst_diff_data__.data(), N);
      {
        std::vector<local_scalar_t__> u_cryst_diff_flat__;
        current_statement__ = 23;
        u_cryst_diff_flat__ = context__.vals_r("u_cryst_diff");
        pos__ = 1;
        for (int sym1__ = 1; sym1__ <= N; ++sym1__) {
          stan::model::assign(u_cryst_diff, u_cryst_diff_flat__[(pos__ - 1)],
            "assigning variable u_cryst_diff", stan::model::index_uni(sym1__));
          pos__ = (pos__ + 1);
        }
      }
      current_statement__ = 23;
      stan::math::check_greater_or_equal(function__, "u_cryst_diff",
        u_cryst_diff, 0);
      current_statement__ = 24;
      stan::math::validate_non_negative_index("sigma_exp", "N_phases",
        N_phases);
      current_statement__ = 25;
      stan::math::validate_non_negative_index("phase_mu", "N_phases",
        N_phases);
    } catch (const std::exception& e) {
      stan::lang::rethrow_located(e, locations_array__[current_statement__]);
    }
    num_params_r__ = N_phases + N_phases;
  }
  inline std::string model_name() const final {
    return "one_sample_model";
  }
  inline std::vector<std::string> model_compile_info() const noexcept {
    return std::vector<std::string>{"stanc_version = stanc3 v2.33.1",
             "stancflags = --filename-in-msg=one_sample.stan"};
  }
  // Base log prob
  template <bool propto__, bool jacobian__, typename VecR, typename VecI,
            stan::require_vector_like_t<VecR>* = nullptr,
            stan::require_vector_like_vt<std::is_integral, VecI>* = nullptr,
            stan::require_not_st_var<VecR>* = nullptr>
  inline stan::scalar_type_t<VecR>
  log_prob_impl(VecR& params_r__, VecI& params_i__, std::ostream*
                pstream__ = nullptr) const {
    using T__ = stan::scalar_type_t<VecR>;
    using local_scalar_t__ = T__;
    T__ lp__(0.0);
    stan::math::accumulator<T__> lp_accum__;
    stan::io::deserializer<local_scalar_t__> in__(params_r__, params_i__);
    int current_statement__ = 0;
    // suppress unused var warning
    (void) current_statement__;
    local_scalar_t__ DUMMY_VAR__(std::numeric_limits<double>::quiet_NaN());
    // suppress unused var warning
    (void) DUMMY_VAR__;
    static constexpr const char* function__ =
      "one_sample_model_namespace::log_prob";
    // suppress unused var warning
    (void) function__;
    try {
      Eigen::Matrix<local_scalar_t__,-1,1> sigma_exp =
        Eigen::Matrix<local_scalar_t__,-1,1>::Constant(N_phases, DUMMY_VAR__);
      current_statement__ = 1;
      sigma_exp = in__.template read_constrain_lb<
                    Eigen::Matrix<local_scalar_t__,-1,1>, jacobian__>(0,
                    lp__, N_phases);
      Eigen::Matrix<local_scalar_t__,-1,1> phase_mu =
        Eigen::Matrix<local_scalar_t__,-1,1>::Constant(N_phases, DUMMY_VAR__);
      current_statement__ = 2;
      phase_mu = in__.template read_constrain_lb<
                   Eigen::Matrix<local_scalar_t__,-1,1>, jacobian__>(0, lp__,
                   N_phases);
      {
        current_statement__ = 3;
        lp_accum__.add(stan::math::student_t_lpdf<propto__>(sigma_exp, 4, 0,
                         prior_exp_scale));
        current_statement__ = 4;
        lp_accum__.add(stan::math::normal_lpdf<propto__>(phase_mu,
                         prior_location, (prior_scale * 2)));
        current_statement__ = 7;
        for (int ii = 1; ii <= N; ++ii) {
          current_statement__ = 5;
          lp_accum__.add(stan::math::normal_lpdf<propto__>(
                           stan::model::rvalue(Y, "Y",
                             stan::model::index_uni(ii)),
                           stan::model::rvalue(phase_mu, "phase_mu",
                             stan::model::index_uni(
                               stan::model::rvalue(phase, "phase",
                                 stan::model::index_uni(ii)))),
                           stan::math::sqrt(
                             (((stan::math::pow(
                                  stan::model::rvalue(sigma_exp, "sigma_exp",
                                    stan::model::index_uni(
                                      stan::model::rvalue(phase, "phase",
                                        stan::model::index_uni(ii)))), 2) +
                             stan::math::pow(
                               stan::model::rvalue(u_int_count,
                                 "u_int_count", stan::model::index_uni(ii)),
                               2)) +
                             stan::math::pow(
                               stan::model::rvalue(u_int_fit, "u_int_fit",
                                 stan::model::index_uni(ii)), 2)) +
                             stan::math::pow(
                               stan::model::rvalue(u_cryst_diff,
                                 "u_cryst_diff", stan::model::index_uni(ii)),
                               2)))));
        }
      }
    } catch (const std::exception& e) {
      stan::lang::rethrow_located(e, locations_array__[current_statement__]);
    }
    lp_accum__.add(lp__);
    return lp_accum__.sum();
  }
  // Reverse mode autodiff log prob
  template <bool propto__, bool jacobian__, typename VecR, typename VecI,
            stan::require_vector_like_t<VecR>* = nullptr,
            stan::require_vector_like_vt<std::is_integral, VecI>* = nullptr,
            stan::require_st_var<VecR>* = nullptr>
  inline stan::scalar_type_t<VecR>
  log_prob_impl(VecR& params_r__, VecI& params_i__, std::ostream*
                pstream__ = nullptr) const {
    using T__ = stan::scalar_type_t<VecR>;
    using local_scalar_t__ = T__;
    T__ lp__(0.0);
    stan::math::accumulator<T__> lp_accum__;
    stan::io::deserializer<local_scalar_t__> in__(params_r__, params_i__);
    int current_statement__ = 0;
    // suppress unused var warning
    (void) current_statement__;
    local_scalar_t__ DUMMY_VAR__(std::numeric_limits<double>::quiet_NaN());
    // suppress unused var warning
    (void) DUMMY_VAR__;
    static constexpr const char* function__ =
      "one_sample_model_namespace::log_prob";
    // suppress unused var warning
    (void) function__;
    try {
      Eigen::Matrix<local_scalar_t__,-1,1> sigma_exp =
        Eigen::Matrix<local_scalar_t__,-1,1>::Constant(N_phases, DUMMY_VAR__);
      current_statement__ = 1;
      sigma_exp = in__.template read_constrain_lb<
                    Eigen::Matrix<local_scalar_t__,-1,1>, jacobian__>(0,
                    lp__, N_phases);
      Eigen::Matrix<local_scalar_t__,-1,1> phase_mu =
        Eigen::Matrix<local_scalar_t__,-1,1>::Constant(N_phases, DUMMY_VAR__);
      current_statement__ = 2;
      phase_mu = in__.template read_constrain_lb<
                   Eigen::Matrix<local_scalar_t__,-1,1>, jacobian__>(0, lp__,
                   N_phases);
      {
        current_statement__ = 3;
        lp_accum__.add(stan::math::student_t_lpdf<propto__>(sigma_exp, 4, 0,
                         prior_exp_scale));
        current_statement__ = 4;
        lp_accum__.add(stan::math::normal_lpdf<propto__>(phase_mu,
                         prior_location, (prior_scale * 2)));
        current_statement__ = 7;
        for (int ii = 1; ii <= N; ++ii) {
          current_statement__ = 5;
          lp_accum__.add(stan::math::normal_lpdf<propto__>(
                           stan::model::rvalue(Y, "Y",
                             stan::model::index_uni(ii)),
                           stan::model::rvalue(phase_mu, "phase_mu",
                             stan::model::index_uni(
                               stan::model::rvalue(phase, "phase",
                                 stan::model::index_uni(ii)))),
                           stan::math::sqrt(
                             (((stan::math::pow(
                                  stan::model::rvalue(sigma_exp, "sigma_exp",
                                    stan::model::index_uni(
                                      stan::model::rvalue(phase, "phase",
                                        stan::model::index_uni(ii)))), 2) +
                             stan::math::pow(
                               stan::model::rvalue(u_int_count,
                                 "u_int_count", stan::model::index_uni(ii)),
                               2)) +
                             stan::math::pow(
                               stan::model::rvalue(u_int_fit, "u_int_fit",
                                 stan::model::index_uni(ii)), 2)) +
                             stan::math::pow(
                               stan::model::rvalue(u_cryst_diff,
                                 "u_cryst_diff", stan::model::index_uni(ii)),
                               2)))));
        }
      }
    } catch (const std::exception& e) {
      stan::lang::rethrow_located(e, locations_array__[current_statement__]);
    }
    lp_accum__.add(lp__);
    return lp_accum__.sum();
  }
  template <typename RNG, typename VecR, typename VecI, typename VecVar,
            stan::require_vector_like_vt<std::is_floating_point,
            VecR>* = nullptr, stan::require_vector_like_vt<std::is_integral,
            VecI>* = nullptr, stan::require_vector_vt<std::is_floating_point,
            VecVar>* = nullptr>
  inline void
  write_array_impl(RNG& base_rng__, VecR& params_r__, VecI& params_i__,
                   VecVar& vars__, const bool
                   emit_transformed_parameters__ = true, const bool
                   emit_generated_quantities__ = true, std::ostream*
                   pstream__ = nullptr) const {
    using local_scalar_t__ = double;
    stan::io::deserializer<local_scalar_t__> in__(params_r__, params_i__);
    stan::io::serializer<local_scalar_t__> out__(vars__);
    static constexpr bool propto__ = true;
    // suppress unused var warning
    (void) propto__;
    double lp__ = 0.0;
    // suppress unused var warning
    (void) lp__;
    int current_statement__ = 0;
    // suppress unused var warning
    (void) current_statement__;
    stan::math::accumulator<double> lp_accum__;
    local_scalar_t__ DUMMY_VAR__(std::numeric_limits<double>::quiet_NaN());
    // suppress unused var warning
    (void) DUMMY_VAR__;
    constexpr bool jacobian__ = false;
    // suppress unused var warning
    (void) jacobian__;
    static constexpr const char* function__ =
      "one_sample_model_namespace::write_array";
    // suppress unused var warning
    (void) function__;
    try {
      Eigen::Matrix<double,-1,1> sigma_exp =
        Eigen::Matrix<double,-1,1>::Constant(N_phases,
          std::numeric_limits<double>::quiet_NaN());
      current_statement__ = 1;
      sigma_exp = in__.template read_constrain_lb<
                    Eigen::Matrix<local_scalar_t__,-1,1>, jacobian__>(0,
                    lp__, N_phases);
      Eigen::Matrix<double,-1,1> phase_mu =
        Eigen::Matrix<double,-1,1>::Constant(N_phases,
          std::numeric_limits<double>::quiet_NaN());
      current_statement__ = 2;
      phase_mu = in__.template read_constrain_lb<
                   Eigen::Matrix<local_scalar_t__,-1,1>, jacobian__>(0, lp__,
                   N_phases);
      out__.write(sigma_exp);
      out__.write(phase_mu);
      if (stan::math::logical_negation(
            (stan::math::primitive_value(emit_transformed_parameters__) ||
            stan::math::primitive_value(emit_generated_quantities__)))) {
        return ;
      }
      if (stan::math::logical_negation(emit_generated_quantities__)) {
        return ;
      }
    } catch (const std::exception& e) {
      stan::lang::rethrow_located(e, locations_array__[current_statement__]);
    }
  }
  template <typename VecVar, typename VecI,
            stan::require_vector_t<VecVar>* = nullptr,
            stan::require_vector_like_vt<std::is_integral, VecI>* = nullptr>
  inline void
  unconstrain_array_impl(const VecVar& params_r__, const VecI& params_i__,
                         VecVar& vars__, std::ostream* pstream__ = nullptr) const {
    using local_scalar_t__ = double;
    stan::io::deserializer<local_scalar_t__> in__(params_r__, params_i__);
    stan::io::serializer<local_scalar_t__> out__(vars__);
    int current_statement__ = 0;
    // suppress unused var warning
    (void) current_statement__;
    local_scalar_t__ DUMMY_VAR__(std::numeric_limits<double>::quiet_NaN());
    // suppress unused var warning
    (void) DUMMY_VAR__;
    try {
      Eigen::Matrix<local_scalar_t__,-1,1> sigma_exp =
        Eigen::Matrix<local_scalar_t__,-1,1>::Constant(N_phases, DUMMY_VAR__);
      current_statement__ = 1;
      stan::model::assign(sigma_exp,
        in__.read<Eigen::Matrix<local_scalar_t__,-1,1>>(N_phases),
        "assigning variable sigma_exp");
      out__.write_free_lb(0, sigma_exp);
      Eigen::Matrix<local_scalar_t__,-1,1> phase_mu =
        Eigen::Matrix<local_scalar_t__,-1,1>::Constant(N_phases, DUMMY_VAR__);
      current_statement__ = 2;
      stan::model::assign(phase_mu,
        in__.read<Eigen::Matrix<local_scalar_t__,-1,1>>(N_phases),
        "assigning variable phase_mu");
      out__.write_free_lb(0, phase_mu);
    } catch (const std::exception& e) {
      stan::lang::rethrow_located(e, locations_array__[current_statement__]);
    }
  }
  template <typename VecVar, stan::require_vector_t<VecVar>* = nullptr>
  inline void
  transform_inits_impl(const stan::io::var_context& context__, VecVar&
                       vars__, std::ostream* pstream__ = nullptr) const {
    using local_scalar_t__ = double;
    stan::io::serializer<local_scalar_t__> out__(vars__);
    int current_statement__ = 0;
    // suppress unused var warning
    (void) current_statement__;
    local_scalar_t__ DUMMY_VAR__(std::numeric_limits<double>::quiet_NaN());
    // suppress unused var warning
    (void) DUMMY_VAR__;
    try {
      current_statement__ = 1;
      context__.validate_dims("parameter initialization", "sigma_exp",
        "double", std::vector<size_t>{static_cast<size_t>(N_phases)});
      current_statement__ = 2;
      context__.validate_dims("parameter initialization", "phase_mu",
        "double", std::vector<size_t>{static_cast<size_t>(N_phases)});
      int pos__ = std::numeric_limits<int>::min();
      pos__ = 1;
      Eigen::Matrix<local_scalar_t__,-1,1> sigma_exp =
        Eigen::Matrix<local_scalar_t__,-1,1>::Constant(N_phases, DUMMY_VAR__);
      {
        std::vector<local_scalar_t__> sigma_exp_flat__;
        current_statement__ = 1;
        sigma_exp_flat__ = context__.vals_r("sigma_exp");
        pos__ = 1;
        for (int sym1__ = 1; sym1__ <= N_phases; ++sym1__) {
          stan::model::assign(sigma_exp, sigma_exp_flat__[(pos__ - 1)],
            "assigning variable sigma_exp", stan::model::index_uni(sym1__));
          pos__ = (pos__ + 1);
        }
      }
      out__.write_free_lb(0, sigma_exp);
      Eigen::Matrix<local_scalar_t__,-1,1> phase_mu =
        Eigen::Matrix<local_scalar_t__,-1,1>::Constant(N_phases, DUMMY_VAR__);
      {
        std::vector<local_scalar_t__> phase_mu_flat__;
        current_statement__ = 2;
        phase_mu_flat__ = context__.vals_r("phase_mu");
        pos__ = 1;
        for (int sym1__ = 1; sym1__ <= N_phases; ++sym1__) {
          stan::model::assign(phase_mu, phase_mu_flat__[(pos__ - 1)],
            "assigning variable phase_mu", stan::model::index_uni(sym1__));
          pos__ = (pos__ + 1);
        }
      }
      out__.write_free_lb(0, phase_mu);
    } catch (const std::exception& e) {
      stan::lang::rethrow_located(e, locations_array__[current_statement__]);
    }
  }
  inline void
  get_param_names(std::vector<std::string>& names__, const bool
                  emit_transformed_parameters__ = true, const bool
                  emit_generated_quantities__ = true) const {
    names__ = std::vector<std::string>{"sigma_exp", "phase_mu"};
    if (emit_transformed_parameters__) {}
    if (emit_generated_quantities__) {}
  }
  inline void
  get_dims(std::vector<std::vector<size_t>>& dimss__, const bool
           emit_transformed_parameters__ = true, const bool
           emit_generated_quantities__ = true) const {
    dimss__ = std::vector<std::vector<size_t>>{std::vector<size_t>{static_cast<
                                                                    size_t>(
                                                                    N_phases)},
                std::vector<size_t>{static_cast<size_t>(N_phases)}};
    if (emit_transformed_parameters__) {}
    if (emit_generated_quantities__) {}
  }
  inline void
  constrained_param_names(std::vector<std::string>& param_names__, bool
                          emit_transformed_parameters__ = true, bool
                          emit_generated_quantities__ = true) const final {
    for (int sym1__ = 1; sym1__ <= N_phases; ++sym1__) {
      param_names__.emplace_back(std::string() + "sigma_exp" + '.' +
        std::to_string(sym1__));
    }
    for (int sym1__ = 1; sym1__ <= N_phases; ++sym1__) {
      param_names__.emplace_back(std::string() + "phase_mu" + '.' +
        std::to_string(sym1__));
    }
    if (emit_transformed_parameters__) {}
    if (emit_generated_quantities__) {}
  }
  inline void
  unconstrained_param_names(std::vector<std::string>& param_names__, bool
                            emit_transformed_parameters__ = true, bool
                            emit_generated_quantities__ = true) const final {
    for (int sym1__ = 1; sym1__ <= N_phases; ++sym1__) {
      param_names__.emplace_back(std::string() + "sigma_exp" + '.' +
        std::to_string(sym1__));
    }
    for (int sym1__ = 1; sym1__ <= N_phases; ++sym1__) {
      param_names__.emplace_back(std::string() + "phase_mu" + '.' +
        std::to_string(sym1__));
    }
    if (emit_transformed_parameters__) {}
    if (emit_generated_quantities__) {}
  }
  inline std::string get_constrained_sizedtypes() const {
    return std::string("[{\"name\":\"sigma_exp\",\"type\":{\"name\":\"vector\",\"length\":" + std::to_string(N_phases) + "},\"block\":\"parameters\"},{\"name\":\"phase_mu\",\"type\":{\"name\":\"vector\",\"length\":" + std::to_string(N_phases) + "},\"block\":\"parameters\"}]");
  }
  inline std::string get_unconstrained_sizedtypes() const {
    return std::string("[{\"name\":\"sigma_exp\",\"type\":{\"name\":\"vector\",\"length\":" + std::to_string(N_phases) + "},\"block\":\"parameters\"},{\"name\":\"phase_mu\",\"type\":{\"name\":\"vector\",\"length\":" + std::to_string(N_phases) + "},\"block\":\"parameters\"}]");
  }
  // Begin method overload boilerplate
  template <typename RNG> inline void
  write_array(RNG& base_rng, Eigen::Matrix<double,-1,1>& params_r,
              Eigen::Matrix<double,-1,1>& vars, const bool
              emit_transformed_parameters = true, const bool
              emit_generated_quantities = true, std::ostream*
              pstream = nullptr) const {
    const size_t num_params__ = (N_phases + N_phases);
    const size_t num_transformed = emit_transformed_parameters * (0);
    const size_t num_gen_quantities = emit_generated_quantities * (0);
    const size_t num_to_write = num_params__ + num_transformed +
      num_gen_quantities;
    std::vector<int> params_i;
    vars = Eigen::Matrix<double,-1,1>::Constant(num_to_write,
             std::numeric_limits<double>::quiet_NaN());
    write_array_impl(base_rng, params_r, params_i, vars,
      emit_transformed_parameters, emit_generated_quantities, pstream);
  }
  template <typename RNG> inline void
  write_array(RNG& base_rng, std::vector<double>& params_r, std::vector<int>&
              params_i, std::vector<double>& vars, bool
              emit_transformed_parameters = true, bool
              emit_generated_quantities = true, std::ostream*
              pstream = nullptr) const {
    const size_t num_params__ = (N_phases + N_phases);
    const size_t num_transformed = emit_transformed_parameters * (0);
    const size_t num_gen_quantities = emit_generated_quantities * (0);
    const size_t num_to_write = num_params__ + num_transformed +
      num_gen_quantities;
    vars = std::vector<double>(num_to_write,
             std::numeric_limits<double>::quiet_NaN());
    write_array_impl(base_rng, params_r, params_i, vars,
      emit_transformed_parameters, emit_generated_quantities, pstream);
  }
  template <bool propto__, bool jacobian__, typename T_> inline T_
  log_prob(Eigen::Matrix<T_,-1,1>& params_r, std::ostream* pstream = nullptr) const {
    Eigen::Matrix<int,-1,1> params_i;
    return log_prob_impl<propto__, jacobian__>(params_r, params_i, pstream);
  }
  template <bool propto__, bool jacobian__, typename T_> inline T_
  log_prob(std::vector<T_>& params_r, std::vector<int>& params_i,
           std::ostream* pstream = nullptr) const {
    return log_prob_impl<propto__, jacobian__>(params_r, params_i, pstream);
  }
  inline void
  transform_inits(const stan::io::var_context& context,
                  Eigen::Matrix<double,-1,1>& params_r, std::ostream*
                  pstream = nullptr) const final {
    std::vector<double> params_r_vec(params_r.size());
    std::vector<int> params_i;
    transform_inits(context, params_i, params_r_vec, pstream);
    params_r = Eigen::Map<Eigen::Matrix<double,-1,1>>(params_r_vec.data(),
                 params_r_vec.size());
  }
  inline void
  transform_inits(const stan::io::var_context& context, std::vector<int>&
                  params_i, std::vector<double>& vars, std::ostream*
                  pstream__ = nullptr) const {
    vars.resize(num_params_r__);
    transform_inits_impl(context, vars, pstream__);
  }
  inline void
  unconstrain_array(const std::vector<double>& params_constrained,
                    std::vector<double>& params_unconstrained, std::ostream*
                    pstream = nullptr) const {
    const std::vector<int> params_i;
    params_unconstrained = std::vector<double>(num_params_r__,
                             std::numeric_limits<double>::quiet_NaN());
    unconstrain_array_impl(params_constrained, params_i,
      params_unconstrained, pstream);
  }
  inline void
  unconstrain_array(const Eigen::Matrix<double,-1,1>& params_constrained,
                    Eigen::Matrix<double,-1,1>& params_unconstrained,
                    std::ostream* pstream = nullptr) const {
    const std::vector<int> params_i;
    params_unconstrained = Eigen::Matrix<double,-1,1>::Constant(num_params_r__,
                             std::numeric_limits<double>::quiet_NaN());
    unconstrain_array_impl(params_constrained, params_i,
      params_unconstrained, pstream);
  }
};
}
using stan_model = one_sample_model_namespace::one_sample_model;
#ifndef USING_R
// Boilerplate
stan::model::model_base&
new_model(stan::io::var_context& data_context, unsigned int seed,
          std::ostream* msg_stream) {
  stan_model* m = new stan_model(data_context, seed, msg_stream);
  return *m;
}
stan::math::profile_map& get_stan_profile_data() {
  return one_sample_model_namespace::profiles__;
}
#endif