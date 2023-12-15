import argparse
from pathlib import Path

DATA_PATH = Path("/mnt/beegfs/merfish/data")
PROCESSED_PATH = Path("/mnt/glustergv0/MERFISH/processed")


class Outputs:
    ADATA = "adata.h5ad"
    METADATA = "experiment.xenium"
    IMAGE = "morphology.ome.tif"
    REPORT = "analysis_summary.html"


def get_suffix(processed_dir: Path, explorer_dir: Path, zarr_dir: Path):
    if (processed_dir / "experiment.xenium").exists():
        return "Complete"
    if not explorer_dir.exists():
        return "Not started (or starting)"
    if not (zarr_dir / "table").exists():
        return "Started"
    names = [
        Outputs.METADATA,
        Outputs.IMAGE,
        Outputs.ADATA,
        Outputs.REPORT,
    ]
    files = [explorer_dir / name for name in names]
    return "Segmentation complete. Missing output files: " + ", ".join(
        [p.name for p in files if not p.exists()]
    )


def subdir(path):
    return [p for p in path.iterdir() if p.is_dir()]


def main(args):
    tissues = [DATA_PATH / args.tissue]
    if not args.tissue:
        tissues = subdir(DATA_PATH)

    for tissue in tissues:
        name = f"Tissue: {tissue.name}"
        print(name)
        print("-" * len(name))

        for slide in subdir(tissue):
            if slide.name in ["reference", "macsima"]:
                continue

            print(f"Slide {slide.name}")

            for i in range(4):
                region = slide / f"region_{i}"
                if region.exists():
                    explorer_dir = slide / f"region_{i}.explorer"
                    zarr_dir = slide / f"region_{i}.zarr"
                    processed_dir = (
                        PROCESSED_PATH / tissue.name / slide.name / f"{region.name}.explorer"
                    )

                    print(f"    {region.name}: {get_suffix(processed_dir, explorer_dir, zarr_dir)}")
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
