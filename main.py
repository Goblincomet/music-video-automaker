import argparse

from librosa.core import get_duration

from beat_detect import get_beat_times
from merge_video import merge_video, get_cut_list
from scene_detect import get_scene_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge video and audio files into a music video",
        usage="%(prog)s video_path audio_path [options]",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=32),
    )
    parser.add_argument("video_path", help="video path (.mp4, .avi)")
    parser.add_argument("audio_path", help="audio path (.mp3, .wav)")
    parser.add_argument("-o", "--output-path", help="output path", default="./merged.mp4", metavar="PATH")
    parser.add_argument(
        "--method", choices=["delay", "pseudochrono", "random"], default="delay", help="clip arrangement method"
    )

    detector_options = parser.add_argument_group("adaptive scene detector")
    detector_options.add_argument(
        "--threshold",
        help="threshold value that the calculated frame score must exceed to trigger a new scene",
        default=3.0,
        type=float,
        metavar="FLOAT",
    )
    detector_options.add_argument(
        "--min-scene-len", help="minimum length of scene in frames", default=15, type=int, metavar="INT"
    )
    detector_options.add_argument(
        "--min-delta-hsv",
        help="minimum delta between scene frames in HSV color space",
        default=15.0,
        type=float,
        metavar="FLOAT",
    )
    detector_options.add_argument(
        "--window-width", help="width of rolling average window for scene detection", default=2, type=int, metavar="INT"
    )
    detector_options.add_argument("--luma-only", action="store_true", help="only consider luma/brightness channel")

    args = parser.parse_args()

    video_path = args.video_path
    audio_path = args.audio_path
    output_path = args.output_path

    print("Getting scene list")
    scene_list = get_scene_list(
        video_path, args.threshold, args.luma_only, args.min_scene_len, args.min_delta_hsv, args.window_width
    )

    print("Getting beat times")
    beat_times, tempo = get_beat_times(audio_path)
    audio_length = get_duration(filename=audio_path)

    scene_cuts = [scene[0].get_seconds() for scene in scene_list]
    print(f"Getting cut list ({args.method})")
    cut_list = get_cut_list(scene_cuts, tempo, beat_times[0], audio_length, method=args.method)

    print("Merging")
    merge_video(video_path, audio_path, output_path, cut_list)
