# spectral-python-magic

This is a Python 3 implementation of the "Spectral Magic" MATLAB codebase originally written by Blair Rossetti. This implementation now has entirely open-access requirements.

This is a kit-based system, e.g., the plan is for you to download this as a directory which you can move around your computer, load your raw CZIs into the `input` directory, reference spectra into `reference`, run the code, and your unmixed TIFF stacks will "magically" appear in the `output` directory.

### What this has and doesn't have: 
CAN DO:
   * loop through as many files as you put into the input folder
   * ignore all non-xls files in `reference`
   * run faster than the MATLAB version ~happy face~
CANNOT DO
   * parse z-stacks
   * extract metadata from the czi to chose the correct unmixing file
   * take command line arguments. Potentially, this could be written as a standalone program that is executed something more like `spectral-python-magic --input-dir /path/to/input --reference /path/to/ref --output /path/to/output [other tags]` But currently, that's not how it works.

# Installation:

We recommend creating a virtual environment to make sure everything works nicely. But, dependencies are simple so there is a good chance you have these packages already, so if you do any amount of scientific Python, you should be good to just install and run. 

We assume you already have Python 3.x.x and pip installed.

1. Acquire the code kit via zip here on GitHub, or via git on the command line. Example:

```
cd 
git clone https://github.com/dutter/spectral-python-magic
cd spectral-python-magic
```

2. Run `python --version` and make sure the output starts with 3 to double check that you're working with Python 3

3. Make sure you have all the dependencies - `pip install -r requirements.txt`
   * Or just `pip install numpy pandas xlrd scipy'

4. Add a test CZI to the `input` directory, an appropriate reference `.xls` file to the `reference` directory, and execute the program by running `python spectral-python-magic.py' (from within the `spectral-python-magic` directory, of course)' and watch it fly!

5. Not working? Sorry. Try emailing me?

