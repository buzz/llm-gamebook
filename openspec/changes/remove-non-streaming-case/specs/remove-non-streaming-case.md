## ADDED Requirements

(none - this is a code simplification change with no new capabilities)

## MODIFIED Requirements

(none - the existing `thinking-duration` requirements remain unchanged; we're just removing the dead code path that didn't support duration tracking)

## REMOVED Requirements

(none)

## Notes

This change does not introduce new requirements or modify existing ones. It removes a dead code path that was never used in production. The existing `thinking-duration` spec requirements are satisfied by the streaming code path, which remains intact.
