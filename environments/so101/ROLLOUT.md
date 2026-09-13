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
without building a hardware context. Physical rollout is pending user execution.
