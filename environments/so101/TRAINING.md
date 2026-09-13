# First ACT learning experiment

Run in Ubuntu, from the repository root:

```sh
uv run --project environments/so101 --frozen lerobot-train --config_path=environments/so101/train_act_smoke.json
```

This offline command does not connect to either arm or the camera. Stop the
Windows camera publisher and put the arms at rest before powering them off.
It uses the third local recording only: the user reported a successful grasp,
and sampled video shows the pouch being held and lifted. Recording 002 was a
missed grasp according to the user; preserve it but exclude it from this initial
behavioral-cloning experiment. That is not a general rule to discard recovery
demonstrations: failures need appropriate action supervision or other objectives.

The goal is to exercise training, not to establish task success or generalization.
One episode gives correlated samples, not hundreds of independent demonstrations.
There is no held-out evaluation split. Training loss is not robot success rate.

Settings: ACT, CUDA, 1,000 optimization steps, batch size 4, chunk size 10,
one action step per call at later inference, zero DataLoader workers, PyAV video
decoding, and no Hub uploads or W&B logging. At nominal 10Hz, each target chunk
contains ten commands at offsets 0.0–0.9s. ResNet18 uses its default ImageNet
pretrained weights, downloaded on first use; robot action learning starts anew.
This is not fine-tuning a pretrained robot policy. Do not deploy the resulting
checkpoint on hardware without a separate evaluation procedure.

Outputs: local/so101/outputs/act-smoke-003. Do not overwrite an existing run.
Validation before launch: CLI imports/help, TrainPipelineConfig validation with
CUDA recognized, and LeRobotDataset sample read from all 600-row metadata.
Sample shapes: image (3,480,640), follower state (6,), action chunk (10,6).
All 600 video frames were decoded separately. On 2026-09-13 the user completed
1,000 steps in about 101 seconds; checkpoints 000500 and 001000 were saved.
Logged training loss fell from 16.160 (step 50) to 2.112 (step 1000).
TorchCodec library loading failed, but PyAV allowed training to complete.

Known dataset limits remain: network capture latency is unmeasured, action is the
leader request before follower target clipping, and tracking is not exact. The
trial retains these semantics and is not yet a curated production training set.

## Inspect predictions without connecting hardware

```sh
uv run --project environments/so101 --frozen python environments/so101/inspect_act_predictions.py
```

This CPU-only default reads the saved checkpoint and all 600 recorded observations.
It loads the checkpoint's normalization processors, supplies only observations to
the policy, and converts the first predicted action back to physical units.
It writes per-frame CSV predictions and per-joint MAE to
`local/so101/analysis/act-smoke-003/`. An existing output directory is refused;
use a new `--output` path when repeating. No camera or robot is connected.

The script is specific to the current SO101 dataset recorded with `use_degrees=True`:
five rotation channels are degrees, gripper is percentage points. It compares
predictions with the leader's recorded request, before follower clipping. A
baseline predicts the follower's current position (hold position); low baseline
error can reflect long stationary intervals, not task-solving ability.

This is a training-data diagnostic, not held-out validation, rollout, or success
rate. Only the first of ten predicted actions is scored. Independent episodes and
physical trials under predefined conditions are still required for evaluation.

First CPU run completed on all 600 frames with finite predictions. MAE in channel
order: 1.00, 5.00, 3.90, 5.35, 0.88 degrees; gripper 3.78 percentage points.
The hold-position baseline scored 0.75, 1.73, 2.26, 8.30, 2.66 degrees and 2.21
points respectively. ACT improves on that baseline only for wrist flex/roll in
this aggregate comparison. Long stationary sections can favor the baseline;
neither result measures grasp success. Raw per-frame values are in the local CSV.

## Temporal ensembling comparison (offline)

```sh
uv run --project environments/so101 --frozen python environments/so101/inspect_act_predictions.py --device cuda --ensemble-coeff 0.01 --output local/so101/analysis/ensemble-train-003
uv run --project environments/so101 --frozen python environments/so101/inspect_act_predictions.py --device cuda --ensemble-coeff 0.01 --repo-id local/so101-teleop-check-001 --root local/so101/datasets/teleop-check-001 --output local/so101/analysis/ensemble-teleop-check-001
```

Both runs completed with finite predictions (600 and 150 frames). The comparison
uses the same predicted chunks for each alternative and LeRobot's official
`ACTTemporalEnsembler`. It averages predictions made at different observation times
for the **same target time**, using only current/past observations and resetting at
episode boundaries. This is not averaging commands for different target times.
Coefficient 0.01 slightly favors older predictions in this installed implementation;
zero enables uniform averaging, while omitting the option disables this comparison.
Normalization is restored from the checkpoint, and results are unnormalized.

Training recording, wrist-flex mean absolute change per adjacent 0.1s frame:
1.90 -> 0.52 degrees. Its target MAE decreased 5.35 -> 4.92 degrees. All six channels
showed lower average changes and lower MAE on this recording.

Manual diagnostic, wrist-flex average change: 2.35 -> 0.50 degrees; target MAE
39.57 -> 38.50 degrees. Elbow MAE remained about 48 degrees. This diagnostic asks
for arbitrary manual movements, not the trained pick-and-place task: these errors
are not a valid grasp-generalization score. They show smoothing does not make the
model reproduce those different commands. They also do not diagnose the cause of
the prior live oscillation: the autonomous trajectory was not recorded.

Reduced command variation is not proof of reduced physical vibration. The replay
uses fixed recorded observations, not a world responding to the predicted commands.
No model weights, live rollout settings, or motor gains were changed. Keep live
autonomous retries paused pending a controlled follow-up.
