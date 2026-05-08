def reciprocal_rank_fusion(results_lists, k=60):
    """
    Combines multiple ranked lists using RRF.
    results_lists: list of lists of documents
    """
    scores = {}
    for results in results_lists:
        for rank, doc in enumerate(results):
            doc_id = doc.page_content # Using content as ID for simplicity
            if doc_id not in scores:
                scores[doc_id] = {"doc": doc, "score": 0}
            scores[doc_id]["score"] += 1.0 / (rank + k)

    # Sort by combined score
    sorted_results = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    return [item["doc"] for item in sorted_results]
