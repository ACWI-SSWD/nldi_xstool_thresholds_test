# nldi_xstool_thresholds_test
Example of nldi_xstool use for USGS NGWOS R&D Thresholds project

# Create conda environment for project:

## setup conda environment

conda create -n pygeoapi_xstool python=3.9 gdal fiona
conda activate pygeoapi_xstool

## install nldi_xstool
# Note: 3 installs below are short-term fix to packages used by nldi_xstool

pip install git+https://github.com/cheginit/pygeoogc.git
pip install git+https://github.com/cheginit/pygeoutils.git
pip install git+https://github.com/cheginit/py3dep.git
pip install git+https://github.com/ACWI-SSWD/nldi_xstool.git
