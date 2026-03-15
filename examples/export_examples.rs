use problemreductions::example_db::{build_example_db, default_generated_dir};
use problemreductions::export::write_example_db_to;
use std::fs;

fn main() {
    let output_dir = default_generated_dir();
    if output_dir.exists() {
        fs::remove_dir_all(&output_dir).expect("Failed to clear generated examples directory");
    }
    fs::create_dir_all(&output_dir).expect("Failed to create generated examples directory");

    let example_db = build_example_db().expect("Failed to build canonical example database");

    write_example_db_to(&output_dir, &example_db);

    println!(
        "Exported {} rule examples and {} model examples",
        example_db.rules.len(),
        example_db.models.len()
    );
}
