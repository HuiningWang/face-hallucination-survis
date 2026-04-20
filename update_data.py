import argparse
import codecs
import json
import os
import time


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "src", "data")
GENERATED_DIR = os.path.join(DATA_DIR, "generated")
PAPERS_DIR = os.path.join(DATA_DIR, "papers_pdf")
PAPERS_IMG_DIR = os.path.join(DATA_DIR, "papers_img")

BIB_FILE = os.path.join(BASE_DIR, "bib", "references.bib")
BIB_JS_FILE = os.path.join(GENERATED_DIR, "bib.js")
AVAILABLE_PDF_FILE = os.path.join(GENERATED_DIR, "available_pdf.js")
AVAILABLE_IMG_FILE = os.path.join(GENERATED_DIR, "available_img.js")


def parse_bibtex(bib_file):
    parsed_data = {}
    last_field = ""
    current_id = ""

    with codecs.open(bib_file, "r", "utf-8-sig") as bib_stream:
        for raw_line in bib_stream:
            line = raw_line.strip("\n").strip("\r")
            if line.startswith("@Comment"):
                continue
            if line.startswith("@"):
                current_id = line.split("{", 1)[1].rstrip(",\n")
                current_type = line.split("{", 1)[0].strip("@ ")
                parsed_data[current_id] = {"type": current_type}
            if not current_id:
                continue
            if "=" in line:
                field, value = line.split("=", 1)
                field = field.strip().lower()
                value = value.strip("} \n")
                if value.endswith("},"):
                    value = value[:-2]
                if value.startswith("{"):
                    value = value[1:]
                if field in parsed_data[current_id]:
                    parsed_data[current_id][field] = parsed_data[current_id][field] + " " + value
                else:
                    parsed_data[current_id][field] = value
                last_field = field
            elif last_field in parsed_data[current_id]:
                value = line.strip().strip("} \n").replace("},", "").strip()
                if value:
                    parsed_data[current_id][last_field] = parsed_data[current_id][last_field] + " " + value

    return parsed_data


def write_json(parsed_data):
    os.makedirs(GENERATED_DIR, exist_ok=True)
    with codecs.open(BIB_JS_FILE, "w", "utf-8-sig") as output_stream:
        output_stream.write("const generatedBibEntries = ")
        output_stream.write(json.dumps(parsed_data, sort_keys=True, indent=4, separators=(",", ": ")))
        output_stream.write(";")


def warn_coursework_requirements(parsed_data):
    entry_count = len(parsed_data)
    if entry_count < 10 or entry_count > 20:
        print("warning: coursework expects 10-20 papers, current bibliography has " + str(entry_count))

    missing_doi = sorted([entry_id for entry_id, fields in parsed_data.items() if not fields.get("doi")])
    if missing_doi:
        print("warning: DOI missing for " + str(len(missing_doi)) + " entries")
        for entry_id in missing_doi:
            print("  - " + entry_id)

    missing_keywords = sorted([entry_id for entry_id, fields in parsed_data.items() if not fields.get("keywords")])
    if missing_keywords:
        print("warning: " + str(len(missing_keywords)) + " entries do not have keywords")
        for entry_id in missing_keywords:
            print("  - " + entry_id)


def list_available_files(source_dir, output_file, variable_name, suffix):
    os.makedirs(GENERATED_DIR, exist_ok=True)
    items = []
    if os.path.isdir(source_dir):
        for filename in sorted(os.listdir(source_dir)):
            if filename.endswith(suffix):
                items.append(filename.replace(suffix, ""))

    with open(output_file, "w", encoding="utf-8") as output_stream:
        output_stream.write("const " + variable_name + " = " + json.dumps(items) + ";")


def list_available_pdf():
    list_available_files(PAPERS_DIR, AVAILABLE_PDF_FILE, "availablePdf", ".pdf")


def list_available_img():
    list_available_files(PAPERS_IMG_DIR, AVAILABLE_IMG_FILE, "availableImg", ".png")


def generate_folders():
    for directory in [GENERATED_DIR, PAPERS_DIR, PAPERS_IMG_DIR]:
        os.makedirs(directory, exist_ok=True)


def update():
    print("convert bib file")
    parsed_data = parse_bibtex(BIB_FILE)
    write_json(parsed_data)
    warn_coursework_requirements(parsed_data)
    print("list available paper PDF files")
    list_available_pdf()
    print("list available paper images")
    list_available_img()
    print("done")


def watch():
    previous_bib_time = 0
    while True:
        current_bib_time = os.stat(BIB_FILE).st_mtime
        if previous_bib_time != current_bib_time:
            print("detected change in bib file")
            update()
            previous_bib_time = current_bib_time
        else:
            print("waiting for changes in bib file: " + BIB_FILE)
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SurVis data files from the BibTeX source.")
    parser.add_argument("--once", action="store_true", help="generate files once and exit")
    args = parser.parse_args()

    generate_folders()

    if args.once:
        update()
    else:
        watch()
