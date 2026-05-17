"""Semantic clustering service using UMAP + HDBSCAN."""

from typing import cast

import numpy as np
from hdbscan import HDBSCAN
from numpy.typing import NDArray
from umap import UMAP

from redit.utils.logging import get_logger

logger = get_logger(__name__)


class SemanticClusteringService:
    """
    Cluster embeddings using UMAP for
    dimensionality reduction + HDBSCAN.
    """

    def __init__(
        self,
        umap_n_neighbors: int = 15,
        umap_min_dist: float = 0.1,
        umap_metric: str = "cosine",
        hdbscan_min_cluster_size: int = 5,
        hdbscan_metric: str = "euclidean",
    ) -> None:

        self.umap_config = {
            "n_neighbors": umap_n_neighbors,
            "min_dist": umap_min_dist,
            "metric": umap_metric,
            "n_components": 10,
            "random_state": 42,
        }

        self.hdbscan_config = {
            "min_cluster_size": hdbscan_min_cluster_size,
            "metric": hdbscan_metric,
            "prediction_data": True,
        }

    def fit_and_predict(
        self,
        embeddings: NDArray[np.float32],
    ) -> tuple[
        NDArray[np.float32],
        NDArray[np.int_],
    ]:
        """
        Reduce dimensionality with UMAP,
        then cluster with HDBSCAN.
        """

        if len(embeddings) == 0:

            logger.warning(
                "Empty embeddings array provided"
            )

            return (
                np.array([], dtype=np.float32),
                np.array([], dtype=np.int_),
            )

        logger.info(
            "Starting UMAP reduction",
            extra={
                "n_embeddings": len(embeddings),
                "dim": int(embeddings.shape[1]),
            },
        )

        umap_reducer = UMAP(
            **self.umap_config
        )

        reduced = cast(
            NDArray[np.float32],
            umap_reducer.fit_transform(
                embeddings
            ),
        )

        logger.info(
            "UMAP reduction complete",
            extra={
                "reduced_dim": int(
                    reduced.shape[1]
                ),
            },
        )

        logger.info(
            "Starting HDBSCAN clustering"
        )

        clusterer = HDBSCAN(
            **self.hdbscan_config
        )

        labels = cast(
            NDArray[np.int_],
            clusterer.fit_predict(reduced),
        )

        n_clusters = (
            len(set(labels))
            - (
                1
                if -1 in labels
                else 0
            )
        )

        n_noise = (
            list(labels).count(-1)
        )

        logger.info(
            "HDBSCAN complete",
            extra={
                "n_clusters": n_clusters,
                "n_noise_points": n_noise,
                "noise_percentage":
                    f"{100*n_noise/len(labels):.1f}%",
            },
        )

        return reduced, labels

    def get_cluster_centers(
        self,
        embeddings: NDArray[np.float32],
        labels: NDArray[np.int_],
    ) -> dict[int, int]:
        """
        Find most central point
        in each cluster.
        """

        centers: dict[int, int] = {}

        unique_labels = set(labels)

        if -1 in unique_labels:
            unique_labels.remove(-1)

        for cluster_id in unique_labels:

            cluster_mask = (
                labels == cluster_id
            )

            cluster_indices = np.where(
                cluster_mask
            )[0]

            if len(cluster_indices) == 0:
                continue

            cluster_embeddings = (
                embeddings[cluster_mask]
            )

            centroid = np.mean(
                cluster_embeddings,
                axis=0,
            )

            distances = np.linalg.norm(
                cluster_embeddings
                - centroid,
                axis=1,
            )

            most_central_idx = int(
                cluster_indices[
                    np.argmin(distances)
                ]
            )

            centers[int(cluster_id)] = (
                most_central_idx
            )

        return centers

    def get_cluster_assignments(
        self,
        labels: NDArray[np.int_],
    ) -> dict[int, list[int]]:
        """
        Group indices by cluster.
        """

        assignments: dict[
            int,
            list[int],
        ] = {}

        for idx, label in enumerate(labels):

            if label == -1:
                continue

            cluster_id = int(label)

            if cluster_id not in assignments:
                assignments[cluster_id] = []

            assignments[
                cluster_id
            ].append(idx)

        return assignments