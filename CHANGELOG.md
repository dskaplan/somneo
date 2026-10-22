# Changelog

All notable changes to this project will be documented in this file.

## 0.2.0 - 2026-10-22

- Make scan interval configurable via options (config entry `scan_interval`, seconds, default 10)
- Upgrade to the async pysomneo 6.0.0; the coordinator and config flow no longer use executor threads
- Close the pysomneo connection on unload
- Remove the "reuse TLS connections" option, pysomneo now always keeps a single connection
- Update human-facing project name and documentation links

## 0.1.0 - Initial

- Initial fork and minimal integration exposing wake-up/light/audio controls for Philips Somneo HF367x
