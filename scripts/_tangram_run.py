import argparse

import anndata

from sopa.annotation.tangram.run import MultiLevelAnnotation


def main(args):
    ad_sp = anndata.read_h5ad(args.path_spatial)
    adata_sc = anndata.read_h5ad(args.path_reference)

    MultiLevelAnnotation(
        ad_sp,
        adata_sc,
        cell_type_key="ct",
        reference_preprocessing=None,
        bag_size=10_000,
        max_obs_reference=10_000,
    ).run()

    ad_sp.write_h5ad(args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-sp",
        "--path_spatial",
        type=str,
        required=True,
        help="Path to the spatial h5ad",
    )
    parser.add_argument(
        "-sc",
        "--path_reference",
        type=str,
        required=True,
        help="Path to the reference h5ad",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Path to the output h5ad",
    )

    main(parser.parse_args())
