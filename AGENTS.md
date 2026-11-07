# Closet

Keep the app small. Rust owns the catalog types, validation, sync and Today
state. The JSON catalog is authoritative; Home Assistant is a projection.
Use Nix and `just check`. Test real HTTP, SQLite, CLI and HA behavior.
Keep credentials, personal catalogs, source photographs and household details
out of source, examples, screenshots, logs and public build output. Examples
must be fictional. No production unwraps or panics. Preserve lifecycle cleanup.
The README is for people: short, practical and inventory-first. Today is an
optional experiment, not the main product or a styling promise.
