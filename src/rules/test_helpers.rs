use crate::models::algebraic::ILP;
use crate::rules::{MinimizeSteps, ReductionChain, ReductionGraph, ReductionResult};
use crate::solvers::{BruteForce, Solver};
use crate::traits::{OptimizationProblem, Problem, SatisfactionProblem};
use crate::types::ProblemSize;
use std::any::Any;

pub(crate) fn assert_optimization_round_trip_from_optimization_target<R>(
    source: &R::Source,
    reduction: &R,
    context: &str,
) where
    R: ReductionResult,
    R::Source: OptimizationProblem + 'static,
    R::Target: OptimizationProblem + 'static,
    <R::Source as OptimizationProblem>::Value: std::fmt::Debug + PartialEq,
    <R::Source as Problem>::Metric: std::fmt::Debug + PartialEq,
{
    let target_solution = solve_optimization_problem(reduction.target_problem())
        .unwrap_or_else(|| panic!("{context}: target solver found no optimal solution"));
    let extracted = reduction.extract_solution(&target_solution);
    let extracted_metric = source.evaluate(&extracted);
    assert!(
        extracted_metric.is_valid(),
        "{context}: extracted source solution is infeasible: {:?}",
        extracted
    );

    let reference_solution = solve_optimization_problem(source)
        .unwrap_or_else(|| panic!("{context}: direct source solver found no optimal solution"));
    let reference_metric = source.evaluate(&reference_solution);
    assert_eq!(
        extracted_metric, reference_metric,
        "{context}: extracted source objective does not match direct solve"
    );
}

pub(crate) fn assert_optimization_round_trip_from_satisfaction_target<R>(
    source: &R::Source,
    reduction: &R,
    context: &str,
) where
    R: ReductionResult,
    R::Source: OptimizationProblem + 'static,
    R::Target: SatisfactionProblem + 'static,
    <R::Source as OptimizationProblem>::Value: std::fmt::Debug + PartialEq,
    <R::Source as Problem>::Metric: std::fmt::Debug + PartialEq,
{
    let target_solution = solve_satisfaction_problem(reduction.target_problem())
        .unwrap_or_else(|| panic!("{context}: target solver found no satisfying solution"));
    let extracted = reduction.extract_solution(&target_solution);
    let extracted_metric = source.evaluate(&extracted);
    assert!(
        extracted_metric.is_valid(),
        "{context}: extracted source solution is infeasible: {:?}",
        extracted
    );

    let reference_solution = solve_optimization_problem(source)
        .unwrap_or_else(|| panic!("{context}: direct source solver found no optimal solution"));
    let reference_metric = source.evaluate(&reference_solution);
    assert_eq!(
        extracted_metric, reference_metric,
        "{context}: extracted source objective does not match direct solve"
    );
}

pub(crate) fn assert_optimization_round_trip_chain<Source, Target>(
    source: &Source,
    chain: &ReductionChain,
    context: &str,
) where
    Source: OptimizationProblem + 'static,
    Target: OptimizationProblem + 'static,
    <Source as OptimizationProblem>::Value: std::fmt::Debug + PartialEq,
    <Source as Problem>::Metric: std::fmt::Debug + PartialEq,
{
    let target_solution = solve_optimization_problem(chain.target_problem::<Target>())
        .unwrap_or_else(|| panic!("{context}: target solver found no optimal solution"));
    let extracted = chain.extract_solution(&target_solution);
    let extracted_metric = source.evaluate(&extracted);
    assert!(
        extracted_metric.is_valid(),
        "{context}: extracted source solution is infeasible: {:?}",
        extracted
    );

    let reference_solution = solve_optimization_problem(source)
        .unwrap_or_else(|| panic!("{context}: direct source solver found no optimal solution"));
    let reference_metric = source.evaluate(&reference_solution);
    assert_eq!(
        extracted_metric, reference_metric,
        "{context}: extracted source objective does not match direct solve"
    );
}

