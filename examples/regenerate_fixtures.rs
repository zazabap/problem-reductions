/// Regenerate example database fixture files from builder code.
///
/// This binary recomputes all model and rule examples using BruteForce/ILP
/// and writes them to `src/example_db/fixtures/` as JSON Lines, one example per
/// line. Run this in release mode after changing any model or rule to update
/// the stored expected results:
///
/// ```
/// cargo run --release --example regenerate_fixtures --features example-db
/// ```
use problemreductions::example_db::{compute_model_db, compute_rule_db};
use problemreductions::export::{write_model_db_to, write_rule_db_to};
use std::fs;
use std::path::Path;

fn main() {
    let fixtures_dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("src/example_db/fixtures");
    fs::create_dir_all(&fixtures_dir).expect("Failed to create fixtures directory");

    let rule_db = compute_rule_db().expect("Failed to compute canonical rule database");
    let model_db = compute_model_db().expect("Failed to compute canonical model database");

    let models_path = fixtures_dir.join("models.json");
    let rules_path = fixtures_dir.join("rules.json");

    write_model_db_to(&fixtures_dir, &model_db);
    write_rule_db_to(&fixtures_dir, &rule_db);

    println!(
        "Regenerated fixtures: {} rule examples, {} model examples",
        rule_db.rules.len(),
        model_db.models.len()
    );
    println!("  Models: {}", models_path.display());
    println!("  Rules: {}", rules_path.display());
}
