# spectral-python-magic

This is a Python 3 implementation of the "Spectral Magic" MATLAB codebase originally written by Blair Rossetti. This implementation now has entirely open-access requirements.

This is a kit-based system, e.g., the plan is for you to download this as a directory which you can move around your computer, load your raw CZIs into the `input` directory, reference spectra into `reference`, run the code, and your unmixed TIFF stacks will "magically" appear in the `output` directory.

### What this has and doesn't have: 
CAN DO:
   * loop through as many files as you put into the input folder
   * ignore all non-xls files in `reference`
   * run faster than the MATLAB version \~happy face\~
   * loop through z-stacks
   * detect and handle whether used with a beamsplitter (e.g. multiple lasers per CZI but only one reference file) or multiple lasers used on a single frame (single laser per CZI, same base file name, reference file names.
   * channel-select to retain only specific unmixed channels from a given laser
   * store physical pixel size in metadata (for easy ImageJ scale bar)
   * _theoretically_ handle z-stacks acquired with multiple single shots (e.g. 30 czi files from 5 lasers each at 6 z-planes, all labelled something like ROOT\_L\_Z.czi, should be able to be unmixed using the 5 reference files into a single unmixed Z-stack of ROOT-unmixed.tiff

CANNOT DO
   * what else should it do?

# Installation:

Dependencies are simple so there is a good chance you have these packages already, so if you do any amount of scientific Python, you should be good to just download the codebase and run. But, here's some directions, assuming you already have Python 3.x.x and pip installed (If you don't have python already, don't worry, the internet is full of very straightforward directions for installing) 

1. Acquire the code kit via zip here on GitHub, or via git on the command line. Example:

```
cd 
git clone https://github.com/dutter/spectral-python-magic
cd spectral-python-magic
```

2. Run `python --version` and make sure the output starts with 3 to double check that you're working with Python 3

3. Make sure you have all the dependencies: `pip install -r requirements.txt`
   * Or just `pip install numpy pandas xlrd scipy`

4. Add a test CZI to the `input` directory, an appropriate reference `.xls` file to the `reference` directory, and execute the program by running `python spectral-python-magic.py` (from within the `spectral-python-magic` directory, of course) and watch it fly!

5. Not working? Sorry. Try emailing me?


# Notes on usage:

For single-shot mode (e.g. images in `input` were each taken with a single laser but there are multiple reference files to choose from in `reference`), the reference file _MUST_ contain the laser name somewhere. It can parse "Reference\_488.xls", "488.xls", "MyFavoriteBeamsplitter488.xls", etc. Which laser's reference to use is based on the laser parsed from the metadata - the unmixer should print this to stdout for each file processed (to help troubleshoot if Zeiss changes metadata significantly).

For cases where multiple files need to be merged, such as z-stacks or multiple single laser shots, a single output file will be saved based on the root filename. Root being defined as every part of the filename that is NOT of the format `_LASER_`. For example, `NiceImage_488_s001.czi NiceImage_488_s001.czi ... NiceImage_633_s001.czi` would all be unmixed and concatenated into `NiceImage_s001-unmixed.tiff`. Similarly, `PrettyPicture_Laser488.czi` would become `PrettyPicture-unmixed.tiff`

If you want to only retain certain channels, simply modify the block of code that starts with `channelSelector`. The format is `"Laser": ["List", "of", "channel", "names", "to", "keep"]` Here, you only need a unique subset of the column names in the corresponding reference file. Names need not be complete, for instance, `At550` will match the reference column `MBL_At550` etc.