pub(crate) fn assert_satisfaction_round_trip_from_optimization_target<R>(
    source: &R::Source,
    reduction: &R,
    context: &str,
) where
    R: ReductionResult,
    R::Source: SatisfactionProblem + 'static,
    R::Target: OptimizationProblem + 'static,
{
    let target_solution = solve_optimization_problem(reduction.target_problem())
        .unwrap_or_else(|| panic!("{context}: target solver found no optimal solution"));
    let extracted = reduction.extract_solution(&target_solution);
    assert!(
        source.evaluate(&extracted),
        "{context}: extracted source solution is not satisfying: {:?}",
        extracted
    );
}

pub(crate) fn assert_satisfaction_round_trip_from_satisfaction_target<R>(
    source: &R::Source,
    reduction: &R,
    context: &str,
) where
    R: ReductionResult,
    R::Source: SatisfactionProblem + 'static,
    R::Target: SatisfactionProblem + 'static,
{
    let target_solution = solve_satisfaction_problem(reduction.target_problem())
        .unwrap_or_else(|| panic!("{context}: target solver found no satisfying solution"));
    let extracted = reduction.extract_solution(&target_solution);
    assert!(
        source.evaluate(&extracted),
        "{context}: extracted source solution is not satisfying: {:?}",
        extracted
    );
}

pub(crate) fn solve_optimization_problem<P>(problem: &P) -> Option<Vec<usize>>
where
    P: OptimizationProblem + 'static,
{
    try_solve_via_direct_ilp(problem).or_else(|| BruteForce::new().find_best(problem))
}

pub(crate) fn solve_satisfaction_problem<P>(problem: &P) -> Option<Vec<usize>>
where
    P: SatisfactionProblem + 'static,
{
    try_solve_via_direct_ilp(problem).or_else(|| BruteForce::new().find_satisfying(problem))
}

#[cfg(feature = "ilp-solver")]
fn try_solve_via_direct_ilp<P>(problem: &P) -> Option<Vec<usize>>
where
    P: Problem + 'static,
{
    use crate::solvers::ILPSolver;

    if let Some(ilp) = (problem as &dyn Any).downcast_ref::<ILP<bool>>() {
        return ILPSolver::new().solve(ilp);
    }
    if let Some(ilp) = (problem as &dyn Any).downcast_ref::<ILP<i32>>() {
        return ILPSolver::new().solve(ilp);
    }

    let graph = ReductionGraph::new();
    let source_variant = ReductionGraph::variant_to_map(&P::variant());
    let source_any = problem as &dyn Any;

    try_solve_via_direct_ilp_edge::<P, bool>(&graph, &source_variant, source_any)
        .or_else(|| try_solve_via_direct_ilp_edge::<P, i32>(&graph, &source_variant, source_any))
}

#[cfg(not(feature = "ilp-solver"))]
fn try_solve_via_direct_ilp<P>(_problem: &P) -> Option<Vec<usize>>
where
    P: Problem + 'static,
{
    None
}

#[cfg(feature = "ilp-solver")]
fn try_solve_via_direct_ilp_edge<P, V>(
    graph: &ReductionGraph,
    source_variant: &std::collections::BTreeMap<String, String>,
    source: &dyn Any,
) -> Option<Vec<usize>>
where
    P: Problem + 'static,
    V: crate::models::algebraic::VariableDomain,
{
    use crate::solvers::ILPSolver;

    let target_variant = ReductionGraph::variant_to_map(&ILP::<V>::variant());
    let path = graph.find_cheapest_path(
        P::NAME,
        source_variant,
        ILP::<V>::NAME,
        &target_variant,
        &ProblemSize::new(vec![]),
        &MinimizeSteps,
    )?;
    if path.len() != 1 {
        return None;
    }

    let chain = graph.reduce_along_path(&path, source)?;
    let ilp = chain.target_problem::<ILP<V>>();
    let ilp_solution = ILPSolver::new().solve(ilp)?;
    Some(chain.extract_solution(&ilp_solution))
}
