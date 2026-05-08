# Changelog

## [Unreleased]

### Added
- Add LICENSE (AGPL v3)
- Add CONTRIBUTING.md
- Add proper credits to original project `strelitzia-reg/qqmusic-decryptor`

### Changed
- Clean up residual files for open-source release
- Update .gitignore with explicit hidden directory listing

## [1.1.0] - 2026-01-31

### Added
- GUI log management
- CLI: `qqmusic-decrypt` global command via `pip install -e .`

### Fixed
- Major fixes and optimizations (see detailed logs)

## [1.0.0] - 2026-01-30

### Added
- Batch decrypt `.mflac` → `.flac`, `.mgg` → `.ogg` via Frida
- Album metadata supplement (cover art embed + release year from QQ Music API)
- Directory structure preservation
- Smart skip for already-converted files
- Error retry mechanism (configurable, default 3 attempts)
- Detailed logging with JSON stats summary
- Dual interface: CLI and GUI modes
- Track number writing from filename
- OGG metadata support
- Source file deletion option
- Lyrics file copy feature

### Changed
- Metadata processing optimized with batch mode
- Switch to QQ Music official API for album covers
- Reorganize project structure

## [0.x] - 2026-01-28/29

### Added
- Initial project setup
- Basic decrypt functionality
- Album metadata supplement (first working version)
- Cover art save path fix
