use crate::registry::{FieldInfo, ProblemSchemaEntry};
use crate::topology::BipartiteGraph;
use crate::traits::{Problem, SatisfactionProblem};
use serde::{Deserialize, Serialize};

inventory::submit! {
    ProblemSchemaEntry {
        name: "BalancedCompleteBipartiteSubgraph",
        display_name: "Balanced Complete Bipartite Subgraph",
        aliases: &[],
        dimensions: &[],
        module_path: module_path!(),
        description: "Decide whether a bipartite graph contains a K_{k,k} subgraph",
        fields: &[
            FieldInfo { name: "graph", type_name: "BipartiteGraph", description: "The bipartite graph G = (A, B, E)" },
            FieldInfo { name: "k", type_name: "usize", description: "Balanced biclique size" },
        ],
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BalancedCompleteBipartiteSubgraph {
    graph: BipartiteGraph,
    k: usize,
}

impl BalancedCompleteBipartiteSubgraph {
    pub fn new(graph: BipartiteGraph, k: usize) -> Self {
        Self { graph, k }
    }

    pub fn graph(&self) -> &BipartiteGraph {
        &self.graph
    }

    pub fn left_size(&self) -> usize {
        self.graph.left_size()
    }

    pub fn right_size(&self) -> usize {
        self.graph.right_size()
    }

    pub fn num_vertices(&self) -> usize {
        self.left_size() + self.right_size()
    }

    pub fn num_edges(&self) -> usize {
        self.graph.left_edges().len()
    }

    pub fn k(&self) -> usize {
        self.k
    }

    fn selected_vertices(&self, config: &[usize]) -> Option<(Vec<usize>, Vec<usize>)> {
        if config.len() != self.num_vertices() {
            return None;
        }

        let mut selected_left = Vec::new();
        let mut selected_right = Vec::new();

        for (index, &value) in config.iter().enumerate() {
            match value {
                0 => {}
                1 => {
                    if index < self.left_size() {
                        selected_left.push(index);
                    } else {
                        selected_right.push(index - self.left_size());
                    }
                }
                _ => return None,
            }
        }

        Some((selected_left, selected_right))
    }

    pub fn is_valid_solution(&self, config: &[usize]) -> bool {
        self.evaluate(config)
    }
}

impl Problem for BalancedCompleteBipartiteSubgraph {
    const NAME: &'static str = "BalancedCompleteBipartiteSubgraph";
    type Metric = bool;

    fn dims(&self) -> Vec<usize> {
        vec![2; self.num_vertices()]
    }

    fn evaluate(&self, config: &[usize]) -> bool {
        let Some((selected_left, selected_right)) = self.selected_vertices(config) else {
            return false;
        };

        if selected_left.len() != self.k || selected_right.len() != self.k {
            return false;
        }

        selected_left.iter().all(|&left| {
            selected_right
                .iter()
                .all(|&right| self.graph.left_edges().contains(&(left, right)))
        })
    }

    fn variant() -> Vec<(&'static str, &'static str)> {
        crate::variant_params![]
    }
}

impl SatisfactionProblem for BalancedCompleteBipartiteSubgraph {}

crate::declare_variants! {
    default sat BalancedCompleteBipartiteSubgraph => "2^num_vertices",
}

#[cfg(feature = "example-db")]
pub(crate) fn canonical_model_example_specs() -> Vec<crate::example_db::specs::ModelExampleSpec> {
    vec![crate::example_db::specs::ModelExampleSpec {
        id: "balanced_complete_bipartite_subgraph",
        build: || {
            let problem = BalancedCompleteBipartiteSubgraph::new(
                BipartiteGraph::new(
                    4,
                    4,
                    vec![
                        (0, 0),
                        (0, 1),
                        (0, 2),
                        (1, 0),
                        (1, 1),
                        (1, 2),
                        (2, 0),
                        (2, 1),
                        (2, 2),
                        (3, 0),
                        (3, 1),
                        (3, 3),
                    ],
                ),
                3,
            );

            crate::example_db::specs::satisfaction_example(
                problem,
                vec![vec![1, 1, 1, 0, 1, 1, 1, 0]],
            )
        },
    }]
}

#[cfg(test)]
#[path = "../../unit_tests/models/graph/balanced_complete_bipartite_subgraph.rs"]
mod tests;
