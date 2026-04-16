# 30-Day Exercise Plan (Stage 2)

Format:
- Exercise
- Purpose

**Current state:** Week 1 - Day 1

## Week 1 - Baseline
- Day 1: Verify topics and TF chain.
  - Purpose: confirm system wiring before tuning.
- Day 2: Straight-line repeat test.
  - Purpose: measure translational error.
- Day 3: In-place rotation repeat test.
  - Purpose: measure heading error.
- Day 4: First calibration pass.
  - Purpose: reduce major geometric bias.
- Day 5: Time behavior check (sim_time on/off).
  - Purpose: detect timing-induced odom instability.
- Day 6: Encoder edge-case tests.
  - Purpose: identify outlier/failure signatures.
- Day 7: Week-1 re-test.
  - Purpose: quantify improvement vs baseline.

## Week 2 - Odometry Robustness
- Day 8: Define outlier thresholds.
  - Purpose: avoid invalid motion updates.
- Day 9: Long/short dt handling test.
  - Purpose: prevent velocity spikes.
- Day 10: Velocity smoothing experiment.
  - Purpose: improve control-level signal quality.
- Day 11: Long standstill test.
  - Purpose: measure drift per minute.
- Day 12: Low-speed sensitivity test.
  - Purpose: find reliable minimum motion range.
- Day 13: Forward-reverse transition test.
  - Purpose: validate sign and continuity handling.
- Day 14: Week-2 consolidation.
  - Purpose: freeze robust odom parameter set.

## Week 3 - Fusion
- Day 15: IMU signal quality check.
  - Purpose: validate fusion input quality.
- Day 16: EKF initial config.
  - Purpose: establish first fusion baseline.
- Day 17: Fusion A/B test on rotation.
  - Purpose: compare heading drift improvement.
- Day 18: Covariance tuning.
  - Purpose: balance responsiveness and noise.
- Day 19: Square-path closure test.
  - Purpose: evaluate integrated pose consistency.
- Day 20: Aggressive acceleration test.
  - Purpose: evaluate dynamic stability.
- Day 21: Week-3 consolidation.
  - Purpose: freeze fusion v1.

## Week 4 - Nav2 Integration
- Day 22: Minimal Nav2 bringup.
  - Purpose: validate stack startup dependency chain.
- Day 23: Multi-goal mission test.
  - Purpose: check repeatable navigation execution.
- Day 24: Local planning behavior tuning.
  - Purpose: reduce oscillation near path/goal.
- Day 25: Recovery behavior validation.
  - Purpose: assess failure handling quality.
- Day 26: Launch/profile cleanup.
  - Purpose: make runtime setup reproducible.
- Day 27: Integrated endurance run.
  - Purpose: test stability over longer sessions.

## Week 5-6 (Compressed) - Reliability and Closure
- Day 28: Fault injection session.
  - Purpose: verify robustness under degraded data.
- Day 29: Operations checklist draft.
  - Purpose: standardize daily bringup/debug routine.
- Day 30: Stage-2 review and backlog.
  - Purpose: define next-stage priorities.
