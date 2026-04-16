# ROS2 Stage-2 Roadmap for Diff-Drive Robot

## Context
- You have completed ROS2 basic examples without AI.
- You are practicing on your own diff-drive robot.
- You have ~2 years of ROS1 experience (AGV/AMR).

Goal of stage 2: move from "working demo" to "measurable, robust, integration-ready".

## Timeline
- 6 weeks (can compress to 4 weeks if full-time).
- 60-90 minutes per day.

## Weekly Focus

### Week 1 - Odometry baseline
- Exercise: verify encoder -> odom -> tf chain.
  - Purpose: ensure data path is correct.
- Exercise: measure drift at standstill and straight/turn error.
  - Purpose: establish baseline metrics.

### Week 2 - Calibration and robustness
- Exercise: tune wheel_radius, wheel_separation, ticks_per_revolution.
  - Purpose: reduce systematic odometry error.
- Exercise: define handling rules for tick outliers and dt anomalies.
  - Purpose: prevent false velocity spikes.

### Week 3 - Time model and fusion
- Exercise: validate ROS time vs system/steady time usage.
  - Purpose: stabilize timing behavior in real and sim runs.
- Exercise: fuse encoder + IMU (robot_localization).
  - Purpose: improve heading stability.

### Week 4 - Nav2 integration
- Exercise: run end-to-end bringup with mapping/localization/navigation.
  - Purpose: validate stack compatibility.
- Exercise: execute repeated goal missions.
  - Purpose: evaluate navigation reliability.

### Week 5 - Reliability testing
- Exercise: fault injection (drop/spike/jitter/delay).
  - Purpose: test resilience under bad data.
- Exercise: add diagnostics and pass/fail checks.
  - Purpose: speed up troubleshooting.

### Week 6 - Production readiness
- Exercise: freeze launch/config profiles (sim vs real).
  - Purpose: make behavior reproducible.
- Exercise: create minimal regression test checklist.
  - Purpose: prevent quality regression.

## AI Usage Rules for Stage 2
- You define I/O, state, and edge cases first.
- Ask AI for small code blocks, not full system rewrites.
- Every AI-generated block must be explainable: input, state changes, failure path, timing behavior.
