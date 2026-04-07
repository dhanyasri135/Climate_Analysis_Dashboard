import argparse
import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from extract_and_prompt import DATASET_COLUMNS, analyze_document_for_dataset_row

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def find_documents(input_dir):
    documents = []
    for name in sorted(os.listdir(input_dir)):
        path = os.path.join(input_dir, name)
        if not os.path.isfile(path):
            continue
        _, ext = os.path.splitext(name)
        if ext.lower() in SUPPORTED_EXTENSIONS:
            documents.append(path)
    return documents


def build_dataset(input_dir, output_csv, fail_fast=False):
    documents = find_documents(input_dir)
    if not documents:
        raise ValueError(f"No supported documents found in {input_dir}")

    rows = []
    failures = []

    for idx, doc_path in enumerate(documents, start=1):
        filename = os.path.basename(doc_path)
        print(f"[{idx}/{len(documents)}] Processing {filename} ...")
        try:
            row = analyze_document_for_dataset_row(doc_path)
            row = {k: row.get(k) for k in DATASET_COLUMNS}
            rows.append(row)
        except Exception as e:
            message = f"{filename}: {str(e)}"
            failures.append(message)
            print(f"  -> FAILED: {message}")
            if fail_fast:
                raise

    if not rows:
        raise RuntimeError("All documents failed. No dataset written.")

    df = pd.DataFrame(rows, columns=DATASET_COLUMNS)
    df.to_csv(output_csv, index=False)

    print(f"\nWrote {len(df)} rows to: {output_csv}")
    if failures:
        print(f"{len(failures)} documents failed:")
        for msg in failures:
            print(f"  - {msg}")


def main():
    parser = argparse.ArgumentParser(
        description="Build megacities dataset using multi-pass chunked ingestion from policy documents."
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing source policy documents (.pdf, .docx, .txt)",
    )
    parser.add_argument(
        "--output-csv",
        default=os.path.join("data", "megacities_dataset_generated.csv"),
        help="Path for generated CSV output",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on the first failed document",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        raise ValueError(f"Input directory does not exist: {args.input_dir}")

    output_dir = os.path.dirname(args.output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    build_dataset(args.input_dir, args.output_csv, fail_fast=args.fail_fast)


if __name__ == "__main__":
    main()
