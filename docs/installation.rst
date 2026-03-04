Installation Guide
==================

Requirements
------------

- Python 3.10 or higher
- CUDA 11.8+ (optional, for GPU acceleration)
- 8GB RAM minimum (16GB recommended)
- 20GB disk space for full datasets

Install from PyPI
-----------------

The easiest way to install STRATICA is via pip:

.. code-block:: bash

   pip install stratica

Install from Source
-------------------

For the latest development version, install from GitHub:

.. code-block:: bash

   git clone https://github.com/gitdeeper8/STRATICA.git
   cd STRATICA
   pip install -e .

Install with GPU Support
------------------------

For GPU acceleration (requires CUDA 11.8+):

.. code-block:: bash

   pip install stratica[gpu]

Install with Development Dependencies
-------------------------------------

For contributing to STRATICA development:

.. code-block:: bash

   git clone https://github.com/gitdeeper8/STRATICA.git
   cd STRATICA
   pip install -e ".[dev]"
   pre-commit install

Verify Installation
-------------------

Check that STRATICA is installed correctly:

.. code-block:: bash

   python -c "import stratica; print(stratica.__version__)"
   stratica --help

Docker Installation
-------------------

You can also run STRATICA using Docker:

.. code-block:: bash

   docker pull gitlab.com/gitdeeper8/stratica:latest
   docker run -p 8000:8000 -p 8501:8501 stratica:latest
