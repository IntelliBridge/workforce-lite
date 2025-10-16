# Custom PDF Scraper for Open WebUI

This submodule implements a custom PDF scraping solution for the Open WebUI container, enhancing document processing capabilities by combining the Unstructured library with Camelot for superior table preservation.

## Overview

This custom scraper modifies and extends functionality from the [Unstructured library](https://github.com/Unstructured-IO/unstructured) to provide enhanced PDF parsing capabilities, particularly focused on maintaining table integrity during the scraping process. By merging Unstructured's document analysis with Camelot's table extraction, the scraper ensures that tables are not reduced to basic paragraph representations but maintain their original format and structure.

## Architecture

### Scraper Components

The scraper modules are located in [`open_webui/backend/open_webui/retrieval/scrapers/`](https://github.com/IntelliBridge/open-webui/tree/3e6f1bb2d5c949f35d0b4aacf9cec56cee2d2fae/backend/open_webui/retrieval/scrapers):

- **base.py** - Base utilities and common functionality
- **custom_partition.py** - Modified partition logic with custom enhancements
- **layout.py** - Layout detection and processing
- **partition_pdf_camelot.py** - Core integration between Unstructured and Camelot for table-aware PDF processing
- **utils.py** - Utility functions for operations and is an important script that contains the download_if_needed_and_get_local_path function. This function specifies the model revision that will be chosen with huggingface. Enables code to find the specific model moved into the image.
- **yolox.py** - YOLOX model integration for object detection

### Loader Components

The loader modules are located in [`open_webui/backend/open_webui/retrieval/loaders/`](https://github.com/IntelliBridge/open-webui/tree/3e6f1bb2d5c949f35d0b4aacf9cec56cee2d2fae/backend/open_webui/retrieval/loaders):

- **icd_loader.py** - Custom document loader implementation
- **main.py** - Main loader entry point that calls the custom loader when the engine is selected

## Key Features

### Table Preservation

The primary enhancement of this custom scraper is its ability to maintain table formatting during document extraction. Traditional scraping approaches often convert tables into plain text paragraphs, losing crucial structural information. This implementation:

- Detects tables within PDF documents using Camelot
- Preserves row and column relationships
- Maintains cell boundaries and formatting
- Outputs tables in a structured format suitable for downstream processing

### Modified Unstructured Components

Several files from the Unstructured library have been copied and modified to:

1. **Update code with custom functionality** - Enhanced processing logic tailored for the Open WebUI use case
2. **Ensure proper imports** - Modified import statements to work within the Open WebUI module structure
3. **Maintain independence** - Code dependencies are self-contained within the scraper folder, independent of the original Unstructured library installation

## Why Not Use Method Overriding?

**Important Caveat**: The Unstructured library does not follow an Object-Oriented Programming (OOP) approach. Instead, it uses pure functions for document partitioning (e.g., `partition()`, `partition_pdf()`). These are standalone functions rather than class methods, which means:

- Traditional OOP patterns like inheritance and method overriding cannot be applied
- Functions cannot be subclassed or have their behavior modified through inheritance
- Custom functionality requires copying and modifying the source files directly

This architectural decision in Unstructured necessitated the approach of duplicating and customizing the relevant source files rather than extending them through inheritance.

## Usage

The custom loader is automatically invoked when the appropriate scraping engine is selected in Open WebUI. The system will:

1. Detect PDF documents requiring processing
2. Route them through `icd_loader.py`
3. Apply the enhanced scraping logic with table preservation
4. Return structured document elements ready for indexing and retrieval

## Integration Points

```
open_webui/backend/open_webui/retrieval/
├── loaders/
│   ├── main.py              # Entry point - routes to icd_loader when selected
│   └── icd_loader.py        # Custom loader implementation
└── scrapers/
    ├── base.py
    ├── custom_partition.py
    ├── layout.py
    ├── partition_pdf_camelot.py  # Core Unstructured + Camelot integration
    ├── utils.py
    └── yolox.py
```

## Dependencies

This custom scraper requires:

- Unstructured library (base functionality)
- Camelot-py (table extraction)
- Associated dependencies from both libraries

Ensure these are installed in your Open WebUI container environment.

## Contributing

When modifying the scraper components:

1. Maintain compatibility with the Open WebUI retrieval system
2. Ensure imports are properly configured for the module structure
3. Test table extraction thoroughly with various PDF formats
4. Document any new custom functionality added to the Unstructured-derived code

## References

- [Unstructured Library](https://github.com/Unstructured-IO/unstructured)
- [Camelot Documentation](https://camelot-py.readthedocs.io/)
- [Open WebUI](https://github.com/open-webui/open-webui)
