# Review Checklist

Open items to revisit during pipeline hardening.

## Threshold Wiring

- [ ] Review `confidence.min_track` and `confidence.min_event` in `configs/thresholds.yaml`.
      They are currently defined in config, but no active pipeline stage appears to apply them
      as filters. Decide whether to wire them into track/event pruning or remove/rename them
      to avoid implying behavior that is not present.
