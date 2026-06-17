# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

- Added inward/outward analytics dashboards with stock health, timing, vendor mix, and gas-type charts.
- Rebuilt the inward/outward report as an intelligence view with KPI cards, charts, insights, and a detailed ledger.
- Improved inward/outward stock-in and stock-out backend validation with clearer frontend error messages.
- Added regression tests for cylinder analytics and stock workflow actions.
- Replaced plaintext login checks with Django password hashing and session key rotation.
- Added middleware to protect QR routes and auto logout expired sessions.
- Updated security settings, authentication tests, and dependency pins after vulnerability scans.
- Updated the UI theme to match the Cylinder Master teal, graphite, and green login background palette.
- Rebuilt the login page with a Next.js-inspired auth card and stronger logo contrast.
- Updated Cylinder Master logo assets to use the full logo with a softened transparent white background.
- Rebranded remaining legacy UI references to Cylinder Master.
- Replaced legacy login and navigation branding images with generated Cylinder Master assets.
- Explicitly defined the project as the Gas Cylinder Scanner in app metadata, admin metadata, model names, and docs.
- Added migration-managed seed data for `Cylinder_Type_Master`.
- Added a seed-data regression test and workflow documentation.
- Added GitHub-ready project documentation.
- Added environment variable example file.
- Added ignore rules for local secrets, databases, virtual environments, and generated Python files.
