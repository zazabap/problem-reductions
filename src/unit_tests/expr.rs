use super::*;
use crate::types::ProblemSize;

#[test]
fn test_expr_const_eval() {
    let e = Expr::Const(42.0);
    let size = ProblemSize::new(vec![]);
    assert_eq!(e.eval(&size), 42.0);
}

#[test]
fn test_expr_var_eval() {
    let e = Expr::Var("n");
    let size = ProblemSize::new(vec![("n", 10)]);
    assert_eq!(e.eval(&size), 10.0);
}

#[test]
fn test_expr_add_eval() {
    // n + 3
    let e = Expr::add(Expr::Var("n"), Expr::Const(3.0));
    let size = ProblemSize::new(vec![("n", 7)]);
    assert_eq!(e.eval(&size), 10.0);
}

#[test]
fn test_expr_mul_eval() {
    // 3 * n
    let e = Expr::mul(Expr::Const(3.0), Expr::Var("n"));
    let size = ProblemSize::new(vec![("n", 5)]);
    assert_eq!(e.eval(&size), 15.0);
}

#[test]
fn test_expr_pow_eval() {
    // n^2
    let e = Expr::pow(Expr::Var("n"), Expr::Const(2.0));
    let size = ProblemSize::new(vec![("n", 4)]);
    assert_eq!(e.eval(&size), 16.0);
}

#[test]
fn test_expr_exp_eval() {
    let e = Expr::Exp(Box::new(Expr::Const(1.0)));
    let size = ProblemSize::new(vec![]);
    assert!((e.eval(&size) - std::f64::consts::E).abs() < 1e-10);
}

#[test]
fn test_expr_log_eval() {
    let e = Expr::Log(Box::new(Expr::Const(std::f64::consts::E)));
    let size = ProblemSize::new(vec![]);
    assert!((e.eval(&size) - 1.0).abs() < 1e-10);
}

#[test]
fn test_expr_sqrt_eval() {
    let e = Expr::Sqrt(Box::new(Expr::Const(9.0)));
    let size = ProblemSize::new(vec![]);
    assert_eq!(e.eval(&size), 3.0);
}

#[test]
fn test_expr_complex() {
    // n^2 + 3*m
    let e = Expr::add(
        Expr::pow(Expr::Var("n"), Expr::Const(2.0)),
        Expr::mul(Expr::Const(3.0), Expr::Var("m")),
    );
    let size = ProblemSize::new(vec![("n", 4), ("m", 2)]);
    assert_eq!(e.eval(&size), 22.0); // 16 + 6
}
