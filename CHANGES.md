# Changes

## Unreleased
- Added KiCad capability detection and a centralized item lookup helper for newer APIs with safe fallbacks.
- Updated edit/move flows to use the shared lookup and return clearer not-found errors.
- Auto-generated KiCad type mappings from protobuf descriptors with override hooks and guarded required-args.
- Lazily initialized the KiCad CLI converter so server startup works without CLI configuration.
- Added a test skip guard when `mcp`/`kipy` dependencies are unavailable.
