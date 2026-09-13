"""Compare first-step ACT predictions with recorded commands; never connects hardware."""

import argparse
import csv
import json
import math
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.policies.act.configuration_act import ACTConfig
from lerobot.policies.act.modeling_act import ACTPolicy, ACTTemporalEnsembler
from lerobot.policies.factory import make_pre_post_processors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=Path(
        "local/so101/outputs/act-smoke-003/checkpoints/001000/pretrained_model"))
    parser.add_argument("--root", type=Path, default=Path("local/so101/datasets/lift-smoke-003"))
    parser.add_argument("--repo-id", default="local/so101-lift-smoke-003")
    parser.add_argument("--output", type=Path, default=Path("local/so101/analysis/act-smoke-003"))
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--ensemble-coeff", type=float, default=None)
    args = parser.parse_args()
    if args.ensemble_coeff is not None and not math.isfinite(args.ensemble_coeff):
        parser.error("Ensemble coefficient must be finite.")
    torch.set_num_threads(4)
    if not args.checkpoint.is_dir() or not args.root.is_dir():
        parser.error("Checkpoint and dataset must exist locally.")
    if args.output.exists():
        parser.error("Output already exists; choose a new --output directory.")

    config = ACTConfig.from_pretrained(str(args.checkpoint), local_files_only=True)
    config.device = args.device
    # All weights come from the local checkpoint; do not fetch ImageNet weights.
    config.pretrained_backbone_weights = None
    policy = ACTPolicy.from_pretrained(str(args.checkpoint), config=config, local_files_only=True)
    policy.eval()
    pre, post = make_pre_post_processors(
        policy.config, pretrained_path=str(args.checkpoint),
        preprocessor_overrides={"device_processor": {"device": args.device}},
    )
    dataset = LeRobotDataset(args.repo_id, root=args.root, video_backend="pyav")
    names = dataset.meta.features["action"]["names"]
    units = ["percentage_points" if name == "gripper.pos" else "degrees" for name in names]
    expected = [f"{name}.pos" for name in (
        "shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")]
    if names != expected or dataset.meta.features["observation.state"]["names"] != names:
        raise ValueError("This report expects the current SO101 six-channel dataset.")
    predictions, targets, states, timestamps, episodes, smoothed = [], [], [], [], [], []
    ensembler = (ACTTemporalEnsembler(args.ensemble_coeff, config.chunk_size)
                 if args.ensemble_coeff is not None else None)
    previous_episode = None
    with torch.inference_mode():
        for batch in DataLoader(dataset, batch_size=8, shuffle=False, num_workers=0):
            # No teacher actions enter the policy: use inference-time latent behavior.
            observations = {key: batch[key] for key in config.input_features}
            chunks = policy.predict_action_chunk(pre(observations))
            predicted = post(chunks[:, 0]).cpu()
            if ensembler is not None:
                # Causal alignment: combine predictions for the same target time.
                # Later observations in this batch never enter earlier outputs.
                for i, episode in enumerate(batch["episode_index"].tolist()):
                    if episode != previous_episode:
                        ensembler.reset()
                    smoothed.append(post(ensembler.update(chunks[i:i + 1])).cpu())
                    previous_episode = episode
            if not torch.isfinite(predicted).all():
                raise ValueError("Non-finite model predictions.")
            predictions.append(predicted)
            targets.append(batch["action"])
            states.append(batch["observation.state"])
            timestamps.append(batch["timestamp"])
            episodes.append(batch["episode_index"])
    predicted, target, state = [torch.cat(items) for items in (predictions, targets, states)]
    times = torch.cat(timestamps)
    mae = (predicted - target).abs().mean(0)
    hold_mae = (state - target).abs().mean(0)
    report = {
        "checkpoint": str(args.checkpoint.resolve()), "dataset": str(args.root.resolve()),
        "frames": len(dataset), "comparison": "first predicted action vs recorded leader request",
        "scope": "Training-data diagnostic, not held-out validation or robot success rate",
        "channels": [{"name": name, "unit": unit, "mae": float(error),
                      "hold_current_state_mae": float(baseline)}
                     for name, unit, error, baseline in zip(names, units, mae, hold_mae)],
    }
    if ensembler is not None:
        smooth = torch.cat(smoothed)
        if not torch.isfinite(smooth).all():
            raise ValueError("Non-finite ensemble predictions.")
        same_episode = torch.diff(torch.cat(episodes)) == 0
        if not same_episode.any():
            raise ValueError("Step-change metrics need consecutive frames in an episode.")
        smooth_mae = (smooth - target).abs().mean(0)
        raw_change = torch.diff(predicted, dim=0).abs()[same_episode]
        smooth_change = torch.diff(smooth, dim=0).abs()[same_episode]
        report["ensemble_coeff"] = args.ensemble_coeff
        report["scope"] = "Recorded-observation comparison; not closed-loop stability or task success"
        for j, channel in enumerate(report["channels"]):
            channel.update({
                "ensemble_mae": float(smooth_mae[j]),
                "raw_mean_step_change": float(raw_change[:, j].mean()),
                "ensemble_mean_step_change": float(smooth_change[:, j].mean()),
                "raw_p95_step_change": float(torch.quantile(raw_change[:, j], 0.95)),
                "ensemble_p95_step_change": float(torch.quantile(smooth_change[:, j], 0.95)),
            })
    args.output.mkdir(parents=True)
    (args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    with (args.output / "predictions.csv").open("w", newline="") as output:
        writer = csv.writer(output)
        kinds = ["target", "predicted", "state"] + (["ensemble"] if ensembler is not None else [])
        writer.writerow(["timestamp"] + [f"{kind}.{name}" for kind in kinds for name in names])
        for i in range(len(dataset)):
            writer.writerow([float(times[i])] + target[i].tolist() + predicted[i].tolist() + state[i].tolist()
                            + (smooth[i].tolist() if ensembler is not None else []))
    print(json.dumps(report, indent=2))
    print("Saved:", args.output.resolve())


if __name__ == "__main__":
    main()
