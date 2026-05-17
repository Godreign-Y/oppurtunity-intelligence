"""
Parser for Hugging Face API responses.
"""


def parse_models(models: list) -> list:
    """
    Parse Hugging Face models safely.
    """

    parsed = []

    for model in models:
        parsed.append(
            {
                "model_id": model.get("modelId"),
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "tags": model.get("tags", []),
                "pipeline_tag": model.get("pipeline_tag"),
                "source_url": f"https://huggingface.co/{model.get('modelId')}",
            }
        )

    return parsed
