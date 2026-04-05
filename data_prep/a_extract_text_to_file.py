import os
import pathlib
import sys

import pdfplumber
import pymupdf4llm
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from unstructured.partition.auto import partition


def main():

    pathlib.Path(".data").mkdir(exist_ok=True)
    file_path = sys.argv[1]

    print("\nStarting marker")
    config_parser = ConfigParser(
        {
            "disable_image_extraction": True,
            "force_ocr": False,
            "output_format": "markdown",
        }
    )

    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
    )
    rendered = converter(file_path)
    text, _, _ = text_from_rendered(rendered)
    with open(".data/raw_text_marker.txt", "w") as f:
        f.write(text)
    print("marker done")

    print("\nStarting pdfplumber")
    with pdfplumber.open(file_path) as pdf:
        with open(".data/raw_text_pdfplumber.txt", "w") as f:
            for page in pdf.pages:
                text = page.extract_text()
                settings = {
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 3,  # merge close-to-parallel lines
                    "join_tolerance": 3,
                    "edge_min_length": 3,
                    "min_words_vertical": 3,  # min words to infer a column
                    "min_words_horizontal": 1,  # min words to infer a row
                    "intersection_tolerance": 3,
                    "text_tolerance": 3,
                }
                tables = page.extract_tables(table_settings=settings)
                f.write(str(text))
                f.write(str(tables))
    print("pdfplumber done")

    print("\nStarting pymupdf4llm")
    md_text = pymupdf4llm.to_markdown(
        file_path,
        table_strategy="text",
        margins=(0, 50, 0, 50),
        ignore_images=True,
        ignore_graphics=True,
        show_progress=True,
    )
    pathlib.Path(".data/raw_text_pymupdf4llm.md").write_text(md_text)
    print("pymupdf4llm done")

    print("\nStarting unstructured")
    elements = partition(
        filename=file_path,
        strategy="hi_res",
        hi_res_model_name="yolox_quantized",
        infer_table_structure=True,
        languages=["deu", "eng"],
        extract_images_in_pdf=False,
    )
    with open(".data/raw_text_unstructured.txt", "w") as f:
        for el in elements:
            f.write(str(el))
    print("unstructured done")


if __name__ == "__main__":
    main()
