# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Backend**: Stabilized the test suite by reconfiguring the test database setup. This resolves intermittent `InterfaceError` and `SAWarning` connection issues by ensuring each test runs in a fully isolated, function-scoped database transaction with a dedicated engine.
- **Frontend**: Resolved CI/CD pipeline failures for `frontend-tests` and `docker-build`.
  - Downgraded `jsdom` to version `22.1.0` to fix `ERR_REQUIRE_ESM` module compatibility errors.
  - Downgraded `tailwindcss` from v4 to v3 to fix native binding installation errors (`@tailwindcss/oxide`) and PostCSS parsing errors during the build process.
  - Updated `vite.config.ts` and `index.css` to match the Tailwind CSS v3 configuration.