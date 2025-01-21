# Changelog

## [0.4.0] - 2024-01-21

### Added
- New `FileStateStorage` class for storing states in files

### Changed
- Converted all async methods in `MemoryStateStorage` to synchronous
- Separated user data storage from state storage, using different cache keys for states and data
