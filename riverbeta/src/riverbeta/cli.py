"""Command-line interface for riverbeta.

Every step is also available standalone so you can re-run just the part
you need (e.g. re-run ``hazards`` after tweaking the keyword list without
re-transcribing).
"""

import argparse
from pathlib import Path

from . import pipeline


def main() -> None:
    parser = argparse.ArgumentParser(prog="riverbeta")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_out_arg(p):
        p.add_argument("--out", type=Path, required=True, help="working directory")

    p_fetch = sub.add_parser("fetch", help="download video + extract audio")
    p_fetch.add_argument("url")
    add_out_arg(p_fetch)

    p_transcribe = sub.add_parser("transcribe", help="speech-to-text + translation (local whisper)")
    add_out_arg(p_transcribe)
    p_transcribe.add_argument("--model", default="small", help="faster-whisper model size")
    p_transcribe.add_argument("--device", default="cpu", choices=["cpu", "cuda"])

    p_frames = sub.add_parser("frames", help="sample frames from the video")
    add_out_arg(p_frames)
    p_frames.add_argument("--fps", type=float, default=1.0)

    p_colormap = sub.add_parser("colormap", help="build pixel color map + detect scene changes")
    add_out_arg(p_colormap)
    p_colormap.add_argument("--grid", type=int, default=8, help="grid size (NxN) per frame")
    p_colormap.add_argument("--threshold", type=float, default=18.0, help="scene-change sensitivity")

    p_hazards = sub.add_parser("hazards", help="extract hazard/landmark mentions from the transcript")
    add_out_arg(p_hazards)

    p_report = sub.add_parser("report", help="render the illustrated HTML report")
    add_out_arg(p_report)

    p_run = sub.add_parser("run", help="run the full pipeline end to end")
    p_run.add_argument("url")
    add_out_arg(p_run)
    p_run.add_argument("--model", default="small", help="faster-whisper model size")
    p_run.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    p_run.add_argument("--fps", type=float, default=1.0)

    args = parser.parse_args()

    if args.command == "fetch":
        pipeline.step_fetch(args.url, args.out)
    elif args.command == "transcribe":
        pipeline.step_transcribe(args.out, model_size=args.model, device=args.device)
    elif args.command == "frames":
        pipeline.step_frames(args.out, fps=args.fps)
    elif args.command == "colormap":
        pipeline.step_colormap(args.out, grid=(args.grid, args.grid), threshold=args.threshold)
    elif args.command == "hazards":
        pipeline.step_hazards(args.out)
    elif args.command == "report":
        report_path = pipeline.step_report(args.out)
        print(report_path)
    elif args.command == "run":
        report_path = pipeline.run_all(
            args.url, args.out, model_size=args.model, device=args.device, fps=args.fps
        )
        print(report_path)


if __name__ == "__main__":
    main()
