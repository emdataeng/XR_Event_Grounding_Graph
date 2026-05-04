# Review Checklist

Open items to revisit during pipeline hardening.

## Threshold Wiring

- [ ] Review `confidence.min_track` and `confidence.min_event` in `configs/thresholds.yaml`.
      They are currently defined in config, but no active pipeline stage appears to apply them
      as filters. Decide whether to wire them into track/event pruning or remove/rename them
      to avoid implying behavior that is not present.

## Staleness Guards

- [ ] Add staleness checks to every pipeline script before it consumes upstream artifacts.
      This should include optional inputs as well as required inputs, so a stage cannot silently
      read stale files from an earlier run. Example cases: `09c` reading old `operation_events.csv`
      before `10b` rebuilds it, and `09d` reading an old `assembly_graph.json` unless `10e`
      metadata proves it is current.
