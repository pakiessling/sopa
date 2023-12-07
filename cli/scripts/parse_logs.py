import argparse
import re
import subprocess
from collections import defaultdict
from datetime import timedelta
from math import floor, log
from pathlib import Path

SUCCESS_STATUS = "COMPLETED"
LOGS_PATH = Path("/mnt/beegfs/merfish/sopa/workflow/logs")


def parse_one(job_id, status):
    try:
        seff = subprocess.check_output(["seff", job_id], text=True).split("\n")

        state = seff[3].split(" ")[1]
        _, hours, min, sec = seff[7].split(":")
        mem, unit, *_ = seff[8].split(":")[1].split()

        rule = "*starting*"
        scat = subprocess.check_output(
            ["head", "-9", LOGS_PATH / job_id],
            text=True,
        ).split("\n")
        rule = scat[-2].split()[1][:-1]

        status[rule][state].append((job_id, float(mem), unit, int(hours), int(min), int(sec)))
    except Exception:
        status["*not-started*"][state].append((job_id, None, None, None, None, None))


def format_bytes(size):
    power = 0 if size <= 0 else floor(log(size, 1024))
    return f"{round(size / 1024 ** power, 2)} {['B', 'KB', 'MB', 'GB', 'TB'][int(power)]}"


to_bytes = {
    "B": 1,
    "KB": 1_000,
    "MB": 1_000_000,
    "GB": 1_000_000_000,
    "TB": 1_000_000_000_000,
}


def mean_size(stats):
    sizes = [s[1] * to_bytes[s[2]] for s in stats]
    return format_bytes(sum(sizes) / len(sizes))


def mean_time(stats):
    seconds = [s[5] + 60 * (s[4] + 60 * s[3]) for s in stats]
    return timedelta(seconds=int(sum(seconds) / len(seconds)))


def show(rule, values):
    if SUCCESS_STATUS in values.keys():
        print(
            f"{rule} ({mean_size(values[SUCCESS_STATUS])} | {mean_time(values[SUCCESS_STATUS])} per run)"
        )
    else:
        print(rule)
    print("-" * len(rule))
    for status, stats in values.items():
        print(
            f"   {status} ({f'N={len(stats)}, last_' if len(stats) > 1 else ''}id={stats[-1][0]})"
        )


def main(path):
    with open(path, "r") as f:
        text = "\n".join(f.readlines())

    job_ids = re.findall(r"(?<=Submitted batch job\s)\d+(?=\D)", text)

    status = defaultdict(lambda: defaultdict(list))

    for job_id in job_ids:
        parse_one(job_id, status)

    print()
    for rule, values in status.items():
        show(rule, values)
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        required=True,
        help="Path to the snakemake log file",
    )

    main(parser.parse_args().path)
