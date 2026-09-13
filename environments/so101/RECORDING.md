# First recording: one diagnostic episode

Run from the repository root in Ubuntu (fish is supported):

```sh
uv run --project environments/so101 --frozen lerobot-record --config_path=environments/so101/record_smoke.json
```

This command moves the follower. Keep the Windows camera publisher running,
close any previous teleoperation process, clear the workspace, and begin with
similar leader/follower poses. Operate the black leader, watching the white
follower. Record a small object's lift and return if possible; success is not
required for this diagnostic episode.

The configuration records one 60-second episode at a requested 10 Hz, with
`max_relative_target=5`, camera topic `wrist`, and local storage under
`local/so101/datasets/lift-smoke-001`. It does not upload to Hugging Face.
It does not display live video. The Windows publisher remains at 30 fps;
the recording loop samples its latest available images. Network latency and
image/action alignment still need validation.

The right-arrow key ends an episode early when the keyboard listener is active.
Ctrl+C interrupts the process, but may leave the current episode unsaved.
Normal cleanup disables motor torque; return the object to the table and keep
the follower low before ending. No extra reset episode is needed for this
single-episode run. An existing output directory is not automatically deleted;
inspect the result before retrying or resuming.

LeRobot 0.6.1's `record_loop` stores the teleoperator action before the follower's
`max_relative_target` clamp. It ignores the returned `_sent_action` for dataset
storage. Thus `action` represents the requested goal, not the limited goal sent
to the servos, and `observation.state` represents follower measurements.
Preserve this distinction when interpreting tracking error or choosing training
and deployment behavior. This first dataset is a pipeline check, not yet a
curated training dataset.

Preparation validation: configuration parsed with the installed RecordConfig,
record CLI imports/help passed, and the default AV1 encoder encoded a synthetic
frame. Actual recording and dataset integrity require the user's physical trial.

## First attempt: startup communication failure

2026-09-13 17:01: the ZMQ camera connected, but enabling follower motor ID 2
(shoulder lift) returned `Incorrect status packet!`. Recording had not started.
The prior TorchCodec warning was nonfatal: LeRobot selected PyAV as a fallback.
The log does not prove the torque-enable write was rejected; its acknowledgement
was invalid. Cleanup reported disconnecting both arms and the camera.

The output directory contained only `meta/info.json`, with zero frames and zero
episodes. It was preserved as `local/so101/datasets/lift-smoke-001-startup-failed-1701`
so the same configuration can be retried without deleting evidence or colliding
with an existing dataset. Do not use resume on this metadata-only attempt.
No motor IDs, calibration, PID settings, or write retry behavior were changed.
Check the follower power/cables with power off before retrying. A repeated failure
should be investigated as serial communication rather than triggering calibration.

## Successful retry: first episode inspection

The user's retry produced one episode with 600 numeric rows and 600 decodable
640x480 video frames. Frame indices are consecutive; stored timestamps run from
0.0 to 59.9 seconds at nominal 10 Hz. These timestamps do not establish actual
sensor acquisition timing or Windows-to-WSL latency. All action/state values are
finite. Contact-sheet sampling shows approach to and gripping of a blue pouch;
full task success (lift and return) has not been independently established.

Mean absolute requested-action minus follower-state differences, in joint order:
shoulder_pan 0.30 deg, shoulder_lift 2.92 deg, elbow_flex 4.92 deg,
wrist_flex 20.68 deg, wrist_roll 0.56 deg, gripper 5.61 percentage points.
The wrist-flex discrepancy warrants investigation before collecting many training
examples. This statistic includes moving and static periods and is not proof of
a calibration fault or steady-state error. Do not automatically raise the target
limit. Keep this diagnostic dataset separate from curated demonstrations.
