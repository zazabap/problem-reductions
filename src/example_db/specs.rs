//! Shared example specification types and helper functions.
//!
//! These types describe canonical model and rule examples with metadata
//! that can be validated against the catalog and reduction registry.

use crate::export::{ModelExample, ProblemSide, RuleExample, SampleEval, SolutionPair};
use crate::models::algebraic::{VariableDomain, ILP};
use crate::prelude::{OptimizationProblem, Problem, ReduceTo, ReductionResult};
use crate::solvers::{BruteForce, ILPSolver};
use serde::Serialize;

/// Specification for a canonical model example.
#[allow(dead_code)]
pub struct ModelExampleSpec {
    /// Unique example identifier.
    pub id: &'static str,
    /// Builder function that produces the full exported example.
    pub build: fn() -> ModelExample,
}

/// Specification for a canonical rule example.
#[allow(dead_code)]
pub struct RuleExampleSpec {
    /// Unique example identifier.
    pub id: &'static str,
    /// Builder function that produces the full exported example.
    pub build: fn() -> RuleExample,
}

// ---- Model example helpers ----

pub fn sample_eval<P>(problem: &P, config: Vec<usize>) -> SampleEval
where
    P: Problem,
    P::Metric: Serialize,
{
    let metric =
        serde_json::to_value(problem.evaluate(&config)).expect("Failed to serialize metric");
    SampleEval { config, metric }
}

pub fn optimization_example<P>(problem: P, samples: Vec<Vec<usize>>) -> ModelExample
where
    P: OptimizationProblem + Serialize,
    P::Metric: Serialize,
{
    let sample_evals = samples
        .into_iter()
        .map(|config| sample_eval(&problem, config))
        .collect();
    let optimal = BruteForce::new()
        .find_all_best(&problem)
        .into_iter()
        .map(|config| sample_eval(&problem, config))
        .collect();
    ModelExample::from_problem(&problem, sample_evals, optimal)
}

pub fn satisfaction_example<P>(problem: P, samples: Vec<Vec<usize>>) -> ModelExample
where
    P: Problem<Metric = bool> + Serialize,
{
    let sample_evals = samples
        .into_iter()
        .map(|config| sample_eval(&problem, config))
        .collect();
    let satisfying = BruteForce::new()
        .find_all_satisfying(&problem)
        .into_iter()
        .map(|config| sample_eval(&problem, config))
        .collect();
    ModelExample::from_problem(&problem, sample_evals, satisfying)
}

pub fn explicit_example<P>(
    problem: P,
    samples: Vec<Vec<usize>>,
    optimal_configs: Vec<Vec<usize>>,
) -> ModelExample
where
    P: Problem + Serialize,
    P::Metric: Serialize,
{
    let sample_evals = samples
        .into_iter()
        .map(|config| sample_eval(&problem, config))
        .collect();
    let optimal = optimal_configs
        .into_iter()
        .map(|config| sample_eval(&problem, config))
        .collect();
    ModelExample::from_problem(&problem, sample_evals, optimal)
}

// ---- Rule example helpers ----

pub fn assemble_rule_example<S, T>(
    source: &S,
    target: &T,
    solutions: Vec<SolutionPair>,
) -> RuleExample
where
    S: Problem + Serialize,
    T: Problem + Serialize,
{
    RuleExample {
        source: ProblemSide::from_problem(source),
        target: ProblemSide::from_problem(target),
        solutions,
    }
}

pub fn direct_best_example<S, T, Keep>(source: S, keep: Keep) -> RuleExample
where
    S: Problem + Serialize + ReduceTo<T>,
    T: OptimizationProblem + Serialize,
    T::Metric: Serialize,
    Keep: Fn(&S, &[usize]) -> bool,
{
    let reduction = ReduceTo::<T>::reduce_to(&source);
    let target = reduction.target_problem();
    let solutions = BruteForce::new()
        .find_all_best(target)
        .into_iter()
        .filter_map(|target_config| {
            let source_config = reduction.extract_solution(&target_config);
            keep(&source, &source_config).then_some(SolutionPair {
                source_config,
                target_config,
            })
        })
        .collect();
    assemble_rule_example(&source, target, solutions)
}

pub fn direct_satisfying_example<S, T, Keep>(source: S, keep: Keep) -> RuleExample
where
    S: Problem + Serialize + ReduceTo<T>,
    T: Problem<Metric = bool> + Serialize,
    Keep: Fn(&S, &[usize]) -> bool,
{
    let reduction = ReduceTo::<T>::reduce_to(&source);
    let target = reduction.target_problem();
    let solutions = BruteForce::new()
        .find_all_satisfying(target)
        .into_iter()
        .filter_map(|target_config| {
            let source_config = reduction.extract_solution(&target_config);
            keep(&source, &source_config).then_some(SolutionPair {
                source_config,
                target_config,
            })
        })
        .collect();
    assemble_rule_example(&source, target, solutions)
}

pub fn direct_ilp_example<S, V, Keep>(source: S, keep: Keep) -> RuleExample
where
    S: Problem + Serialize + ReduceTo<ILP<V>>,
    ILP<V>: Serialize,
    V: VariableDomain,
    Keep: Fn(&S, &[usize]) -> bool,
{
    let reduction = ReduceTo::<ILP<V>>::reduce_to(&source);
    let target = reduction.target_problem();
    let target_config = ILPSolver::new()
        .solve(target)
        .expect("canonical ILP target example should solve");
    let source_config = reduction.extract_solution(&target_config);
    let solutions = if keep(&source, &source_config) {
        vec![SolutionPair {
            source_config,
            target_config,
        }]
    } else {
        Vec::new()
    };
    assemble_rule_example(&source, target, solutions)
}

pub fn keep_bool_source<S>(source: &S, config: &[usize]) -> bool
where
    S: Problem<Metric = bool>,
{
    source.evaluate(config)
}
