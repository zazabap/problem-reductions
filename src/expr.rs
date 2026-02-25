//! General symbolic expression AST for reduction overhead.

use crate::types::ProblemSize;

/// A symbolic math expression over problem size variables.
#[derive(Clone, Debug, PartialEq, serde::Serialize, serde::Deserialize)]
pub enum Expr {
    /// Numeric constant.
    Const(f64),
    /// Named variable (e.g., "num_vertices").
    Var(&'static str),
    /// Addition: a + b.
    Add(Box<Expr>, Box<Expr>),
    /// Multiplication: a * b.
    Mul(Box<Expr>, Box<Expr>),
    /// Exponentiation: base ^ exponent.
    Pow(Box<Expr>, Box<Expr>),
    /// Exponential function: exp(a).
    Exp(Box<Expr>),
    /// Natural logarithm: log(a).
    Log(Box<Expr>),
    /// Square root: sqrt(a).
    Sqrt(Box<Expr>),
}

impl Expr {
    /// Convenience constructor for addition.
    pub fn add(a: Expr, b: Expr) -> Self {
        Expr::Add(Box::new(a), Box::new(b))
    }

    /// Convenience constructor for multiplication.
    pub fn mul(a: Expr, b: Expr) -> Self {
        Expr::Mul(Box::new(a), Box::new(b))
    }

    /// Convenience constructor for exponentiation.
    pub fn pow(base: Expr, exp: Expr) -> Self {
        Expr::Pow(Box::new(base), Box::new(exp))
    }

    /// Evaluate the expression given concrete variable values.
    pub fn eval(&self, vars: &ProblemSize) -> f64 {
        match self {
            Expr::Const(c) => *c,
            Expr::Var(name) => vars.get(name).unwrap_or(0) as f64,
            Expr::Add(a, b) => a.eval(vars) + b.eval(vars),
            Expr::Mul(a, b) => a.eval(vars) * b.eval(vars),
            Expr::Pow(base, exp) => base.eval(vars).powf(exp.eval(vars)),
            Expr::Exp(a) => a.eval(vars).exp(),
            Expr::Log(a) => a.eval(vars).ln(),
            Expr::Sqrt(a) => a.eval(vars).sqrt(),
        }
    }
}

#[cfg(test)]
#[path = "unit_tests/expr.rs"]
mod tests;
