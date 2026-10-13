Contributing
============

Thanks for considering contributing to Simple Somneo (this repository).

How to contribute

- Fork the repository and open a pull request with a clear description of the changes.
- Run and add tests using `pytest` and `pytest-homeassistant-custom-component`.
- Follow Home Assistant developer guidance for integrations:
  - Use a shared DataUpdateCoordinator for polling-based integrations.
  - Provide stable `unique_id` values for entities and test registry migrations.
  - Implement async_unload_entry, config-flow and options-flow when appropriate.

Running tests (local)

This project uses pytest and pytest-homeassistant-custom-component. To run tests locally:

1. Create a virtualenv with Python 3.11+.
2. Install dev/test dependencies:
   pip install -e .
   pip install pytest pytest-homeassistant-custom-component
3. Run pytest

Contact

If you find bugs or want to request features, please open an issue at the repository issue tracker.
