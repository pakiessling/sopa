import argparse
from pathlib import Path

DATA_PATH = Path("/mnt/beegfs/merfish/data")
HISTORY_PATH = Path("/mnt/beegfs/merfish/.smk_history")
PROCESSED_PATH = Path("/mnt/glustergv0/MERFISH/processed")


class Outputs:
    ADATA = "adata.h5ad"
    VZG = "output.vzg"
    REPORT = "report.html"
    NICHES = "obsm_stagate.npy"
    ANNOTATION = "tangram_annotations.h5ad"
    TEMP = "adata_temp.h5ad"
    SEGMENTATION = "cellpose_micron_space.parquet"


def get_suffix(run, processed):
    if processed.exists():
        return "COMPLETE"
    if (run / Outputs.TEMP).exists():
        names = [
            Outputs.VZG,
            Outputs.ANNOTATION,
            Outputs.NICHES,
            Outputs.ADATA,
            Outputs.REPORT,
        ]
        files = [run / name for name in names]
        return "Extracted h5ad but missing " + ", ".join(
            [p.name for p in files if not p.exists()]
        )
    if (run / Outputs.SEGMENTATION).exists():
        return "Segmentation is complete but missing h5ad extraction"
    return "Incomplete segmentation"


def get_last_log(run, history):
    for config, z, log_path in history[::-1]:
        if run.name == f"vpt_{config}_z{z}":
            return Path(log_path).name
    return ""


def subdir(path):
    return [p for p in path.iterdir() if p.is_dir()]


def parse_history(history_path):
    with open(history_path, "r") as f:
        return [line.split() for line in f.readlines()]


def main(args):
    tissues = [DATA_PATH / args.tissue]
    if not args.tissue:
        tissues = subdir(DATA_PATH)

    for tissue in tissues:
        name = f"Tissue: {tissue.name}"
        print(name)
        print("-" * len(name))

        for slide in subdir(tissue):
            print(f"Slide {slide.name}")

            for i in range(4):
                region = slide / f"region_{i}"
                if region.exists():
                    print(f"    - {region.name}")

                    history_path = (
                        HISTORY_PATH / f"{tissue.name}_{slide.name}_{region.name}.txt"
                    )
                    if not history_path.exists():
                        print("        (No pipeline started)")
                    else:
                        history = parse_history(history_path)

                        for run in subdir(region):
                            if run.name.startswith("vpt_"):
                                processed = (
                                    PROCESSED_PATH
                                    / tissue.name
                                    / slide.name
                                    / region.name
                                    / run.name
                                )
                                print(
                                    f"        {run.name} ({get_suffix(run, processed)}) - Last log: {get_last_log(run, history)}"
                                )
            print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tissue",
        type=str,
        nargs="?",
        const="",
        help="Tissue name",
    )

    main(parser.parse_args())
