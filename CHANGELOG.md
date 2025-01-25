# Changelog

## [0.3.3] - 2025-01-25

### Added
- **New async classes**:
  - `AsyncFileStateStorage`
  - `AsyncMemoryStateStorage`
  - `AsyncRedisStateStorage`  
  These classes provide full asynchronous (async) support for state storage.

- **`ex` argument** added to `set_state`, `set_data`, and `update_data` methods:
  - The `ex` argument is now supported in `RedisStateStorage` and `AsyncRedisStateStorage` for setting expiry time.

### Changed
- `FileStateStorage`, `MemoryStateStorage`, and `RedisStateStorage` are now **synchronous (sync)** only.
  
- **RedisStateStorage and AsyncRedisStateStorage constructor update**:
  - The constructor for both classes now accepts additional parameters: `host`, `port`, `db`, and `password`. The `ex` argument was also updated to be optional for expiry handling.

### Improved
- **Serialization update**: Switched from `json` to `msgspec` for data handling:
  - Reduced memory usage.
  - Increased performance.

---

## [0.3.2] - 2024-01-23

### Changed
- Renamed the `clear_data` method to `delete_data` in `MemoryStateStorage`, `FileStateStorage`, and `RedisStateStorage`.

### Added
- `delete_data` now deletes and returns the deleted data.
- Added a new `default` argument to `delete_data`. If the data doesn't exist, the `default` value will be returned.

---

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
