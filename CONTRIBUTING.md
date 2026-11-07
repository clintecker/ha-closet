# Contributing

Use `nix develop` and `just check`. The default Cargo target is the service;
`cargo run --bin ha-closet -- --help` runs the client. Keep the API and CLI on
the same owned Rust types.

Tests should exercise real HTTP, SQLite, CLI, Home Assistant and visible UI
behavior. Cover invalid input, revision conflicts, uncertain retries, restart
and cleanup. Do not add source-snippet tests or weaken checks to merge updates.
Run EXPLAIN on actual changed queries with representative disposable data.

Use fictional catalogs and screenshots. Never add your own wardrobe, receipts,
private source URLs, credentials or household configuration, even temporarily.
The public-tree check scans reachable Git history as well as current files.

Version changes must agree across Cargo, the HA manifest and app metadata.
Release only after required checks pass on the exact head. Container smoke
checks cover both architectures and restore a backup into a fresh instance.
