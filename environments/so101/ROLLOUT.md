# First autonomous motion check

This is a user-operated, ten-second hardware check of the ACT checkpoint. It is
not a measured grasp-success evaluation. The original demonstration took roughly
50 seconds to reach the lift, so this short check need not complete the task.

Before running:

1. Keep the white follower clamped. Place the same light object and wrist camera
   as in recording 003, and arrange a similar starting arm posture. Position the
   supported arm with motor power off; do not push powered joints into position.
2. Check the white follower uses its 12V supply and its USB remains attached to
   WSL. Stop any recording or teleoperation process using the arms.
3. Start the existing Windows camera publisher. Confirm the configured host
   `172.24.144.1` still matches the Windows endpoint and the picture is current.
4. Clear hands and obstacles from the follower's motion. Keep Ctrl+C accessible
   and the follower power supply reachable. Disconnecting disables holding torque;
   allow for the arm dropping. The black leader is not an intervention controller
   in this mode.

Windows PowerShell camera command (leave running):

```powershell
uv run --script "\\wsl.localhost\Ubuntu\home\tyuyoshi\robot-learning-a-tutorial\environments\so101\windows_camera_server.py" --bind 172.24.144.1
```

Ubuntu, from the repository root (this command moves the white arm):

```sh
uv run --project environments/so101 --frozen lerobot-rollout --config_path=environments/so101/rollout_smoke.json --policy.path=local/so101/outputs/act-smoke-003/checkpoints/001000/pretrained_model
```

There is no additional confirmation prompt before motion. The duration is checked
between control-loop iterations, so ten seconds is not a hard emergency deadline.
Stop with Ctrl+C if motion approaches the table or an obstacle; if software does
not stop motion, cut the follower's power. Do not catch the moving gripper.

`base` selects autonomous operation without dataset recording or upload. `sync`
uses synchronous inference, at a target 10Hz. The checkpoint predicts ten actions
but uses one per observation (`n_action_steps=1`). The follower retains
`max_relative_target=5`, which is neither collision protection nor a force limit.
`return_to_initial_position=false` disables the default extra return motion.
Normal teardown disconnects and disables torque. No online learning occurs.

Report whether the white arm moved, its direction, any contact or stopping, and
the final log lines. Black-arm motion does not affect this run. Do not increase
duration or limits simply to force a grasp.

Validation: installed LeRobot 0.6.1 rollout code inspected; configuration parsed
without building a hardware context. The user then executed the physical checks
below. Completion of the loop is not task success.

## 2026-09-13: startup failure, oscillation, and manual comparison

- At 17:58 startup failed on motor 6 (gripper), writing `Lock=1`: no status packet.
  Policy and camera loaded, but autonomous control did not start. A prior recording
  had failed on motor 2 with an incorrect status packet. Root cause is unconfirmed.
  The `so100_follower` log label is a shared configuration alias; the JSON still
  selects SO101 and the correct white follower port and calibration.
- At 18:01 the user reported shaking without task progress. The ten-second loop
  and disconnect completed. No motor communication exception appeared in that log.
  Wrist target commands alternated around -83 and -70 degrees. Clamp warnings show
  only selected ticks, not the complete action sequence. The 2.2Hz warning appeared
  once at startup; it does not establish sustained 2.2Hz operation.
- CPU diagnostic: five `select_action` calls on the identical saved first image
  and state of recording 003 produced maximum output difference 0.0. Rollout code
  uses eval mode. This rules out random variation for that tested input, not every
  source of instability on hardware.
- Working hypotheses: an insufficiently learned policy and/or observations unlike
  training may form an oscillating feedback loop. Camera delay and physical control
  effects remain possible. Do not label the cause established, increase the target
  limit, or keep repeating autonomous motion. Temporal smoothing could reduce
  oscillation but would not demonstrate learned task completion.

The user subsequently ran the following manual diagnostic, with the model absent:

```sh
uv run --project environments/so101 --frozen lerobot-record --config_path=environments/so101/record_smoke.json --dataset.repo_id=local/so101-teleop-check-001 --dataset.root=local/so101/datasets/teleop-check-001 --dataset.episode_time_s=15
```

Verified 150 finite state/action rows and 150 decoded video frames. In order
pan/lift/elbow/wrist-flex/wrist-roll/gripper, leader-vs-follower MAE was
0.80/0.92/1.48/0.88/3.10 degrees and 0.19 percentage points. Follower motion spans
were 18.37/4.66/61.63/52.04/91.52 degrees and 0.21 points. Thus several joints moved,
but the leader shoulder-lift span was only 0.44 degrees and the gripper was barely
operated: this is not a complete joint motion test. Mean error alone does not prove
absence of shaking. The user's observation of manual smoothness is pending.

Keep this diagnostic recording separate from training examples; the inherited
pick-and-place task text is not a claim that a grasp was attempted or completed.

## Temporal ensemble: next short comparison

The user clarified that manual operation followed the leader with some roughness,
unlike the autonomous trial that shook without task progress. An offline comparison
then reduced command variation using temporal ensembling (see TRAINING.md).

`rollout_ensemble.json` retains the original hardware, 10Hz, ten-second duration,
target delta limit 5, and disabled return motion. It references the same 001000
checkpoint and overrides only `temporal_ensemble_coeff=0.01`. The saved checkpoint
and original rollout config are unchanged. There is no retraining.

With the existing Windows camera publisher running, other control processes stopped,
and a similar initial arm pose, object placement, and camera view to the previous
trial, run in Ubuntu (moves the white arm; black cannot intervene):

```sh
uv run --project environments/so101 --frozen lerobot-rollout --config_path=environments/so101/rollout_ensemble.json
```

Keep the earlier power/clearance/stop precautions. Stop immediately for sustained
shaking or contact; do not wait ten seconds to see whether it improves. On disconnect
the arm loses holding torque. This base-mode trial does not record video or actions.
Report shaking separately from task progress: less shaking, motion toward the
object, and any contact/stop. A ten-second observation is not a grasp success rate.
Initial pose matching is approximate, so the physical comparison is exploratory.

Validation: parsed the exact JSON through the installed rollout parser without
connecting hardware, asserting coefficient 0.01, one action step, checkpoint,
duration, FPS, target limit, no teleoperator/dataset, and disabled return motion.
The user executed the ensemble trial and reported less shaking than before and
felt that it came close to completing the task. Grasp/lift success is unconfirmed.
This is a subjective observation from an unrecorded trial, with approximately
matched starting conditions, not a repeated controlled measurement. Model weights
were unchanged; this is an inference change, not learning during execution.
Before extending duration, determine whether the timer interrupted progress,
the gripper closed off-target, or the arm stalled before reaching the object.
