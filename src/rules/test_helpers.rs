use crate::rules::{ReductionChain, ReductionResult};
use crate::solvers::{BruteForce, Solver};
use crate::traits::{OptimizationProblem, Problem, SatisfactionProblem};
use std::collections::HashSet;

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
    let solver = BruteForce::new();
    let target_solutions = solver.find_all_best(reduction.target_problem());
    assert!(
        !target_solutions.is_empty(),
        "{context}: target solver found no optimal solutions"
    );

    let reference_solutions: HashSet<Vec<usize>> = solver.find_all_best(source).into_iter().collect();
    assert!(
        !reference_solutions.is_empty(),
        "{context}: direct source solver found no optimal solutions"
    );

    let reference_metric = source
        .evaluate(reference_solutions.iter().next().expect("reference set is non-empty"));
    let extracted: HashSet<Vec<usize>> = target_solutions
        .iter()
        .map(|target_solution| reduction.extract_solution(target_solution))
        .collect();
    assert!(!extracted.is_empty(), "{context}: no extracted source solutions");
    assert!(
        extracted.is_subset(&reference_solutions),
        "{context}: extracted source solutions are not all directly optimal"
    );
    for source_solution in &extracted {
        let extracted_metric = source.evaluate(source_solution);
        assert!(
            extracted_metric.is_valid(),
            "{context}: extracted source solution is infeasible: {:?}",
            source_solution
        );
        assert_eq!(
            extracted_metric, reference_metric,
            "{context}: extracted source objective does not match direct solve"
        );
    }
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
    let solver = BruteForce::new();
    let target_solutions = solver.find_all_satisfying(reduction.target_problem());
    assert!(
        !target_solutions.is_empty(),
        "{context}: target solver found no satisfying solutions"
    );

    let reference_solutions: HashSet<Vec<usize>> = solver.find_all_best(source).into_iter().collect();
    assert!(
        !reference_solutions.is_empty(),
        "{context}: direct source solver found no optimal solutions"
    );

    let reference_metric = source
        .evaluate(reference_solutions.iter().next().expect("reference set is non-empty"));
    let extracted: HashSet<Vec<usize>> = target_solutions
        .iter()
        .map(|target_solution| reduction.extract_solution(target_solution))
        .collect();
    assert!(!extracted.is_empty(), "{context}: no extracted source solutions");
    assert!(
        extracted.is_subset(&reference_solutions),
        "{context}: extracted source solutions are not all directly optimal"
    );
    for source_solution in &extracted {
        let extracted_metric = source.evaluate(source_solution);
        assert!(
            extracted_metric.is_valid(),
            "{context}: extracted source solution is infeasible: {:?}",
            source_solution
        );
        assert_eq!(
            extracted_metric, reference_metric,
            "{context}: extracted source objective does not match direct solve"
        );
    }
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
    let solver = BruteForce::new();
    let target_solutions = solver.find_all_best(chain.target_problem::<Target>());
    assert!(
        !target_solutions.is_empty(),
        "{context}: target solver found no optimal solutions"
    );

    let reference_solutions: HashSet<Vec<usize>> = solver.find_all_best(source).into_iter().collect();
    assert!(
        !reference_solutions.is_empty(),
        "{context}: direct source solver found no optimal solutions"
    );

    let reference_metric = source
        .evaluate(reference_solutions.iter().next().expect("reference set is non-empty"));
    let extracted: HashSet<Vec<usize>> = target_solutions
        .iter()
        .map(|target_solution| chain.extract_solution(target_solution))
        .collect();
    assert!(!extracted.is_empty(), "{context}: no extracted source solutions");
    assert!(
        extracted.is_subset(&reference_solutions),
        "{context}: extracted source solutions are not all directly optimal"
    );
    for source_solution in &extracted {
        let extracted_metric = source.evaluate(source_solution);
        assert!(
            extracted_metric.is_valid(),
            "{context}: extracted source solution is infeasible: {:?}",
            source_solution
        );
        assert_eq!(
            extracted_metric, reference_metric,
            "{context}: extracted source objective does not match direct solve"
        );
    }
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
    let target_solutions = BruteForce::new().find_all_best(reduction.target_problem());
    assert!(
        !target_solutions.is_empty(),
        "{context}: target solver found no optimal solutions"
    );
    let extracted: HashSet<Vec<usize>> = target_solutions
        .iter()
        .map(|target_solution| reduction.extract_solution(target_solution))
        .collect();
    assert!(!extracted.is_empty(), "{context}: no extracted source solutions");
    for source_solution in &extracted {
        assert!(
            source.evaluate(source_solution),
            "{context}: extracted source solution is not satisfying: {:?}",
            source_solution
        );
    }
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
    let target_solutions = BruteForce::new().find_all_satisfying(reduction.target_problem());
    assert!(
        !target_solutions.is_empty(),
        "{context}: target solver found no satisfying solutions"
    );
    let extracted: HashSet<Vec<usize>> = target_solutions
        .iter()
        .map(|target_solution| reduction.extract_solution(target_solution))
        .collect();
    assert!(!extracted.is_empty(), "{context}: no extracted source solutions");
    for source_solution in &extracted {
        assert!(
            source.evaluate(source_solution),
            "{context}: extracted source solution is not satisfying: {:?}",
            source_solution
        );
    }
}

pub(crate) fn solve_optimization_problem<P>(problem: &P) -> Option<Vec<usize>>
where
    P: OptimizationProblem + 'static,
{
    BruteForce::new().find_best(problem)
}

pub(crate) fn solve_satisfaction_problem<P>(problem: &P) -> Option<Vec<usize>>
where
    P: SatisfactionProblem + 'static,
{
    BruteForce::new().find_satisfying(problem)
}
