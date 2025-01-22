# Changelog

## [0.3.1] - 2024-01-22

### Fixed
- Fixed a bug in `MemoryStateStorage` affecting the functionality of `set_data`, `get_data`, `update_data`, and `clear_data`, ensuring proper data handling and consistency.

---

## [0.3.0] - 2024-01-21

### Added
- New `FileStateStorage` class for storing states in files

### Changed
- Converted all async methods in `MemoryStateStorage` to synchronous
- Separated user data storage from state storage, using different cache keys for states and data
