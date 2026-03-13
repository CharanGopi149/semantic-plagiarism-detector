# Semantic Plagiarism Benchmark

This folder contains a synthetic but realistic evaluation dataset for the semantic plagiarism detection project.

## Dataset Size

- 60 markdown documents
- 10 topic families
- 6 documents per family
- Train split: 36 documents
- Validation split: 12 documents
- Test split: 12 documents

## Document Variants Per Family

Each family contains:

- `source`: the original source document
- `direct_copy`: a near-verbatim plagiarism case
- `paraphrase_light`: a lightly rewritten semantic plagiarism case
- `paraphrase_heavy`: a more strongly rewritten semantic plagiarism case
- `mosaic`: a mixed document that blends copied, paraphrased, and clean content
- `independent`: a related but non-plagiarized control document

## Topics

- Adaptive Learning Analytics
- Renewable Microgrids
- Healthcare Cybersecurity
- Sustainable Supply Chains
- Explainable AI in Credit Risk
- Urban Traffic Forecasting
- Telemedicine Chronic Care
- Precision Agriculture IoT
- Cloud Disaster Recovery
- Battery Recycling

## Files

- `documents/train/`, `documents/validation/`, `documents/test/`
- `metadata.csv`: one row per document
- `pair_labels.csv`: expected plagiarism pairs for derived documents
- `summary.json`: dataset totals and split counts

## Metadata Fields

`metadata.csv` includes:

- `doc_id`
- `family_id`
- `split`
- `topic`
- `title`
- `variant`
- `plagiarism_label`
- `primary_source_doc_id`
- `expected_similarity_band`
- `sections_with_overlap`
- `word_count`
- `path`

## Regeneration

To regenerate the dataset:

```bat
.venv\Scripts\python scripts\generate_semantic_plagiarism_dataset.py
```

## Notes

- All documents are synthetic and intended for benchmarking, demos, and testing.
- The runtime demo corpus used by the app is still in `data/corpus/`.
- This dataset is kept separate so the main demo workflow stays lightweight.
