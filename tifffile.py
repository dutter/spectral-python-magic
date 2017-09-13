#! /usr/bin/python3
# -*- coding: utf-8 -*-
# tifffile.py

# Copyright (c) 2008-2017, Christoph Gohlke
# Copyright (c) 2008-2017, The Regents of the University of California
# Produced at the Laboratory for Fluorescence Dynamics
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright holders nor the names of any
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Read image and meta data from (bio)TIFF files. Save numpy arrays as TIFF.

Image and metadata can be read from TIFF, BigTIFF, OME-TIFF, STK, LSM, NIH,
SGI, ImageJ, MicroManager, FluoView, SEQ and GEL files.
Only a subset of the TIFF specification is supported, mainly uncompressed
and losslessly compressed 2**(0 to 6) bit integer, 16, 32 and 64-bit float,
grayscale and RGB(A) images, which are commonly used in bio-scientific imaging.
Specifically, reading JPEG and CCITT compressed image data, chroma subsampling,
or EXIF, IPTC, GPS, and XMP metadata is not implemented. Only primary info
records are read for STK, FluoView, MicroManager, and NIH Image formats.

TIFF, the Tagged Image File Format aka Thousands of Incompatible File Formats,
is under the control of Adobe Systems. BigTIFF allows for files greater than
4 GB. STK, LSM, FluoView, SGI, SEQ, GEL, and OME-TIFF, are custom extensions
defined by Molecular Devices (Universal Imaging Corporation), Carl Zeiss
MicroImaging, Olympus, Silicon Graphics International, Media Cybernetics,
Molecular Dynamics, and the Open Microscopy Environment consortium
respectively.

For command line usage run C{python -m tifffile --help}

:Author:
  `Christoph Gohlke <http://www.lfd.uci.edu/~gohlke/>`_

:Organization:
  Laboratory for Fluorescence Dynamics, University of California, Irvine

:Version: 2017.07.21.dev

Requirements
------------
* `CPython 3.6 64-bit <http://www.python.org>`_
* `Numpy 1.13 <http://www.numpy.org>`_
* `Matplotlib 2.0 <http://www.matplotlib.org>`_ (optional for plotting)
* `Tifffile.c 2017.01.10 <http://www.lfd.uci.edu/~gohlke/>`_
  (recommended for faster decoding of PackBits and LZW encoded strings)

Revisions
---------
2017.07.21.dev (tentative)
    Many backwards incompatible changes improving speed and resource usage:
    Pass 2267 tests.
    Replace nih_image_header tag and attribute with nih_metadata dict.
    Rename imagej_tags attribute to imagej_metadata.
    Remove cz_lsm attributes; use lsm_metadata instead.
    Consolidate LSM lsm_scan_info header and subrecords in lsm_metadata dict.
    Add function to convert LSM to tiled BIN files.
    Align image data in file.
    Make TiffPage.dtype a numpy.dtype.
    Allow imsave to write non-BigTIFF files up to ~4 GB.
    Only read one page for shaped series if possible.
    Return offset and bytecounts of contiguous data from TiffWriter.save.
    Add memmap function to create memory-mapped array stored in TIFF file.
    Add option to save empty arrays to TIFF files.
    Add option to save truncated TIFF files.
    Allow single tile images to be saved contiguously.
    Only return main image series for LSM files.
    Add optional movie mode for files with uniform pages.
    Lazy load pages.
    Use lightweight TiffFrame for IFDs sharing properties with key TiffPage.
    Move module constants to 'CONST' namespace (speed up module import).
    Remove 'fastij' option from TiffFile.
    Remove 'pages' parameter from TiffFile.
    Remove TIFFfile alias.
    Deprecate Python 2.
    Remove Record and return all metadata as dict or numpy.record instead.
    Add functions to parse STK, MetaSeries, ScanImage, SVS, Pilatus metadata.
    Read tags from EXIF and GPS IFDs.
    Use pprint for info strings.
    Fix reading some UIC tags (bug fix).
    Do not modify input array in imshow (bug fix).
    Fix Python implementation of unpack_ints.
2017.05.23
    Pass 1961 tests.
    Write correct number of sample_format values (bug fix).
    Use Adobe deflate code to write ZIP compressed files.
    Add option to pass tag values as packed binary data for writing.
    Defer tag validation to attribute access.
    Use property instead of lazyattr decorator for simple expressions.
2017.03.17
    Write IFDs and tag values on word boundaries.
    Read ScanImage metadata.
    Remove is_rgb and is_indexed attributes from TiffFile.
    Create files used by doctests.
2017.01.12
    Read Zeiss SEM metadata.
    Read OME-TIFF with invalid references to external files.
    Rewrite C LZW decoder (5x faster).
    Read corrupted LSM files missing EOI code in LZW stream.
2017.01.01
    Add option to append images to existing TIFF files.
    Read files without pages.
    Read S-FEG and Helios NanoLab tags created by FEI software.
    Allow saving Color Filter Array (CFA) images.
    Add info functions returning more information about TiffFile and TiffPage.
    Add option to read specific pages only.
    Remove maxpages argument (backwards incompatible).
    Remove test_tifffile function.
2016.10.28
    Pass 1944 tests.
    Improve detection of ImageJ hyperstacks.
    Read TVIPS metadata created by EM-MENU (by Marco Oster).
    Add option to disable using OME-XML metadata.
    Allow non-integer range attributes in modulo tags (by Stuart Berg).
2016.06.21
    Do not always memmap contiguous data in page series.
2016.05.13
    Add option to specify resolution unit.
    Write grayscale images with extra samples when planarconfig is specified.
    Do not write RGB color images with 2 samples.
    Reorder TiffWriter.save keyword arguments (backwards incompatible).
2016.04.18
    Pass 1932 tests.
    TiffWriter, imread, and imsave accept open binary file streams.
2016.04.13
    Correctly handle reversed fill order in 2 and 4 bps images (bug fix).
    Implement reverse_bitorder in C.
2016.03.18
    Fix saving additional ImageJ metadata.
2016.02.22
    Pass 1920 tests.
    Write 8 bytes double tag values using offset if necessary (bug fix).
    Add option to disable writing second image description tag.
    Detect tags with incorrect counts.
    Disable color mapping for LSM.
2015.11.13
    Read LSM 6 mosaics.
    Add option to specify directory of memory-mapped files.
    Add command line options to specify vmin and vmax values for colormapping.
2015.10.06
    New helper function to apply colormaps.
    Renamed is_palette attributes to is_indexed (backwards incompatible).
    Color-mapped samples are now contiguous (backwards incompatible).
    Do not color-map ImageJ hyperstacks (backwards incompatible).
    Towards supporting Leica SCN.
2015.09.25
    Read images with reversed bit order (fill_order is lsb2msb).
2015.09.21
    Read RGB OME-TIFF.
    Warn about malformed OME-XML.
2015.09.16
    Detect some corrupted ImageJ metadata.
    Better axes labels for 'shaped' files.
    Do not create TiffTag for default values.
    Chroma subsampling is not supported.
    Memory-map data in TiffPageSeries if possible (optional).
2015.08.17
    Pass 1906 tests.
    Write ImageJ hyperstacks (optional).
    Read and write LZMA compressed data.
    Specify datetime when saving (optional).
    Save tiled and color-mapped images (optional).
    Ignore void byte_counts and offsets if possible.
    Ignore bogus image_depth tag created by ISS Vista software.
    Decode floating point horizontal differencing (not tiled).
    Save image data contiguously if possible.
    Only read first IFD from ImageJ files if possible.
    Read ImageJ 'raw' format (files larger than 4 GB).
    TiffPageSeries class for pages with compatible shape and data type.
    Try to read incomplete tiles.
    Open file dialog if no filename is passed on command line.
    Ignore errors when decoding OME-XML.
    Rename decoder functions (backwards incompatible)
2014.08.24
    TiffWriter class for incremental writing images.
    Simplify examples.
2014.08.19
    Add memmap function to FileHandle.
    Add function to determine if image data in TiffPage is memory-mappable.
    Do not close files if multifile_close parameter is False.
2014.08.10
    Pass 1730 tests.
    Return all extrasamples by default (backwards incompatible).
    Read data from series of pages into memory-mapped array (optional).
    Squeeze OME dimensions (backwards incompatible).
    Workaround missing EOI code in strips.
    Support image and tile depth tags (SGI extension).
    Better handling of STK/UIC tags (backwards incompatible).
    Disable color mapping for STK.
    Julian to datetime converter.
    TIFF ASCII type may be NULL separated.
    Unwrap strip offsets for LSM files greater than 4 GB.
    Correct strip byte counts in compressed LSM files.
    Skip missing files in OME series.
    Read embedded TIFF files.
2014.02.05
    Save rational numbers as type 5 (bug fix).
2013.12.20
    Keep other files in OME multi-file series closed.
    FileHandle class to abstract binary file handle.
    Disable color mapping for bad OME-TIFF produced by bio-formats.
    Read bad OME-XML produced by ImageJ when cropping.
2013.11.03
    Allow zlib compress data in imsave function (optional).
    Memory-map contiguous image data (optional).
2013.10.28
    Read MicroManager metadata and little endian ImageJ tag.
    Save extra tags in imsave function.
    Save tags in ascending order by code (bug fix).
2012.10.18
    Accept file like objects (read from OIB files).
2012.08.21
    Rename TIFFfile to TiffFile and TIFFpage to TiffPage.
    TiffSequence class for reading sequence of TIFF files.
    Read UltraQuant tags.
    Allow float numbers as resolution in imsave function.
2012.08.03
    Read MD GEL tags and NIH Image header.
2012.07.25
    Read ImageJ tags.
    ...

Notes
-----
The API is not stable yet and might change between revisions.

Tested on little-endian platforms only.

TIFF trees defined via sub_ifds tags are not supported.

Other Python packages and modules for reading bio-scientific TIFF files:

*  `python-bioformats <https://github.com/CellProfiler/python-bioformats>`_
*  `Imread <https://github.com/luispedro/imread>`_
*  `PyLibTiff <https://github.com/pearu/pylibtiff>`_
*  `SimpleITK <http://www.simpleitk.org>`_
*  `PyLSM <https://launchpad.net/pylsm>`_
*  `PyMca.TiffIO.py <https://github.com/vasole/pymca>`_ (same as fabio.TiffIO)
*  `BioImageXD.Readers <http://www.bioimagexd.net/>`_
*  `Cellcognition.io <http://cellcognition.org/>`_
*  `pymimage <https://github.com/ardoi/pymimage>`_

Acknowledgements
----------------
*   Egor Zindy, University of Manchester, for lsm_scan_info specifics.
*   Wim Lewis for a bug fix and some read_lsm functions.
*   Hadrien Mary for help on reading MicroManager files.
*   Christian Kliche for help writing tiled and color-mapped files.

References
----------
1)  TIFF 6.0 Specification and Supplements. Adobe Systems Incorporated.
    http://partners.adobe.com/public/developer/tiff/
2)  TIFF File Format FAQ. http://www.awaresystems.be/imaging/tiff/faq.html
3)  MetaMorph Stack (STK) Image File Format.
    http://support.meta.moleculardevices.com/docs/t10243.pdf
4)  Image File Format Description LSM 5/7 Release 6.0 (ZEN 2010).
    Carl Zeiss MicroImaging GmbH. BioSciences. May 10, 2011
5)  The OME-TIFF format.
    http://www.openmicroscopy.org/site/support/file-formats/ome-tiff
6)  UltraQuant(r) Version 6.0 for Windows Start-Up Guide.
    http://www.ultralum.com/images%20ultralum/pdf/UQStart%20Up%20Guide.pdf
7)  Micro-Manager File Formats.
    http://www.micro-manager.org/wiki/Micro-Manager_File_Formats
8)  Tags for TIFF and Related Specifications. Digital Preservation.
    http://www.digitalpreservation.gov/formats/content/tiff_tags.shtml
9)  ScanImage BigTiff Specification - ScanImage 2016.
    http://scanimage.vidriotechnologies.com/display/SI2016/
    ScanImage+BigTiff+Specification
10) CIPA DC-008-2016: Exchangeable image file format for digital still cameras:
    Exif Version 2.31.
    http://www.cipa.jp/std/documents/e/DC-008-Translation-2016-E.pdf

Examples
--------
# >>> data = numpy.random.rand(5, 301, 219)
# >>> imsave('temp.tif', data)
# >>> image = imread('temp.tif')
# >>> numpy.testing.assert_array_equal(image, data)
#
# >>> with TiffFile('temp.tif') as tif:
# ...     images = tif.asarray()
# ...     for page in tif.pages:
# ...         for tag in page.tags.values():
# ...             _ = tag.name, tag.value
# ...         image = page.asarray()
#
"""

from __future__ import division, print_function

import sys
import os
import re
import glob
import math
import zlib
import time
import json
import struct
import warnings
import tempfile
import datetime
import collections
# from fractions import Fraction  # delay import
# from xml.etree import cElementTree as etree  # delay import

import numpy

try:
    import lzma
except ImportError:
    try:
        import backports.lzma as lzma
    except ImportError:
        lzma = None

__version__ = '2017.07.21.dev'
__docformat__ = 'restructuredtext en'
__all__ = (
    'imsave', 'imread', 'imshow', 'memmap',
    'TiffFile', 'TiffWriter', 'TiffSequence',
    # utility functions used by oiffile or czifile
    'FileHandle', 'lazyattr', 'natural_sorted', 'decode_lzw', 'stripnull',
    'repeat_nd', 'format_size', 'product')


def imread(files, **kwargs):
    """Return image data from TIFF file(s) as numpy array.

    Refer to the TiffFile class and member functions for documentation.

    Parameters
    ----------
    files : str, binary stream, or sequence
        File name, seekable binary stream, glob pattern, or sequence of
        file names.
    kwargs : dict
        Parameters 'multifile', 'multifile_close', and 'is_ome' are passed
        to the TiffFile class.
        The 'pattern' parameter is passed to the TiffSequence class.
        Other parameters are passed to the asarray functions.
        The first image series is returned if no arguments are provided.

    Examples
    --------
    >>> imsave('temp.tif', numpy.random.rand(3, 4, 301, 219))
    >>> im = imread('temp.tif', key=0)
    >>> im.shape
    (4, 301, 219)

    >>> ims = imread(['temp.tif', 'temp.tif'])
    >>> ims.shape
    (2, 3, 4, 301, 219)

    """
    kwargs_file = parse_kwargs(kwargs, 'multifile', 'multifile_close',
                               'is_ome')
    kwargs_seq = parse_kwargs(kwargs, 'pattern')

    if isinstance(files, basestring) and any(i in files for i in '?*'):
        files = glob.glob(files)
    if not files:
        raise ValueError('no files found')
    if not hasattr(files, 'seek') and len(files) == 1:
        files = files[0]

    if isinstance(files, basestring) or hasattr(files, 'seek'):
        with TiffFile(files, **kwargs_file) as tif:
            return tif.asarray(**kwargs)
    else:
        with TiffSequence(files, **kwargs_seq) as imseq:
            return imseq.asarray(**kwargs)


def imsave(file, data=None, shape=None, dtype=None, bigsize=2**32-2**25,
           **kwargs):
    """Write image data to TIFF file.

    If data is None, an empty array of the specified shape and dtype is
    saved to file.
    If the image data are written contiguously, return offset and bytecount
    of image data in the file.
    Refer to the TiffWriter class and member functions for documentation.

    Parameters
    ----------
    file : str or binary stream
        File name or writable binary stream, such as a open file or BytesIO.
    data : array_like
        Input image. The last dimensions are assumed to be image depth,
        height, width, and samples.
    shape : tuple
        If data is None, shape of an empty array to save to the file.
    dtype : numpy.dtype
        If data is None, data-type of an empty array to save to the file.
    bigsize : int
        Create a BigTIFF file if the size of data in bytes is larger than
        this threshold and 'imagej' or 'truncate' are not enabled.
        By default, the threshold is 4 GB minus 32 MB reserved for metadata.
        Use the 'bigtiff' parameter to explicitly specify the type of
        file created.
    kwargs : dict
        Parameters 'append', 'byteorder', 'bigtiff', 'software', and 'imagej',
        are passed to TiffWriter().
        Other parameters are passed to TiffWriter.save().

    Examples
    --------
    >>> data = numpy.random.rand(2, 5, 3, 301, 219)
    >>> imsave('temp.tif', data, compress=6, metadata={'axes': 'TZCYX'})

    """
    tifargs = parse_kwargs(kwargs, 'append', 'bigtiff', 'byteorder',
                           'software', 'imagej')
    if data is None:
        size = product(shape) * numpy.dtype(dtype).itemsize
    else:
        try:
            size = data.size * data.dtype.itemsize
        except:
            size = 0
    if size > bigsize and 'bigtiff' not in tifargs and not (
            tifargs.get('imagej', False) or tifargs.get('truncate', False)):
        tifargs['bigtiff'] = True

    with TiffWriter(file, **tifargs) as tif:
        return tif.save(data, shape, dtype, **kwargs)


def memmap(filename, shape=None, dtype=None, page=None, series=0, mode='r+',
           **kwargs):
    """Return memory-mapped numpy array stored in TIFF file.

    Memory-mapping requires data stored in native byte order, without tiling,
    compression, predictors, etc.
    If shape and dtype are provided, existing files will be overwritten or
    appended to depending on the 'append' parameter.
    Otherwise the image data of a specified page or series in an existing
    file will be memory-mapped. By default, the image data of the first page
    series is memory-mapped.
    Call flush() to write any changes in the array to the file.
    Raise ValueError if the image data in the file is not memory-mappable

    Parameters
    ----------
    filename : str
        Name of the TIFF file which stores the array.
    shape : tuple
        Shape of the empty array.
    dtype : numpy.dtype
        Data-type of the empty array.
    page : int
        Index of the page which image data to memory-map.
    series : int
        Index of the page series which image data to memory-map.
    mode : {'r+', 'r', 'c'}, optional
        The file open mode. Default is to open existing file for reading and
        writing ('r+').
    kwargs : dict
        Additional parameters passed to imsave() or TiffFile().

    Examples
    --------
    >>> im = memmap('temp.tif', shape=(256, 256), dtype='float32')
    >>> im[255, 255] = 1.0
    >>> im.flush()
    >>> im.shape, im.dtype
    ((256, 256), dtype('float32'))
    >>> del im

    >>> im = memmap('temp.tif', page=0)
    >>> im[255, 255]
    1.0

    """
    if shape is not None and dtype is not None:
        # create a new, empty array
        kwargs.update(data=None, shape=shape, dtype=dtype, return_offset=True,
                      align=CONST.ALLOCATIONGRANULARITY)
        result = imsave(filename, **kwargs)
        if result is None:
            # TODO: fail before creating file or writing data
            raise ValueError("image data is not memory-mappable")
        offset = result[0]
    else:
        # use existing file
        with TiffFile(filename, **kwargs) as tif:
            if page is not None:
                page = tif.pages[page]
                if not page.is_memmappable(False, False):
                    raise ValueError("image data is not memory-mappable")
                offset, _ = page.is_contiguous
                shape = page.shape
                dtype = page.dtype
            else:
                series = tif.series[series]
                if series.offset is None:
                    raise ValueError("image data is not memory-mappable")
                shape = series.shape
                dtype = series.dtype
                offset = series.offset
    return numpy.memmap(filename, dtype, mode, offset, shape, 'C')


class lazyattr(object):
    """Attribute whose value is computed on first access."""
    # TODO: help() doesn't work
    __slots__ = ('func',)

    def __init__(self, func):
        self.func = func
        # self.__name__ = func.__name__
        # self.__doc__ = func.__doc__
        # self.lock = threading.RLock()

    def __get__(self, instance, owner):
        # with self.lock:
        if instance is None:
            return self
        try:
            value = self.func(instance)
        except AttributeError as e:
            raise RuntimeError(e)
        if value is NotImplemented:
            return getattr(super(owner, instance), self.func.__name__)
        setattr(instance, self.func.__name__, value)
        return value


class TiffWriter(object):
    """Write image data to TIFF file.

    TiffWriter instances must be closed using the 'close' method, which is
    automatically called when using the 'with' context manager.

    Examples
    --------
    >>> data = numpy.random.rand(2, 5, 3, 301, 219)
    >>> with TiffWriter('temp.tif', bigtiff=True) as tif:
    ...     for i in range(data.shape[0]):
    ...         tif.save(data[i], compress=6)

    """
    def __init__(self, file, bigtiff=False, byteorder=None,
                 software='tifffile.py', append=False, imagej=False):
        """Open a TIFF file for writing.

        A empty TIFF file is created if the file does not exist, else the file
        is overwritten unless append=True.
        Use bigtiff=True when creating files larger than 4 GB.

        Parameters
        ----------
        file : str, binary stream, or FileHandle
            File name or writable binary stream, such as a open file
            or BytesIO.
        bigtiff : bool
            If True, the BigTIFF format is used.
        byteorder : {'<', '>'}
            The endianness of the data in the file.
            By default, this is the system's native byte order.
        software : str
            Name of the software used to create the file.
            Saved with the first page in the file only.
        append : bool
            If True and 'file' is an existing standard TIFF file, image data
            and tags are appended to the file.
            Appending data may corrupt specifically formatted TIFF files
            such as LSM, STK, ImageJ, NIH, or FluoView.
        imagej : bool
            If True, write an ImageJ hyperstack compatible file.
            This format can handle data types uint8, uint16, or float32 and
            data shapes up to 6 dimensions in TZCYXS order.
            RGB images (S=3 or S=4) must be uint8.
            ImageJ's default byte order is big endian but this implementation
            uses the system's native byte order by default.
            ImageJ does not support BigTIFF format or LZMA compression.
            The ImageJ file format is undocumented.

        """
        if append:
            # determine if file is an existing TIFF file that can be extended
            try:
                with FileHandle(file, mode='rb', size=0) as fh:
                    pos = fh.tell()
                    try:
                        with TiffFile(fh) as tif:
                            if (append != 'force' and
                                any(getattr(tif, 'is_'+a) for a in
                                    ('lsm', 'stk', 'imagej', 'nih', 'fluoview',
                                     'micromanager'))):
                                raise ValueError("file contains metadata")
                            byteorder = tif.byteorder
                            bigtiff = tif.is_bigtiff
                            self._ifd_offset = tif.pages.next_page_offset
                            if tif.pages:
                                software = None
                    except Exception as e:
                        raise ValueError("can not append to file: %s" % str(e))
                    finally:
                        fh.seek(pos)
            except (IOError, FileNotFoundError):
                append = False

        if byteorder in (None, '='):
            byteorder = '<' if sys.byteorder == 'little' else '>'
        elif byteorder not in ('<', '>'):
            raise ValueError("invalid byteorder %s" % byteorder)
        if imagej and bigtiff:
            warnings.warn("writing incompatible BigTIFF ImageJ")

        self._byteorder = byteorder
        self._software = software
        self._imagej = bool(imagej)
        self._truncate = False
        self._metadata = None
        self._colormap = None

        self._description_offset = 0
        self._description_len_offset = 0
        self._description_len = 0

        self._tags = None
        self._shape = None  # normalized shape of data in consecutive pages
        self._data_shape = None  # shape of data in consecutive pages
        self._data_dtype = None  # data type
        self._data_offset = None  # offset to data
        self._data_byte_counts = None  # byte counts per plane
        self._tag_offsets = None  # strip or tile offset tag code

        if bigtiff:
            self._bigtiff = True
            self._offset_size = 8
            self._tag_size = 20
            self._tagno_format = 'Q'
            self._offset_format = 'Q'
            self._value_format = '8s'
        else:
            self._bigtiff = False
            self._offset_size = 4
            self._tag_size = 12
            self._tagno_format = 'H'
            self._offset_format = 'I'
            self._value_format = '4s'

        if append:
            self._fh = FileHandle(file, mode='r+b', size=0)
            self._fh.seek(0, 2)
        else:
            self._fh = FileHandle(file, mode='wb', size=0)
            self._fh.write({'<': b'II', '>': b'MM'}[byteorder])
            if bigtiff:
                self._fh.write(struct.pack(byteorder+'HHH', 43, 8, 0))
            else:
                self._fh.write(struct.pack(byteorder+'H', 42))
            # first IFD
            self._ifd_offset = self._fh.tell()
            self._fh.write(struct.pack(byteorder+self._offset_format, 0))

    def save(self, data=None, shape=None, dtype=None, return_offset=False,
             photometric=None, planarconfig=None, tile=None,
             contiguous=True, align=16, truncate=False, compress=0,
             colormap=None, description=None, datetime=None, resolution=None,
             metadata={}, extratags=()):
        """Write image data and tags to TIFF file.

        The data shape's last dimensions are assumed to be image depth,
        height (length), width, and samples.
        If a colormap is provided, the dtype must be uint8 or uint16 and
        the data values are indices into the last dimension of the
        colormap.
        If shape and dtype are specified, an empty array is saved.
        This option can not be used with compression or multiple tiles.
        Image data are written in one stripe per plane by default.
        Dimensions larger than 2 to 4 (depending on photometric mode, planar
        configuration, and SGI mode) are flattened and saved as separate pages.
        The 'sample_format' and 'bits_per_sample' tags are derived from
        the data type.

        Parameters
        ----------
        data : numpy.ndarray or None
            Input image array.
        shape : tuple or None
            Shape of the empty array to save. Used only if data is None.
        dtype : numpy.dtype or None
            Data-type of the empty array to save. Used only if data is None.
        return_offset : bool
            If True and the image data in the file is memory-mappable, return
            the offset and number of bytes of the image data in the file.
        photometric : {'minisblack', 'miniswhite', 'rgb', 'palette', 'cfa'}
            The color space of the image data.
            By default, this setting is inferred from the data shape and the
            value of colormap.
            For CFA images, DNG tags must be specified in extratags.
        planarconfig : {'contig', 'planar'}
            Specifies if samples are stored contiguous or in separate planes.
            By default, this setting is inferred from the data shape.
            If this parameter is set, extra samples are used to store grayscale
            images.
            'contig': last dimension contains samples.
            'planar': third last dimension contains samples.
        tile : tuple of int
            The shape (depth, length, width) of image tiles to write.
            If None (default), image data are written in one stripe per plane.
            The tile length and width must be a multiple of 16.
            If the tile depth is provided, the SGI image_depth and tile_depth
            tags are used to save volume data.
            Unless a single tile is used, tiles cannot be used to write
            contiguous files.
            Few software can read the SGI format, e.g. MeVisLab.
        contiguous : bool
            If True (default) and the data and parameters are compatible with
            previous ones, if any, the image data are stored contiguously after
            the previous one. Parameters 'photometric' and 'planarconfig' are
            ignored.
        align : int
            Byte boundary on which to align the image data in the file.
            Default 16. Use mmap.ALLOCATIONGRANULARITY for memory-mapped data.
            Following contiguous writes are not aligned.
        truncate : bool
            If True, only write the first page including shape metadata if
            possible (uncompressed, contiguous, not tiled).
            Other TIFF readers will only be able to read part of the data.
        compress : int or 'lzma'
            Values from 0 to 9 controlling the level of zlib compression.
            If 0, data are written uncompressed (default).
            Compression cannot be used to write contiguous files.
            If 'lzma', LZMA compression is used, which is not available on
            all platforms.
        colormap : numpy.ndarray
            RGB color values for the corresponding data value.
            Must be of shape (3, 2**(data.itemsize*8)) and dtype uint16.
        description : str
            The subject of the image. Saved with the first page only.
            Cannot be used with the ImageJ format.
        datetime : datetime
            Date and time of image creation. Saved with the first page only.
            If None (default), the current date and time is used.
        resolution : (float, float[, str]) or ((int, int), (int, int)[, str])
            X and Y resolutions in pixels per resolution unit as float or
            rational numbers.
            A third, optional parameter specifies the resolution unit,
            which must be None (default for ImageJ), 'inch' (default), or 'cm'.
        metadata : dict
            Additional meta data to be saved along with shape information
            in JSON or ImageJ formats in an image_description tag.
            If None, do not write a second image_description tag.
        extratags : sequence of tuples
            Additional tags as [(code, dtype, count, value, writeonce)].

            code : int
                The TIFF tag Id.
            dtype : str
                Data type of items in 'value' in Python struct format.
                One of B, s, H, I, 2I, b, h, i, 2i, f, d, Q, or q.
            count : int
                Number of data values. Not used for string or byte string
                values.
            value : sequence
                'Count' values compatible with 'dtype'.
                Byte strings must contain count values of dtype packed as
                binary data.
            writeonce : bool
                If True, the tag is written to the first page only.

        """
        # TODO: refactor this function
        fh = self._fh
        byteorder = self._byteorder
        tagno_format = self._tagno_format
        value_format = self._value_format
        offset_format = self._offset_format
        offset_size = self._offset_size
        tag_size = self._tag_size

        if data is None:
            if compress:
                raise ValueError("can not save compressed empty file")
            data_shape = shape
            data_dtype = numpy.dtype(dtype).newbyteorder(byteorder)
            data_dtype_char = data_dtype.char
            data = None
        else:
            data = numpy.asarray(data, byteorder+data.dtype.char, 'C')
            if data.size == 0:
                raise ValueError("can not save empty array")
            data_shape = data.shape
            data_dtype = data.dtype
            data_dtype_char = data.dtype.char

        return_offset = return_offset and data_dtype.isnative
        _data_shape = data_shape  # data shape of input array
        data_size = product(data_shape) * data_dtype.itemsize

        # just append contiguous data if possible
        self._truncate = bool(truncate)
        if self._data_shape:
            if (not contiguous
                    or self._data_shape[1:] != data_shape
                    or self._data_dtype != data_dtype
                    or (compress and self._tags)
                    or tile
                    or not numpy.array_equal(colormap, self._colormap)):
                # incompatible shape, dtype, compression mode, or colormap
                self._write_remaining_pages()
                self._write_image_description()
                self._truncate = False
                self._description_offset = 0
                self._description_len_offset = 0
                self._data_shape = None
                self._colormap = None
                if self._imagej:
                    raise ValueError(
                        "ImageJ does not support non-contiguous data")
            else:
                # consecutive mode
                self._data_shape = (self._data_shape[0] + 1,) + data_shape
                if not compress:
                    # write contiguous data, write ifds/tags later
                    offset = fh.tell()
                    if data is None:
                        fh.write_empty(data_size)
                    else:
                        fh.write_array(data)
                    if return_offset:
                        return offset, data_size
                    return

        if photometric not in (None, 'minisblack', 'miniswhite',
                               'rgb', 'palette', 'cfa'):
            raise ValueError("invalid photometric %s" % photometric)
        if planarconfig not in (None, 'contig', 'planar'):
            raise ValueError("invalid planarconfig %s" % planarconfig)

        # prepare compression
        if not compress:
            compress = False
            compress_tag = 1
        elif compress == 'lzma':
            compress = lzma.compress
            compress_tag = 34925
            if self._imagej:
                raise ValueError("ImageJ can not handle LZMA compression")
        elif not 0 <= compress <= 9:
            raise ValueError("invalid compression level %s" % compress)
        elif compress:
            def compress(data, level=compress):
                return zlib.compress(data, level)
            compress_tag = 8

        # prepare ImageJ format
        if self._imagej:
            if description:
                warnings.warn("not writing description to ImageJ file")
                description = None
            volume = False
            if data_dtype_char not in 'BHhf':
                raise ValueError("ImageJ does not support data type '%s'"
                                 % data_dtype_char)
            ijrgb = photometric == 'rgb' if photometric else None
            if data_dtype_char not in 'B':
                ijrgb = False
            ijshape = imagej_shape(data_shape, ijrgb)
            if ijshape[-1] in (3, 4):
                photometric = 'rgb'
                if data_dtype_char not in 'B':
                    raise ValueError("ImageJ does not support data type '%s' "
                                     "for RGB" % data_dtype_char)
            elif photometric is None:
                photometric = 'minisblack'
                planarconfig = None
            if planarconfig == 'planar':
                raise ValueError("ImageJ does not support planar images")
            else:
                planarconfig = 'contig' if ijrgb else None

        # verify colormap and indices
        if colormap is not None:
            if data_dtype_char not in 'BH':
                raise ValueError("invalid data dtype for palette mode")
            colormap = numpy.asarray(colormap, dtype=byteorder+'H')
            if colormap.shape != (3, 2**(data_dtype.itemsize * 8)):
                raise ValueError("invalid color map shape")
            self._colormap = colormap

        # verify tile shape
        if tile:
            tile = tuple(int(i) for i in tile[:3])
            volume = len(tile) == 3
            if (len(tile) < 2 or tile[-1] % 16 or tile[-2] % 16 or
                    any(i < 1 for i in tile)):
                raise ValueError("invalid tile shape")
        else:
            tile = ()
            volume = False

        # normalize data shape to 5D or 6D, depending on volume:
        #   (pages, planar_samples, [depth,] height, width, contig_samples)
        data_shape = reshape_nd(data_shape, 3 if photometric == 'rgb' else 2)
        shape = data_shape
        ndim = len(data_shape)

        samplesperpixel = 1
        extrasamples = 0
        if volume and ndim < 3:
            volume = False
        if colormap is not None:
            photometric = 'palette'
            planarconfig = None
        if photometric is None:
            photometric = 'minisblack'
            if planarconfig == 'contig':
                if ndim > 2 and shape[-1] in (3, 4):
                    photometric = 'rgb'
            elif planarconfig == 'planar':
                if volume and ndim > 3 and shape[-4] in (3, 4):
                    photometric = 'rgb'
                elif ndim > 2 and shape[-3] in (3, 4):
                    photometric = 'rgb'
            elif ndim > 2 and shape[-1] in (3, 4):
                photometric = 'rgb'
            elif self._imagej:
                photometric = 'minisblack'
            elif volume and ndim > 3 and shape[-4] in (3, 4):
                photometric = 'rgb'
            elif ndim > 2 and shape[-3] in (3, 4):
                photometric = 'rgb'
        if planarconfig and len(shape) <= (3 if volume else 2):
            planarconfig = None
            photometric = 'minisblack'
        if photometric == 'rgb':
            if len(shape) < 3:
                raise ValueError("not a RGB(A) image")
            if len(shape) < 4:
                volume = False
            if planarconfig is None:
                if shape[-1] in (3, 4):
                    planarconfig = 'contig'
                elif shape[-4 if volume else -3] in (3, 4):
                    planarconfig = 'planar'
                elif shape[-1] > shape[-4 if volume else -3]:
                    planarconfig = 'planar'
                else:
                    planarconfig = 'contig'
            if planarconfig == 'contig':
                data_shape = (-1, 1) + shape[(-4 if volume else -3):]
                samplesperpixel = data_shape[-1]
            else:
                data_shape = (-1,) + shape[(-4 if volume else -3):] + (1,)
                samplesperpixel = data_shape[1]
            if samplesperpixel > 3:
                extrasamples = samplesperpixel - 3
        elif photometric == 'cfa':
            if len(shape) != 2:
                raise ValueError("invalid CFA image")
            volume = False
            planarconfig = None
            data_shape = (-1, 1) + shape[-2:] + (1,)
            if 50706 not in (et[0] for et in extratags):
                raise ValueError("must specify DNG tags for CFA image")
        elif planarconfig and len(shape) > (3 if volume else 2):
            if planarconfig == 'contig':
                data_shape = (-1, 1) + shape[(-4 if volume else -3):]
                samplesperpixel = data_shape[-1]
            else:
                data_shape = (-1,) + shape[(-4 if volume else -3):] + (1,)
                samplesperpixel = data_shape[1]
            extrasamples = samplesperpixel - 1
        else:
            planarconfig = None
            # remove trailing 1s
            while len(shape) > 2 and shape[-1] == 1:
                shape = shape[:-1]
            if len(shape) < 3:
                volume = False
            data_shape = (-1, 1) + shape[(-3 if volume else -2):] + (1,)

        # normalize shape to 6D
        assert len(data_shape) in (5, 6)
        if len(data_shape) == 5:
            data_shape = data_shape[:2] + (1,) + data_shape[2:]
        if data_shape[0] == -1:
            s0 = product(_data_shape) // product(data_shape[1:])
            data_shape = (s0,) + data_shape[1:]
        shape = data_shape
        if data is not None:
            data = data.reshape(shape)

        if tile and not volume:
            tile = (1, tile[-2], tile[-1])

        if photometric == 'palette':
            if (samplesperpixel != 1 or extrasamples or
                    shape[1] != 1 or shape[-1] != 1):
                raise ValueError("invalid data shape for palette mode")

        if photometric == 'rgb' and samplesperpixel == 2:
            raise ValueError("not a RGB image (samplesperpixel=2)")

        bytestr = bytes if sys.version[0] == '2' else (
            lambda x: bytes(x, 'utf-8') if isinstance(x, str) else x)
        tags = []  # list of (code, ifdentry, ifdvalue, writeonce)

        strip_or_tile = 'tile' if tile else 'strip'
        tag_byte_counts = CONST.TIFF_TAGS_NAMES[strip_or_tile + '_byte_counts']
        tag_offsets = CONST.TIFF_TAGS_NAMES[strip_or_tile + '_offsets']
        self._tag_offsets = tag_offsets

        def pack(fmt, *val):
            return struct.pack(byteorder+fmt, *val)

        def addtag(code, dtype, count, value, writeonce=False):
            # Compute ifdentry & ifdvalue bytes from code, dtype, count, value
            # Append (code, ifdentry, ifdvalue, writeonce) to tags list
            code = int(CONST.TIFF_TAGS_NAMES.get(code, code))
            try:
                tifftype = CONST.TIFF_DATA_DTYPES[dtype]
            except KeyError:
                raise ValueError("unknown dtype %s" % dtype)
            rawcount = count

            if dtype == 's':
                # strings
                value = bytestr(value) + b'\0'
                count = rawcount = len(value)
                rawcount = value.find(b'\0\0')
                if rawcount < 0:
                    rawcount = count
                else:
                    rawcount += 1  # length of string without buffer
                value = (value,)
            elif isinstance(value, bytes):
                # packed binary data
                dtsize = struct.calcsize(dtype)
                if len(value) % dtsize:
                    raise ValueError('invalid packed binary data')
                count = len(value) // dtsize
            if len(dtype) > 1:
                count *= int(dtype[:-1])
                dtype = dtype[-1]
            ifdentry = [pack('HH', code, tifftype),
                        pack(offset_format, rawcount)]
            ifdvalue = None
            if struct.calcsize(dtype) * count <= offset_size:
                # value(s) can be written directly
                if isinstance(value, bytes):
                    ifdentry.append(pack(value_format, value))
                elif count == 1:
                    if isinstance(value, (tuple, list, numpy.ndarray)):
                        value = value[0]
                    ifdentry.append(pack(value_format, pack(dtype, value)))
                else:
                    ifdentry.append(pack(value_format,
                                         pack(str(count)+dtype, *value)))
            else:
                # use offset to value(s)
                ifdentry.append(pack(offset_format, 0))
                if isinstance(value, bytes):
                    ifdvalue = value
                elif isinstance(value, numpy.ndarray):
                    assert value.size == count
                    assert value.dtype.char == dtype
                    ifdvalue = value.tostring()
                elif isinstance(value, (tuple, list)):
                    ifdvalue = pack(str(count)+dtype, *value)
                else:
                    ifdvalue = pack(dtype, value)
            tags.append((code, b''.join(ifdentry), ifdvalue, writeonce))

        def rational(arg, max_denominator=1000000):
            # return nominator and denominator from float or two integers
            from fractions import Fraction  # delayed import
            try:
                f = Fraction.from_float(arg)
            except TypeError:
                f = Fraction(arg[0], arg[1])
            f = f.limit_denominator(max_denominator)
            return f.numerator, f.denominator

        if description:
            # user provided description
            addtag('image_description', 's', 0, description, writeonce=True)

        # write shape and metadata to image_description
        self._metadata = {} if not metadata else metadata
        if self._imagej:
            description = imagej_description(
                _data_shape, shape[-1] in (3, 4), self._colormap is not None,
                **self._metadata)
        elif metadata or metadata == {}:
            description = json_description(
                _data_shape, self._colormap is not None, **self._metadata)
        else:
            description = None
        if description:
            # add 32 bytes buffer
            # the image description might be updated later with the final shape
            description += b'\0'*32
            self._description_len = len(description)
            addtag('image_description', 's', 0, description, writeonce=True)

        if self._software:
            addtag('software', 's', 0, self._software, writeonce=True)
            self._software = None  # only save to first page in file
        if datetime is None:
            datetime = self._now()
        addtag('datetime', 's', 0, datetime.strftime("%Y:%m:%d %H:%M:%S"),
               writeonce=True)
        addtag('compression', 'H', 1, compress_tag)
        addtag('image_width', 'I', 1, shape[-2])
        addtag('image_length', 'I', 1, shape[-3])
        if tile:
            addtag('tile_width', 'I', 1, tile[-1])
            addtag('tile_length', 'I', 1, tile[-2])
            if tile[0] > 1:
                addtag('image_depth', 'I', 1, shape[-4])
                addtag('tile_depth', 'I', 1, tile[0])
        addtag('new_subfile_type', 'I', 1, 0)
        sampleformat = {'u': 1, 'i': 2, 'f': 3, 'c': 6}[data_dtype.kind]
        addtag('sample_format', 'H', samplesperpixel,
               (sampleformat,) * samplesperpixel)
        addtag('photometric', 'H', 1, {'miniswhite': 0, 'minisblack': 1,
                                       'rgb': 2, 'palette': 3,
                                       'cfa': 32803}[photometric])
        if colormap is not None:
            addtag('color_map', 'H', colormap.size, colormap)
        addtag('samples_per_pixel', 'H', 1, samplesperpixel)
        if planarconfig and samplesperpixel > 1:
            addtag('planar_configuration', 'H', 1, 1
                   if planarconfig == 'contig' else 2)
            addtag('bits_per_sample', 'H', samplesperpixel,
                   (data_dtype.itemsize * 8,) * samplesperpixel)
        else:
            addtag('bits_per_sample', 'H', 1, data_dtype.itemsize * 8)
        if extrasamples:
            if photometric == 'rgb' and extrasamples == 1:
                addtag('extra_samples', 'H', 1, 1)  # associated alpha channel
            else:
                addtag('extra_samples', 'H', extrasamples, (0,) * extrasamples)
        if resolution:
            addtag('x_resolution', '2I', 1, rational(resolution[0]))
            addtag('y_resolution', '2I', 1, rational(resolution[1]))
            if len(resolution) > 2:
                resolution_unit = {None: 1, 'inch': 2, 'cm': 3}[resolution[2]]
            elif self._imagej:
                resolution_unit = 1
            else:
                resolution_unit = 2
            addtag('resolution_unit', 'H', 1, resolution_unit)
        if not tile:
            addtag('rows_per_strip', 'I', 1, shape[-3])  # * shape[-4]

        contiguous = not compress
        if tile:
            # use one chunk per tile per plane
            tiles = ((shape[2] + tile[0] - 1) // tile[0],
                     (shape[3] + tile[1] - 1) // tile[1],
                     (shape[4] + tile[2] - 1) // tile[2])
            numtiles = product(tiles) * shape[1]
            strip_byte_counts = [
                product(tile) * shape[-1] * data_dtype.itemsize] * numtiles
            addtag(tag_byte_counts, offset_format, numtiles, strip_byte_counts)
            addtag(tag_offsets, offset_format, numtiles, [0] * numtiles)
            contiguous = contiguous and product(tiles) == 1
            if not contiguous:
                # allocate tile buffer
                chunk = numpy.empty(tile + (shape[-1],), dtype=data_dtype)
        else:
            # use one strip per plane
            strip_byte_counts = [
                product(data_shape[2:]) * data_dtype.itemsize] * shape[1]
            addtag(tag_byte_counts, offset_format, shape[1], strip_byte_counts)
            addtag(tag_offsets, offset_format, shape[1], [0] * shape[1])

        if data is None and not contiguous:
            raise ValueError("can not write non-contiguous empty file")

        # add extra tags from user
        for t in extratags:
            addtag(*t)

        # TODO: check TIFFReadDirectoryCheckOrder warning in files containing
        #   multiple tags of same code
        # the entries in an IFD must be sorted in ascending order by tag code
        tags = sorted(tags, key=lambda x: x[0])

        if not (self._bigtiff or self._imagej) and (
                fh.tell() + data_size > 2**31-1):
            raise ValueError("data too large for standard TIFF file")

        # if not compressed or multi-tiled, write the first ifd and then
        # all data contiguously; else, write all ifds and data interleaved
        for pageindex in range(1 if contiguous else shape[0]):
            # update pointer at ifd_offset
            pos = fh.tell()
            if pos % 2:
                # location of IFD must begin on a word boundary
                fh.write(b'\0')
                pos += 1
            fh.seek(self._ifd_offset)
            fh.write(pack(offset_format, pos))
            fh.seek(pos)

            # write ifdentries
            fh.write(pack(tagno_format, len(tags)))
            tag_offset = fh.tell()
            fh.write(b''.join(t[1] for t in tags))
            self._ifd_offset = fh.tell()
            fh.write(pack(offset_format, 0))  # offset to next IFD

            # write tag values and patch offsets in ifdentries, if necessary
            for tagindex, tag in enumerate(tags):
                if tag[2]:
                    pos = fh.tell()
                    if pos % 2:
                        # tag value is expected to begin on a word boundary
                        fh.write(b'\0')
                        pos += 1
                    fh.seek(tag_offset + tagindex*tag_size + offset_size + 4)
                    fh.write(pack(offset_format, pos))
                    fh.seek(pos)
                    if tag[0] == tag_offsets:
                        strip_offsets_offset = pos
                    elif tag[0] == tag_byte_counts:
                        strip_byte_counts_offset = pos
                    elif tag[0] == 270 and tag[2].endswith(b'\0\0\0\0'):
                        # image description buffer
                        self._description_offset = pos
                        self._description_len_offset = (
                            tag_offset + tagindex * tag_size + 4)
                    fh.write(tag[2])

            # write image data
            data_offset = fh.tell()
            skip = align - data_offset % align
            fh.seek(skip, 1)
            data_offset += skip
            if compress:
                strip_byte_counts = []
            if contiguous:
                if data is None:
                    fh.write_empty(data_size)
                else:
                    fh.write_array(data)
            elif tile:
                for plane in data[pageindex]:
                    for tz in range(tiles[0]):
                        for ty in range(tiles[1]):
                            for tx in range(tiles[2]):
                                c0 = min(tile[0], shape[2] - tz*tile[0])
                                c1 = min(tile[1], shape[3] - ty*tile[1])
                                c2 = min(tile[2], shape[4] - tx*tile[2])
                                chunk[c0:, c1:, c2:] = 0
                                chunk[:c0, :c1, :c2] = plane[
                                    tz*tile[0]:tz*tile[0]+c0,
                                    ty*tile[1]:ty*tile[1]+c1,
                                    tx*tile[2]:tx*tile[2]+c2]
                                if compress:
                                    t = compress(chunk)
                                    strip_byte_counts.append(len(t))
                                    fh.write(t)
                                else:
                                    fh.write_array(chunk)
                                    fh.flush()
            elif compress:
                for plane in data[pageindex]:
                    plane = compress(plane)
                    strip_byte_counts.append(len(plane))
                    fh.write(plane)

            # update strip/tile offsets and byte_counts if necessary
            pos = fh.tell()
            for tagindex, tag in enumerate(tags):
                if tag[0] == tag_offsets:  # strip/tile offsets
                    if tag[2]:
                        fh.seek(strip_offsets_offset)
                        strip_offset = data_offset
                        for size in strip_byte_counts:
                            fh.write(pack(offset_format, strip_offset))
                            strip_offset += size
                    else:
                        fh.seek(tag_offset + tagindex*tag_size +
                                offset_size + 4)
                        fh.write(pack(offset_format, data_offset))
                elif tag[0] == tag_byte_counts:  # strip/tile byte_counts
                    if compress:
                        if tag[2]:
                            fh.seek(strip_byte_counts_offset)
                            for size in strip_byte_counts:
                                fh.write(pack(offset_format, size))
                        else:
                            fh.seek(tag_offset + tagindex*tag_size +
                                    offset_size + 4)
                            fh.write(pack(offset_format, strip_byte_counts[0]))
                    break
            fh.seek(pos)
            fh.flush()

            # remove tags that should be written only once
            if pageindex == 0:
                tags = [tag for tag in tags if not tag[-1]]

        self._shape = shape
        self._data_shape = (1,) + _data_shape
        self._data_dtype = data_dtype
        self._data_offset = data_offset
        self._data_byte_counts = strip_byte_counts

        if contiguous:
            # write remaining ifds/tags later
            self._tags = tags
            # return offset and size of image data
            if return_offset:
                return data_offset, sum(strip_byte_counts)

    def _write_remaining_pages(self):
        """Write outstanding IFDs and tags to file."""
        if not self._tags or self._truncate:
            return

        fh = self._fh
        byteorder = self._byteorder
        tagno_format = self._tagno_format
        offset_format = self._offset_format
        offset_size = self._offset_size
        tag_size = self._tag_size
        data_offset = self._data_offset
        page_data_size = sum(self._data_byte_counts)
        tag_bytes = b''.join(t[1] for t in self._tags)
        pageno = self._shape[0] * self._data_shape[0] - 1

        pos = fh.tell()
        if not self._bigtiff and pos + len(tag_bytes) * pageno > 2**32 - 256:
            if self._imagej:
                warnings.warn("truncating ImageJ file")
                return
            raise ValueError("data too large for non-BigTIFF file")

        def pack(fmt, *val):
            return struct.pack(byteorder+fmt, *val)

        for _ in range(pageno):
            # update pointer at ifd_offset
            pos = fh.tell()
            if pos % 2:
                # location of IFD must begin on a word boundary
                fh.write(b'\0')
                pos += 1
            fh.seek(self._ifd_offset)
            fh.write(pack(offset_format, pos))
            fh.seek(pos)

            # write ifd entries
            fh.write(pack(tagno_format, len(self._tags)))
            tag_offset = fh.tell()
            fh.write(tag_bytes)
            self._ifd_offset = fh.tell()
            fh.write(pack(offset_format, 0))  # offset to next IFD

            # offset to image data
            data_offset += page_data_size

            # write tag values and patch offsets in ifdentries, if necessary
            for tagindex, tag in enumerate(self._tags):
                if tag[2]:
                    pos = fh.tell()
                    if pos % 2:
                        # tag value is expected to begin on a word boundary
                        fh.write(b'\0')
                        pos += 1
                    fh.seek(tag_offset + tagindex*tag_size + offset_size + 4)
                    fh.write(pack(offset_format, pos))
                    fh.seek(pos)
                    if tag[0] == self._tag_offsets:
                        strip_offsets_offset = pos
                    fh.write(tag[2])

            # update strip/tile offsets if necessary
            pos = fh.tell()
            for tagindex, tag in enumerate(self._tags):
                if tag[0] == self._tag_offsets:  # strip/tile offsets
                    if tag[2]:
                        fh.seek(strip_offsets_offset)
                        strip_offset = data_offset
                        for size in self._data_byte_counts:
                            fh.write(pack(offset_format, strip_offset))
                            strip_offset += size
                    else:
                        fh.seek(tag_offset + tagindex*tag_size +
                                offset_size + 4)
                        fh.write(pack(offset_format, data_offset))
                    break
            fh.seek(pos)

        self._tags = None
        self._data_dtype = None
        self._data_offset = None
        self._data_byte_counts = None
        # do not reset _shape or _data_shape

    def _write_image_description(self):
        """Write meta data to image_description tag."""
        if (not self._data_shape or self._data_shape[0] == 1 or
                self._description_offset <= 0):
            return

        colormapped = self._colormap is not None
        if self._imagej:
            isrgb = self._shape[-1] in (3, 4)
            description = imagej_description(
                self._data_shape, isrgb, colormapped, **self._metadata)
        else:
            description = json_description(
                self._data_shape, colormapped, **self._metadata)

        # rewrite description and its length to file
        description = description[:self._description_len-1]
        pos = self._fh.tell()
        self._fh.seek(self._description_offset)
        self._fh.write(description)
        self._fh.seek(self._description_len_offset)
        self._fh.write(struct.pack(self._byteorder+self._offset_format,
                                   len(description)+1))
        self._fh.seek(pos)

        self._description_offset = 0
        self._description_len_offset = 0
        self._description_len = 0

    def _now(self):
        """Return current date and time."""
        return datetime.datetime.now()

    def close(self):
        """Write remaining pages and close file handle."""
        if not self._truncate:
            self._write_remaining_pages()
        self._write_image_description()
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class TiffFile(object):
    """Read image and metadata from TIFF, STK, LSM, and FluoView files.

    TiffFile instances must be closed using the 'close' method, which is
    automatically called when using the 'with' context manager.

    Attributes
    ----------
    pages : TiffPages
        Sequence of TIFF pages from file.
    series : list of TiffPageSeries
        Sequences of closely related TIFF pages. These are computed
        from OME, LSM, ImageJ, etc. metadata or based on similarity
        of page properties such as shape, dtype, compression, etc.
    byteorder : '>', '<'
        The endianness of data in the file.
        '>': big-endian (Motorola).
        '>': little-endian (Intel).
    is_*format* : bool
        If True, file is of a certain format.
        Formats are: bigtiff, movie, shaped, ome, imagej, stk, lsm, fluoview,
        nih, vista, 'micromanager, metaseries, mdgel, mediacy, tvips, fei,
        sem, scn, svs, scanimage, andor, epics, pilatus.

    All attributes are read-only.

    Examples
    --------
    >>> imsave('temp.tif', numpy.random.rand(5, 301, 219))
    >>> with TiffFile('temp.tif') as tif:
    ...     data = tif.asarray()
    ...     data.shape
    (5, 301, 219)

    """
    def __init__(self, arg, name=None, offset=None, size=None,
                 multifile=True, multifile_close=True, movie=None, **kwargs):
        """Initialize instance from file.

        Parameters
        ----------
        arg : str or open file
            Name of file or open file object.
            The file objects are closed in TiffFile.close().
        name : str
            Optional name of file in case 'arg' is a file handle.
        offset : int
            Optional start position of embedded file. By default, this is
            the current file position.
        size : int
            Optional size of embedded file. By default, this is the number
            of bytes from the 'offset' to the end of the file.
        multifile : bool
            If True (default), series may include pages from multiple files.
            Currently applies to OME-TIFF only.
        multifile_close : bool
            If True (default), keep the handles of other files in multifile
            series closed. This is inefficient when few files refer to
            many pages. If False, the C runtime may run out of resources.
        movie : bool
            If True, assume that later pages differ from first page only by
            data offsets and byte_counts. Significantly increases speed and
            reduces memory usage when reading movies with thousands of pages.
            Enabling this for non-movie files will result in data corruption
            or crashes. Python 3 only.
        kwargs : bool
            'is_ome': If False, disable processing of OME-XML metadata.

        """
        if 'fastij' in kwargs:
            del kwargs['fastij']
            raise DeprecationWarning("The fastij option will be removed.")
        for key, value in kwargs.items():
            if key[:3] == 'is_' and key[3:] in CONST.TIFF_FILE_ATTRS:
                if value is not None and not value:
                    setattr(self, key, bool(value))
            else:
                raise TypeError(
                    "got an unexpected keyword argument '%s'" % key)

        fh = FileHandle(arg, mode='rb', name=name, offset=offset, size=size)
        self._fh = fh
        self._multifile = bool(multifile)
        self._multifile_close = bool(multifile_close)
        self._files = {fh.name: self}  # cache of TiffFiles
        try:
            fh.seek(0)
            try:
                byteorder = {b'II': '<', b'MM': '>'}[fh.read(2)]
            except KeyError:
                raise ValueError("invalid TIFF file")
            sys_byteorder = {'big': '>', 'little': '<'}[sys.byteorder]
            self.is_native = byteorder == sys_byteorder

            version = struct.unpack(byteorder+'H', fh.read(2))[0]
            if version == 43:
                # BigTiff
                self.is_bigtiff = True
                offset_size, zero = struct.unpack(byteorder+'HH', fh.read(4))
                if zero or offset_size != 8:
                    raise ValueError("invalid BigTIFF file")
                self.byteorder = byteorder
                self.offset_size = 8
                self.offset_format = byteorder+'Q'
                self.tagno_size = 8
                self.tagno_format = byteorder+'Q'
                self.tag_size = 20
                self.tag_format1 = byteorder+'HH'
                self.tag_format2 = byteorder+'Q8s'
            elif version == 42:
                self.is_bigtiff = False
                self.byteorder = byteorder
                self.offset_size = 4
                self.offset_format = byteorder+'I'
                self.tagno_size = 2
                self.tagno_format = byteorder+'H'
                self.tag_size = 12
                self.tag_format1 = byteorder+'HH'
                self.tag_format2 = byteorder+'I4s'
            else:
                raise ValueError("not a TIFF file")

            # file handle is at offset to offset to first page
            self.pages = TiffPages(self)

            if self.is_lsm and (self.filehandle.size >= 2**32 or
                                self.pages[0].compression or
                                self.pages[1].compression):
                self._lsm_load_pages()
                self._lsm_fix_strip_offsets()
                self._lsm_fix_strip_byte_counts()
            elif movie:
                self.pages.useframes = True

        except Exception:
            fh.close()
            raise

    @property
    def filehandle(self):
        """Return file handle."""
        return self._fh

    @property
    def filename(self):
        """Return name of file handle."""
        return self._fh.name

    @lazyattr
    def fstat(self):
        """Return status of file handle as stat_result object."""
        try:
            return os.fstat(self._fh.fileno())
        except Exception:  # io.UnsupportedOperation
            return None

    def close(self):
        """Close open file handle(s)."""
        for tif in self._files.values():
            tif.filehandle.close()
        self._files = {}

    def asarray(self, key=None, series=None, memmap=False, tempdir=None):
        """Return image data from multiple TIFF pages as numpy array.

        By default, the data from the first series is returned.

        Parameters
        ----------
        key : int, slice, or sequence of page indices
            Defines which pages to return as array.
        series : int or TiffPageSeries
            Defines which series of pages to return as array.
        memmap : bool
            If True, return an read-only array stored in a binary file on disk
            if possible. The TIFF file is used if possible, else a temporary
            file is created.
        tempdir : str
            The directory where the memory-mapped file will be created.

        """
        if not self.pages:
            return numpy.array([])
        if key is None and series is None:
            series = 0
        if series is not None:
            try:
                series = self.series[series]
            except (KeyError, TypeError):
                pass
            pages = series.pages
        else:
            pages = self.pages

        if key is None:
            pass
        elif isinstance(key, inttypes):
            pages = [pages[key]]
        elif isinstance(key, slice):
            pages = pages[key]
        elif isinstance(key, collections.Iterable):
            pages = [pages[k] for k in key]
        else:
            raise TypeError("key must be an int, slice, or sequence")

        if not pages:
            raise ValueError("no pages selected")

        if self.is_nih:
            if pages[0].is_indexed:
                result = stack_pages(pages, colormapped=False, squeeze=False)
                result = apply_colormap(result, pages[0].color_map)
            else:
                result = stack_pages(pages, memmap=memmap, tempdir=tempdir,
                                     colormapped=False, squeeze=False)
        elif key is None and series and series.offset:
            if memmap and pages[0].is_memmappable(False, False):
                result = self.filehandle.memmap_array(
                    series.dtype, series.shape, series.offset)
            else:
                self.filehandle.seek(series.offset)
                result = self.filehandle.read_array(series.dtype,
                                                    product(series.shape))
                if not self.is_native:
                    result.byteswap(True)
        elif len(pages) == 1:
            result = pages[0].asarray(memmap=memmap)
        elif self.is_ome and series:
            if any(p is None for p in pages):
                # zero out missing pages
                firstpage = next(p for p in pages if p)
                nopage = numpy.zeros_like(
                    firstpage.asarray(memmap=False))
            if memmap:
                with tempfile.NamedTemporaryFile() as fh:
                    result = numpy.memmap(fh, series.dtype, shape=series.shape)
                    result = result.reshape(-1)
            else:
                result = numpy.empty(series.shape, series.dtype).reshape(-1)
            index = 0

            class KeepOpen(object):
                # keep Tiff files open between consecutive pages
                def __init__(self, parent, close):
                    self.master = parent
                    self.parent = parent
                    self._close = close

                def open(self, page):
                    if self._close and page and page.parent != self.parent:
                        if self.parent != self.master:
                            self.parent.filehandle.close()
                        self.parent = page.parent
                        self.parent.filehandle.open()

                def close(self):
                    if self._close and self.parent != self.master:
                        self.parent.filehandle.close()

            keep = KeepOpen(self, self._multifile_close)
            for page in pages:
                keep.open(page)
                if page:
                    a = page.asarray(memmap=False, colormapped=False,
                                     reopen=False)
                else:
                    a = nopage
                try:
                    result[index:index + a.size] = a.reshape(-1)
                except ValueError as e:
                    warnings.warn("ome-tiff: %s" % e)
                    break
                index += a.size
            keep.close()
        else:
            result = stack_pages(pages, memmap=memmap, tempdir=tempdir)

        if key is None:
            try:
                result.shape = series.shape
            except ValueError:
                try:
                    warnings.warn("failed to reshape %s to %s" % (
                        result.shape, series.shape))
                    # try series of expected shapes
                    result.shape = (-1,) + series.shape
                except ValueError:
                    # revert to generic shape
                    result.shape = (-1,) + pages[0].shape
        elif len(pages) == 1:
            result.shape = pages[0].shape
        else:
            result.shape = (-1,) + pages[0].shape
        return result

    @lazyattr
    def series(self):
        """Return related pages as TiffPageSeries."""
        if not self.pages:
            return []

        useframes = self.pages.useframes
        keyframe = self.pages.keyframe
        series = []
        for name in 'ome imagej lsm fluoview nih shaped'.split():
            if getattr(self, 'is_' + name, False):
                series = getattr(self, '_%s_series' % name)()
                break
        if not series:
            self.pages.useframes = useframes
            self.pages.keyframe = keyframe
            series = self._generic_series()

        # remove empty series, e.g. in MD Gel files
        series = [s for s in series if sum(s.shape) > 0]

        for i, s in enumerate(series):
            s.index = i
        return series

    def _generic_series(self):
        """Return image series in file."""
        if self.pages.useframes:
            # movie mode
            page = self.pages[0]
            shape = page.shape
            axes = page.axes
            if len(self.pages) > 1:
                shape = (len(self.pages),) + shape
                axes = 'I' + axes
            return [TiffPageSeries(self.pages[:], shape, page.dtype, axes,
                                   stype='movie')]

        self.pages.clear(False)
        self.pages.load()
        result = []
        keys = []
        series = {}
        compressions = CONST.TIFF_DECOMPESSORS
        for page in self.pages:
            if not page.shape:
                continue
            key = page.shape + (page.axes, page.compression in compressions)
            if key in series:
                series[key].append(page)
            else:
                keys.append(key)
                series[key] = [page]
        for key in keys:
            pages = series[key]
            page = pages[0]
            shape = page.shape
            axes = page.axes
            if len(pages) > 1:
                shape = (len(pages),) + shape
                axes = 'I' + axes
            result.append(TiffPageSeries(pages, shape, page.dtype, axes,
                                         stype='generic'))

        return result

    def _shaped_series(self):
        """Return image series in "shaped" file."""
        pages = self.pages
        pages.useframes = True
        lenpages = len(pages)

        def append_series(series, pages, axes, shape, reshape, name):
            page = pages[0]
            if not axes:
                shape = page.shape
                axes = page.axes
                if len(pages) > 1:
                    shape = (len(pages),) + shape
                    axes = 'Q' + axes
            size = product(shape)
            resize = product(reshape)
            if page.is_contiguous and resize > size and resize % size == 0:
                # truncated file
                axes = 'Q' + axes
                shape = (resize // size,) + shape
            try:
                axes = reshape_axes(axes, shape, reshape)
                shape = reshape
            except ValueError as e:
                warnings.warn(str(e))
            series.append(TiffPageSeries(pages, shape, page.dtype, axes,
                                         name=name, stype='shaped'))

        keyframe = axes = shape = reshape = name = None
        series = []
        i = 0
        while True:
            if i >= lenpages:
                break
            # new keyframe; start of new series
            pages.keyframe = i
            keyframe = pages[i]
            if not keyframe.is_shaped:
                warnings.warn("invalid shape metadata or corrupted file")
                return
            # read metadata
            axes = None
            shape = None
            metadata = json_description_metadata(keyframe.is_shaped)
            name = metadata.get('name', '')
            reshape = metadata['shape']
            if 'axes' in metadata:
                axes = metadata['axes']
                if len(axes) == len(reshape):
                    shape = reshape
                else:
                    axes = ''
                    warnings.warn("axes do not match shape")
            # skip pages if possible
            spages = [keyframe]
            size = product(reshape)
            nopages, mod = divmod(size, product(keyframe.shape))
            if mod:
                warnings.warn("series shape not matching page shape")
                return
            if 1 < nopages <= lenpages - i:
                size *= keyframe._dtype.itemsize
                page1 = pages[i+1]
                if page1.is_shaped:
                    # truncated series
                    nopages = 1
                elif not (keyframe.is_final and
                          keyframe.offset + size < page1.offset):
                    # need to read all pages for series
                    for j in range(i+1, i+nopages):
                        page = pages[j]
                        page.keyframe = keyframe
                        spages.append(page)
            append_series(series, spages, axes, shape, reshape, name)
            i += nopages

        return series

    def _imagej_series(self):
        """Return image series in ImageJ file."""
        # ImageJ's dimension order is always TZCYXS
        # TODO: fix loading of color, composite or palette images
        self.pages.useframes = True
        self.pages.keyframe = 0

        pages = self.pages
        page = pages[0]
        ij = page.imagej_metadata

        def is_hyperstack():
            # ImageJ hyperstack store all image metadata in the first page and
            # image data is stored contiguously before the second page, if any.
            if not page.is_final:
                return False
            images = ij.get('images', 0)
            if images <= 1:
                return False
            offset, count = page.is_contiguous
            if (count != product(page.shape) * page.bits_per_sample // 8
                    or offset + count*images > self.filehandle.size):
                raise ValueError()
            # check that next page is stored after data
            if len(pages) > 1 and offset + count*images > pages[1].offset:
                return False
            return True

        try:
            hyperstack = is_hyperstack()
        except ValueError:
            warnings.warn("invalid ImageJ metadata or corrupted file")
            return
        if hyperstack:
            # no need to read other pages
            pages = [page]
        else:
            self.pages.load()

        shape = []
        axes = []
        if 'frames' in ij:
            shape.append(ij['frames'])
            axes.append('T')
        if 'slices' in ij:
            shape.append(ij['slices'])
            axes.append('Z')
        if 'channels' in ij and not (page.is_rgb and not
                                     ij.get('hyperstack', False)):
            shape.append(ij['channels'])
            axes.append('C')
        remain = ij.get('images', len(pages))//(product(shape) if shape else 1)
        if remain > 1:
            shape.append(remain)
            axes.append('I')
        if page.axes[0] == 'I':
            # contiguous multiple images
            shape.extend(page.shape[1:])
            axes.extend(page.axes[1:])
        elif page.axes[:2] == 'SI':
            # color-mapped contiguous multiple images
            shape = page.shape[0:1] + tuple(shape) + page.shape[2:]
            axes = list(page.axes[0]) + axes + list(page.axes[2:])
        else:
            shape.extend(page.shape)
            axes.extend(page.axes)
        return [TiffPageSeries(pages, shape, page.dtype, axes, stype='imagej')]

    def _fluoview_series(self):
        """Return image series in FluoView file."""
        self.pages.useframes = True
        self.pages.keyframe = 0
        self.pages.load()

        page = self.pages[0]
        mmhd = list(reversed(page.mm_header['dimensions']))
        axes = ''.join(CONST.FLUOVIEW_DIMENSIONS.get(i[0].strip().upper(), 'Q')
                       for i in mmhd if i[1] > 1)
        shape = tuple(int(i[1]) for i in mmhd if i[1] > 1)
        name = bytes2str(stripnull(page.mm_header['image_name']))
        return [TiffPageSeries(self.pages, shape, page.dtype, axes,
                               name=name, stype='fluoview')]

    def _nih_series(self):
        """Return image series in NIH file."""
        self.pages.useframes = True
        self.pages.keyframe = 0
        self.pages.load()
        page0 = self.pages[0]
        if len(self.pages) == 1:
            shape = page0.shape
            axes = page0.axes
        else:
            shape = (len(self.pages),) + page0.shape
            axes = 'I' + page0.axes
        return [
            TiffPageSeries(self.pages, shape, page0.dtype, axes, stype='nih')]

    def _ome_series(self):
        """Return image series in OME-TIFF file(s)."""
        from xml.etree import cElementTree as etree  # delayed import
        omexml = self.pages[0].tags['image_description'].value
        try:
            root = etree.fromstring(omexml)
        except etree.ParseError as e:
            # TODO: test this
            warnings.warn("ome-xml: %s" % e)
            omexml = omexml.decode('utf-8', 'ignore').encode('utf-8')
            root = etree.fromstring(omexml)

        self.pages.useframes = True
        self.pages.keyframe = 0
        self.pages.load()

        uuid = root.attrib.get('UUID', None)
        self._files = {uuid: self}
        dirname = self._fh.dirname
        modulo = {}
        series = []
        for element in root:
            if element.tag.endswith('BinaryOnly'):
                warnings.warn("ome-xml: not an ome-tiff master file")
                break
            if element.tag.endswith('StructuredAnnotations'):
                for annot in element:
                    if not annot.attrib.get('Namespace',
                                            '').endswith('modulo'):
                        continue
                    for value in annot:
                        for modul in value:
                            for along in modul:
                                if not along.tag[:-1].endswith('Along'):
                                    continue
                                axis = along.tag[-1]
                                newaxis = along.attrib.get('Type', 'other')
                                newaxis = CONST.AXES_LABELS[newaxis]
                                if 'Start' in along.attrib:
                                    step = float(along.attrib.get('Step', 1))
                                    start = float(along.attrib['Start'])
                                    stop = float(along.attrib['End']) + step
                                    labels = numpy.arange(start, stop, step)
                                else:
                                    labels = [label.text for label in along
                                              if label.tag.endswith('Label')]
                                modulo[axis] = (newaxis, labels)

            if not element.tag.endswith('Image'):
                continue

            attr = element.attrib
            name = attr.get('Name', None)

            for pixels in element:
                if not pixels.tag.endswith('Pixels'):
                    continue
                attr = pixels.attrib
                dtype = attr.get('PixelType', None)
                axes = ''.join(reversed(attr['DimensionOrder']))
                shape = list(int(attr['Size'+ax]) for ax in axes)
                size = product(shape[:-2])
                ifds = None
                spp = 1  # samples per pixel
                for data in pixels:
                    if data.tag.endswith('Channel'):
                        attr = data.attrib
                        if ifds is None:
                            spp = int(attr.get('SamplesPerPixel', spp))
                            ifds = [None] * (size // spp)
                        elif int(attr.get('SamplesPerPixel', 1)) != spp:
                            raise ValueError(
                                "Can't handle differing SamplesPerPixel")
                        continue
                    if ifds is None:
                        ifds = [None] * (size // spp)
                    if not data.tag.endswith('TiffData'):
                        continue
                    attr = data.attrib
                    ifd = int(attr.get('IFD', 0))
                    num = int(attr.get('NumPlanes', 1 if 'IFD' in attr else 0))
                    num = int(attr.get('PlaneCount', num))
                    idx = [int(attr.get('First'+ax, 0)) for ax in axes[:-2]]
                    try:
                        idx = numpy.ravel_multi_index(idx, shape[:-2])
                    except ValueError:
                        # ImageJ produces invalid ome-xml when cropping
                        warnings.warn("ome-xml: invalid TiffData index")
                        continue
                    for uuid in data:
                        if not uuid.tag.endswith('UUID'):
                            continue
                        if uuid.text not in self._files:
                            if not self._multifile:
                                # abort reading multifile OME series
                                # and fall back to generic series
                                return []
                            fname = uuid.attrib['FileName']
                            try:
                                tif = TiffFile(os.path.join(dirname, fname))
                                tif.pages.load()
                            except (IOError, FileNotFoundError, ValueError):
                                warnings.warn(
                                    "ome-xml: failed to read '%s'" % fname)
                                break
                            self._files[uuid.text] = tif
                            if self._multifile_close:
                                tif.close()
                        pages = self._files[uuid.text].pages
                        try:
                            for i in range(num if num else len(pages)):
                                ifds[idx + i] = pages[ifd + i]
                        except IndexError:
                            warnings.warn("ome-xml: index out of range")
                        # only process first uuid
                        break
                    else:
                        pages = self.pages
                        try:
                            for i in range(num if num else len(pages)):
                                ifds[idx + i] = pages[ifd + i]
                        except IndexError:
                            warnings.warn("ome-xml: index out of range")

                if all(i is None for i in ifds):
                    # skip images without data
                    continue

                # set a keyframe on all ifds
                keyframe = None
                for i in ifds:
                    # try find a TiffPage
                    if i and i == i.keyframe:
                        keyframe = i
                        break
                if not keyframe:
                    # reload a TiffPage from file
                    for i, keyframe in enumerate(ifds):
                        if keyframe:
                            keyframe.parent.pages.keyframe = keyframe.index
                            keyframe = keyframe.parent.pages[keyframe.index]
                            ifds[i] = keyframe
                            break
                for i in ifds:
                    if i is not None:
                        i.keyframe = keyframe

                dtype = keyframe.dtype
                series.append(
                    TiffPageSeries(ifds, shape, dtype, axes, parent=self,
                                   name=name, stype='ome'))
        for serie in series:
            shape = list(serie.shape)
            for axis, (newaxis, labels) in modulo.items():
                i = serie.axes.index(axis)
                size = len(labels)
                if shape[i] == size:
                    serie.axes = serie.axes.replace(axis, newaxis, 1)
                else:
                    shape[i] //= size
                    shape.insert(i+1, size)
                    serie.axes = serie.axes.replace(axis, axis+newaxis, 1)
            serie.shape = tuple(shape)
        # squeeze dimensions
        for serie in series:
            serie.shape, serie.axes = squeeze_axes(serie.shape, serie.axes)
        return series

    def _lsm_series(self, reduced=False):
        """Return main image series in LSM file. Skip thumbnails."""
        page = self.pages[0]
        lsmi = page.lsm_metadata
        axes = CONST.LSM_SCAN_TYPES[lsmi['scan_type']]
        if page.is_rgb:
            axes = axes.replace('C', '').replace('XY', 'XYC')
        if lsmi.get('dimension_p', 0) > 1:
            axes += 'P'
        if lsmi.get('dimension_m', 0) > 1:
            axes += 'M'
        axes = axes[::-1]
        shape = tuple(int(lsmi[CONST.LSM_DIMENSIONS[i]]) for i in axes)
        name = bytes2str(lsmi.get('name', b''))
        self.pages.keyframe = 0
        pages = self.pages[::2]
        dtype = pages[0].dtype
        series = [TiffPageSeries(pages, shape, dtype, axes, name=name,
                                 stype='lsm')]

        if reduced and self.pages[1].is_reduced:
            self.pages.keyframe = 1
            pages = self.pages[1::2]
            dtype = pages[0].dtype
            cp, i = 1, 0
            while cp < len(pages) and i < len(shape)-2:
                cp *= shape[i]
                i += 1
            shape = shape[:i] + pages[0].shape
            axes = axes[:i] + 'CYX'
            series.append(TiffPageSeries(pages, shape, dtype, axes, name=name,
                                         stype='lsm_reduced'))

        return series

    def _lsm_load_pages(self):
        """Load all pages from LSM file."""
        self.pages.cache = True
        self.pages.useframes = True
        # second series: thumbnails
        self.pages.keyframe = 1
        keyframe = self.pages[1]
        for page in self.pages[1::2]:
            page.keyframe = keyframe
        # first series: data
        self.pages.keyframe = 0
        keyframe = self.pages[0]
        for page in self.pages[::2]:
            page.keyframe = keyframe

    def _lsm_fix_strip_offsets(self):
        """Unwrap strip offsets for LSM files greater than 4 GB.

        Each series and position require separate unwrapping (undocumented).

        """
        if self.filehandle.size < 2**32:
            return
        for series in self.series:
            positions = 1
            for i in 0, 1:
                if series.axes[i] in 'PM':
                    positions *= series.shape[i]
            positions = len(series.pages) // positions
            for i, page in enumerate(series.pages):
                if not i % positions:
                    wrap = 0
                    previous_offset = 0
                data_offsets = []
                for current_offset in page.data_offsets:
                    if current_offset < previous_offset:
                        wrap += 2**32
                    data_offsets.append(current_offset + wrap)
                    previous_offset = current_offset
                page.data_offsets = tuple(data_offsets)

    def _lsm_fix_strip_byte_counts(self):
        """Set strip_byte_counts to size of compressed data.

        The strip_byte_counts tag in LSM files contains the number of bytes
        for the uncompressed data.

        """
        pages = self.pages
        if not pages or not (pages[0].compression or pages[1].compression):
            return
        strips = {}
        for page in pages:
            assert len(page.data_offsets) == len(page.data_byte_counts)
            for offset, count in zip(page.data_offsets, page.data_byte_counts):
                strips[offset] = count
        offsets = sorted(strips.keys())
        offsets.append(min(offsets[-1] + strips[offsets[-1]], self._fh.size))
        for i, offset in enumerate(offsets[:-1]):
            strips[offset] = min(strips[offset], offsets[i+1] - offset)
        if pages[0].compression:
            for page in pages[::2]:
                page.data_byte_counts = tuple(strips[offset]
                                              for offset in page.data_offsets)
        if pages[1].compression:
            for page in pages[1::2]:
                page.data_byte_counts = tuple(strips[offset]
                                              for offset in page.data_offsets)

    def __getattr__(self, name):
        """Return 'is_*' attributes from first page."""
        if name[3:] in CONST.TIFF_FILE_ATTRS:
            if not self.pages:
                return False
            value = bool(getattr(self.pages[0], name))
            setattr(self, name, value)
            return value
        raise AttributeError("'%s' object has no attribute '%s'" %
                             (self.__class__.__name__, name))

    def __len__(self):
        """Return number of pages in file."""
        return len(self.pages)

    def __getitem__(self, key):
        """Return specified page(s)."""
        return self.pages[key]

    def __iter__(self):
        """Return iterator over pages."""
        return iter(self.pages)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __str__(self):
        """Return string containing information about file."""
        result = [
            "TiffFile '%s'" % snipstr(self._fh.name, 32),
            format_size(self._fh.size),
            {'<': 'little endian', '>': 'big endian'}[self.byteorder]]
        if self.is_bigtiff:
            result.append("bigtiff")
        result.append('|'.join((attr for attr in CONST.TIFF_FILE_ATTRS
                                if getattr(self, 'is_' + attr))))
        if len(self.pages) > 1:
            result.append("%i pages" % len(self.pages))
        if len(self.series) > 1:
            result.append("%i series" % len(self.series))
        if len(self._files) > 1:
            result.append("%i files" % (len(self._files)))
        return "  ".join(result)

    def info(self, series=None, pages=None):
        """Return string with detailed information about file."""
        if series is None:
            series = self.series[:CONST.PRINT_MAX_LINES]
        else:
            series = [self.series[i] for i in sequence(series)]

        result = [str(self)]
        result.append("\n".join(str(s) for s in series))

        if pages is None:
            for s in series:
                result.append(next(p.info() for p in s.pages if p))
        else:
            if pages == 'all':
                pages = self.pages
            else:
                pages = [self.pages[i] for i in sequence(pages)]
            for p in pages:
                result.append(p.info())

        return '\n\n'.join(result)

    @lazyattr
    def micromanager_metadata(self):
        """Return MicroManager metadata not stored in TIFF tags."""
        if self.is_micromanager:
            return read_micromanager_metadata(self._fh)

    @lazyattr
    def scanimage_metadata(self):
        """Return ScanImage non-varying frame and ROI metadata as dict."""
        if self.is_scanimage:
            try:
                frame_data, roi_data = read_scanimage_metadata(self._fh)
                frame_data.update(roi_data)
                return frame_data
            except ValueError:
                pass

    @lazyattr
    def is_mdgel(self):
        """File has MD Gel format."""
        try:
            return self.pages[1].is_mdgel
        except (IndexError, AttributeError):
            return False

    @property
    def is_movie(self):
        """Return if file is a movie."""
        return self.pages.useframes


class TiffPages(object):
    """Sequence of TIFF image file directories."""
    def __init__(self, parent):
        """Initialize instance from file. Read first TiffPage from file.

        The file position must be at an offset to an offset to a TiffPage.

        """
        self.parent = parent
        self.pages = []  # cache of TiffPages, TiffFrames, or their offsets
        self.complete = False  # True if offsets to all pages were read
        self._tiffpage = TiffPage  # class for reading tiff pages
        self._keyframe = None
        self._cache = True

        # read offset to first page
        fh = parent.filehandle
        self._next_page_offset = fh.tell()
        offset = struct.unpack(parent.offset_format,
                               fh.read(parent.offset_size))[0]

        if offset == 0:
            # warnings.warn("file contains no pages")
            self.complete = True
            return
        if offset >= fh.size:
            warnings.warn("invalid page offset (%i)" % offset)
            self.complete = True
            return

        # always read and cache first page
        fh.seek(offset)
        page = TiffPage(parent, index=0)
        self.pages.append(page)
        self._keyframe = page

    @property
    def cache(self):
        """Return if pages/frames are currenly being cached."""
        return self._cache

    @cache.setter
    def cache(self, value):
        """Enable or disable caching of pages/frames. Clear cache if False."""
        value = bool(value)
        if self._cache and not value:
            self.clear()
        self._cache = value

    @property
    def useframes(self):
        """Return if currently using TiffFrame (True) or TiffPage (False)."""
        return self._tiffpage == TiffFrame and TiffFrame is not TiffPage

    @useframes.setter
    def useframes(self, value):
        """Set to use TiffFrame (True) or TiffPage (False)."""
        self._tiffpage = TiffFrame if value else TiffPage

    @property
    def keyframe(self):
        """Return index of current keyframe."""
        return self._keyframe.index

    @keyframe.setter
    def keyframe(self, index):
        """Set current keyframe. Load TiffPage from file if necessary."""
        if self.complete or 0 <= index < len(self.pages):
            page = self.pages[index]
            if isinstance(page, TiffPage):
                self._keyframe = page
                return
            elif isinstance(page, TiffFrame):
                # remove existing frame
                self.pages[index] = page.offset
        # load TiffPage from file
        useframes = self.useframes
        self._tiffpage = TiffPage
        self._keyframe = self[index]
        self.useframes = useframes

    @property
    def next_page_offset(self):
        """Return offset where offset to a new page can be stored."""
        if not self.complete:
            self._seek(-1)
        return self._next_page_offset

    def load(self):
        """Read all remaining pages from file."""
        fh = self.parent.filehandle
        keyframe = self._keyframe
        pages = self.pages
        if not self.complete:
            self._seek(-1)
        for i, page in enumerate(pages):
            if isinstance(page, inttypes):
                fh.seek(page)
                page = self._tiffpage(self.parent, index=i, keyframe=keyframe)
                pages[i] = page

    def clear(self, fully=True):
        """Delete all but first page from cache. Set keyframe to first page."""
        pages = self.pages
        if not self._cache or len(pages) < 1:
            return
        self._keyframe = pages[0]
        if fully:
            # delete all but first TiffPage/TiffFrame
            for i, page in enumerate(pages[1:]):
                if not isinstance(page, inttypes):
                    pages[i+1] = page.offset
        elif TiffFrame is not TiffPage:
            # delete only TiffFrames
            for i, page in enumerate(pages):
                if isinstance(page, TiffFrame):
                    pages[i] = page.offset

    def _seek(self, index):
        """Seek file to offset of specified page."""
        pages = self.pages
        if not pages:
            return

        fh = self.parent.filehandle
        if self.complete or 0 <= index < len(pages):
            page = pages[index]
            offset = page if isinstance(page, inttypes) else page.offset
            fh.seek(offset)
            return

        offset_format = self.parent.offset_format
        offset_size = self.parent.offset_size
        tagno_format = self.parent.tagno_format
        tagno_size = self.parent.tagno_size
        tag_size = self.parent.tag_size
        unpack = struct.unpack

        page = pages[-1]
        offset = page if isinstance(page, inttypes) else page.offset

        while True:
            # read offsets to pages from file until index is reached
            fh.seek(offset)
            # skip tags
            try:
                tagno = unpack(tagno_format, fh.read(tagno_size))[0]
                if tagno > 4096:
                    raise ValueError("suspicious number of tags")
            except Exception:
                warnings.warn("corrupted tag list at offset %i" % offset)
                del pages[-1]
                self.complete = True
                break
            self._next_page_offset = offset + tagno_size + tagno * tag_size
            fh.seek(self._next_page_offset)

            # read offset to next page
            offset = unpack(offset_format, fh.read(offset_size))[0]
            if offset == 0:
                self.complete = True
                break
            if offset >= fh.size:
                warnings.warn("invalid page offset (%i)" % offset)
                self.complete = True
                break

            pages.append(offset)
            if 0 <= index < len(pages):
                break

        if index >= len(pages):
            raise IndexError('list index out of range')

        page = pages[index]
        fh.seek(page if isinstance(page, inttypes) else page.offset)

    def __bool__(self):
        """Return True if file contains any pages."""
        return len(self.pages) > 0

    def __len__(self):
        """Return number of pages in file."""
        if not self.complete:
            self._seek(-1)
        return len(self.pages)

    def __getitem__(self, key):
        """Return specified page(s) from cache or file."""
        pages = self.pages
        if not pages:
            raise IndexError('list index out of range')
        if key is 0:
            return pages[key]

        if isinstance(key, slice):
            start, stop, _ = key.indices(2**31)
            if not self.complete and max(stop, start) > len(pages):
                self._seek(-1)
            return [self[i] for i in range(*key.indices(len(pages)))]

        if self.complete and key >= len(pages):
            raise IndexError('list index out of range')

        try:
            page = pages[key]
        except IndexError:
            page = 0
        if not isinstance(page, inttypes):
            return page

        self._seek(key)
        page = self._tiffpage(self.parent, index=key, keyframe=self._keyframe)
        if self._cache:
            pages[key] = page
        return page

    def __iter__(self):
        """Return iterator over all pages."""
        i = 0
        while True:
            try:
                yield self[i]
                i += 1
            except IndexError:
                break


class TiffPage(object):
    """TIFF image file directory (IFD).

    Attributes
    ----------
    index : int
        Index of page in file.
    dtype : numpy.dtype or None
        Data type of image, color-mapped if applicable.
    shape : tuple
        Dimensions of the image array in TIFF page,
        color-mapped and with extra samples if applicable.
    axes : str
        Axes label codes:
        'X' width, 'Y' height, 'S' sample, 'I' image series|page|plane,
        'Z' depth, 'C' color|em-wavelength|channel, 'E' ex-wavelength|lambda,
        'T' time, 'R' region|tile, 'A' angle, 'P' phase, 'H' lifetime,
        'L' exposure, 'V' event, 'Q' unknown, '_' missing
    tags : dict
        Dictionary of tags in IFD. {tag.name: TiffTag}
    color_map : numpy.ndarray
        Color look up table, if exists.

    All attributes are read-only.

    Notes
    -----
    The internal, normalized '_shape' attribute is 6 dimensional:

    0 : number planes/images  (stk, ij).
    1 : planar samples_per_pixel.
    2 : image_depth Z  (sgi).
    3 : image_length Y.
    4 : image_width X.
    5 : contig samples_per_pixel.

    """
    def __init__(self, parent, index, keyframe=None):
        """Initialize instance from file.

        The file handle position must be at offset to a valid IFD.

        """
        self.parent = parent
        self.index = index

        self.shape = self._shape = ()
        self.dtype = self._dtype = None
        self.axes = ""
        self.offset = None  # offset to this IDF
        self.tags = {}

        self._fromfile()
        self._process_tags()

    def _fromfile(self):
        """Read TIFF IFD structure and its tags from file."""
        parent = self.parent
        fh = parent.filehandle

        self.offset = fh.tell()  # offset to this IDF

        # read standard tags
        try:
            tagno = struct.unpack(parent.tagno_format,
                                  fh.read(parent.tagno_size))[0]
            if tagno > 4096:
                raise ValueError("suspicious number of tags")
        except Exception:
            raise ValueError("corrupted tag list at offset %i" % self.offset)

        tags = self.tags
        for _ in range(tagno):
            try:
                tag = TiffTag(self.parent)
            except TiffTag.Error as e:
                warnings.warn(str(e))
                continue
            if tag.name not in tags:
                tags[tag.name] = tag
            else:
                # some files contain multiple tags with same code
                # e.g. MicroManager files contain two image_description tags
                i = 1
                while True:
                    name = "%s_%i" % (tag.name, i)
                    if name not in tags:
                        tags[name] = tag
                        break

        # consolidate private tags; remove them from self.tags
        if self.is_andor:
            self.andor_metadata
        elif self.is_epics:
            self.epics_metadata

        if self.is_lsm or (self.index and self.parent.is_lsm):
            # correct non standard LSM bitspersample tags
            self.tags['bits_per_sample']._fix_lsm_bitspersample(self)

        if self.is_stk and 'uic1tag' in tags and not tags['uic1tag'].value:
            # read uic1tag now that plane count is known
            uic1tag = tags['uic1tag']
            fh.seek(uic1tag.value_offset)
            tags['uic1tag'].value = read_uic1tag(
                fh, parent.byteorder, uic1tag.dtype,
                uic1tag.count, None, tags['uic2tag'].count)

    def _process_tags(self):
        """Validate standard tags and initialize attributes.

        Raise ValueError if tag values are not supported.

        """
        tags = self.tags

        if 'bits_per_sample' in tags:
            tag = tags['bits_per_sample']
            if tag.count == 1:
                self.bits_per_sample = tag.value
            else:
                # LSM might list more items than samples_per_pixel
                value = tag.value[:self.samples_per_pixel]
                if any((v-value[0] for v in value)):
                    self.bits_per_sample = value
                else:
                    self.bits_per_sample = value[0]

        if 'sample_format' in tags:
            tag = tags['sample_format']
            if tag.count == 1:
                self.sample_format = CONST.TIFF_SAMPLE_FORMATS[tag.value]
            else:
                value = tag.value[:self.samples_per_pixel]
                if any((v-value[0] for v in value)):
                    self.sample_format = [CONST.TIFF_SAMPLE_FORMATS[v]
                                          for v in value]
                else:
                    self.sample_format = CONST.TIFF_SAMPLE_FORMATS[value[0]]

        if 'photometric' not in tags:
            self.photometric = None

        if 'image_length' in tags:
            if 'rows_per_strip' not in tags:
                self.rows_per_strip = self.image_length
            self.strips_per_image = int(math.floor(
                float(self.image_length + self.rows_per_strip - 1) /
                self.rows_per_strip))
        else:
            self.strips_per_image = 0

        # determine dtype
        dtype = self.sample_format, self.bits_per_sample
        dtype = CONST.TIFF_SAMPLE_DTYPES.get(dtype, None)
        if dtype is not None:
            dtype = numpy.dtype(dtype)
        self.dtype = self._dtype = dtype
        if self.is_indexed:
            self.dtype = numpy.dtype(self.tags['color_map'].dtype[1])
            self.color_map = numpy.array(self.color_map, self.dtype)
            dmax = self.color_map.max()
            if dmax < 256:
                self.dtype = numpy.dtype('uint8')
                self.color_map = self.color_map.astype(self.dtype)
            # else:
            #     self.dtype = numpy.dtype('uint8')
            #     self.color_map >>= 8
            #     self.color_map = self.color_map.astype(self.dtype)
            # TODO: support other photometric modes than RGB
            self.color_map.shape = (3, -1)

        if 'image_length' not in self.tags or 'image_width' not in self.tags:
            # some GEL file pages are missing image data
            self.image_length = 0
            self.image_width = 0
            self.image_depth = 0
            self.strip_offsets = (0,)
            self._shape = ()
            self.shape = ()
            self.axes = ''

        if self.is_vista or (self.index and self.parent.is_vista):
            # ISS Vista writes wrong image_depth tag
            self.image_depth = 1

        # determine shape of data
        image_length = self.image_length
        image_width = self.image_width
        image_depth = self.image_depth
        samples_per_pixel = self.samples_per_pixel

        if self.is_stk:
            assert self.image_depth == 1
            planes = self.tags['uic2tag'].count
            if self.is_contig:
                self._shape = (planes, 1, 1, image_length, image_width,
                               samples_per_pixel)
                if samples_per_pixel == 1:
                    self.shape = (planes, image_length, image_width)
                    self.axes = 'YX'
                else:
                    self.shape = (planes, image_length, image_width,
                                  samples_per_pixel)
                    self.axes = 'YXS'
            else:
                self._shape = (planes, samples_per_pixel, 1, image_length,
                               image_width, 1)
                if samples_per_pixel == 1:
                    self.shape = (planes, image_length, image_width)
                    self.axes = 'YX'
                else:
                    self.shape = (planes, samples_per_pixel, image_length,
                                  image_width)
                    self.axes = 'SYX'
            # detect type of series
            if planes == 1:
                self.shape = self.shape[1:]
            elif numpy.all(self.uic2tag['z_distance'] != 0):
                self.axes = 'Z' + self.axes
            elif numpy.all(numpy.diff(self.uic2tag['time_created']) != 0):
                self.axes = 'T' + self.axes
            else:
                self.axes = 'I' + self.axes
            # DISABLED
            if self.is_indexed:
                assert False, "color mapping disabled for stk"
                if self.color_map.shape[1] >= 2**self.bits_per_sample:
                    if image_depth == 1:
                        self.shape = (planes, image_length, image_width,
                                      self.color_map.shape[0])
                    else:
                        self.shape = (planes, image_depth, image_length,
                                      image_width, self.color_map.shape[0])
                    self.axes = self.axes + 'S'
                else:
                    warnings.warn("palette cannot be applied")
                    self.is_indexed = False
        elif self.is_indexed:
            samples = 1
            if 'extra_samples' in self.tags:
                samples += self.tags['extra_samples'].count
            if self.is_contig:
                self._shape = (1, 1, image_depth, image_length, image_width,
                               samples)
            else:
                self._shape = (1, samples, image_depth, image_length,
                               image_width, 1)
            if self.color_map.shape[1] >= 2**self.bits_per_sample:
                if image_depth == 1:
                    self.shape = (image_length, image_width,
                                  self.color_map.shape[0])
                    self.axes = 'YXS'
                else:
                    self.shape = (image_depth, image_length, image_width,
                                  self.color_map.shape[0])
                    self.axes = 'ZYXS'
            else:
                warnings.warn("palette cannot be applied")
                self.is_indexed = False
                if image_depth == 1:
                    self.shape = (image_length, image_width)
                    self.axes = 'YX'
                else:
                    self.shape = (image_depth, image_length, image_width)
                    self.axes = 'ZYX'
        elif self.is_rgb or samples_per_pixel > 1:
            if self.is_contig:
                self._shape = (1, 1, image_depth, image_length, image_width,
                               samples_per_pixel)
                if image_depth == 1:
                    self.shape = (image_length, image_width, samples_per_pixel)
                    self.axes = 'YXS'
                else:
                    self.shape = (image_depth, image_length, image_width,
                                  samples_per_pixel)
                    self.axes = 'ZYXS'
            else:
                self._shape = (1, samples_per_pixel, image_depth,
                               image_length, image_width, 1)
                if image_depth == 1:
                    self.shape = (samples_per_pixel, image_length, image_width)
                    self.axes = 'SYX'
                else:
                    self.shape = (samples_per_pixel, image_depth,
                                  image_length, image_width)
                    self.axes = 'SZYX'
            if False and self.is_rgb and 'extra_samples' in self.tags:
                # DISABLED: only use RGB and first alpha channel if exists
                extra_samples = self.extra_samples
                if self.tags['extra_samples'].count == 1:
                    extra_samples = (extra_samples,)
                for exs in extra_samples:
                    if exs in ('unassalpha', 'assocalpha', 'unspecified'):
                        if self.is_contig:
                            self.shape = self.shape[:-1] + (4,)
                        else:
                            self.shape = (4,) + self.shape[1:]
                        break
        else:
            self._shape = (1, 1, image_depth, image_length, image_width, 1)
            if image_depth == 1:
                self.shape = (image_length, image_width)
                self.axes = 'YX'
            else:
                self.shape = (image_depth, image_length, image_width)
                self.axes = 'ZYX'

        # data_offsets and data_byte_counts
        self.data_byte_counts = None
        if 'tile_offsets' in self.tags:
            self.data_offsets = self.tile_offsets
        else:
            self.data_offsets = self.strip_offsets
        if 'tile_byte_counts' in tags:
            self.data_byte_counts = self.tile_byte_counts
        elif 'strip_byte_counts' in tags:
            self.data_byte_counts = self.strip_byte_counts
        if self.data_byte_counts is None:
            if not self.compression:
                self.data_byte_counts = (
                    product(self.shape) * (self.bits_per_sample // 8),)
            else:
                raise ValueError("byte_counts not found")
        assert len(self.shape) == len(self.axes)

    def asarray(self, squeeze=True, colormapped=True, rgbonly=False,
                scale_mdgel=False, memmap=False, reopen=True,
                maxsize=64*2**30, validate=True):
        """Read image data from file and return as numpy array.

        Raise ValueError if format is unsupported.
        If any of 'squeeze', 'colormapped', or 'rgbonly' are not the default,
        the shape of the returned array might be different from the page shape.

        Parameters
        ----------
        squeeze : bool
            If True, all length-1 dimensions (except X and Y) are
            squeezed out from result.
        colormapped : bool
            If True, color mapping is applied for palette-indexed images.
        rgbonly : bool
            If True, return RGB(A) image without additional extra samples.
        memmap : bool
            If True, use numpy.memmap to read arrays from file if possible.
            For use on 64-bit systems and files with few huge contiguous data.
        reopen : bool
            If True and the parent file handle is closed, the file is
            temporarily re-opened (and closed if no exception occurs).
        scale_mdgel : bool
            If True, MD Gel data will be scaled according to the private
            metadata in the second TIFF page. The dtype will be float32.
        maxsize: int or None
            Maximum size of data before a ValueError is raised.
            Can be used to catch DOS. Default: 64 GB.

        """
        self_ = self
        self = self.keyframe  # self or keyframe

        if not self._shape:
            return

        tags = self.tags

        if validate:
            if maxsize and product(self._shape) > maxsize:
                raise ValueError("data is too large %s" % str(self._shape))

            if self.dtype is None:
                raise ValueError("data type not supported: %s%i" % (
                    self.sample_format, self.bits_per_sample))
            if self.compression not in CONST.TIFF_DECOMPESSORS:
                raise ValueError("cannot decompress %s" % self.compression)
            if 'sample_format' in tags:
                tag = tags['sample_format']
                if tag.count != 1 and any((i-tag.value[0] for i in tag.value)):
                    raise ValueError(
                        "sample formats do not match %s" % tag.value)

            if self.is_chroma_subsampled:
                # TODO: implement chroma subsampling
                raise NotImplementedError("chroma subsampling not supported")

        fh = self_.parent.filehandle
        closed = fh.closed
        if closed:
            if reopen:
                fh.open()
            else:
                raise IOError("file handle is closed")

        dtype = self._dtype
        shape = self._shape
        image_width = self.image_width
        image_length = self.image_length
        image_depth = self.image_depth
        typecode = self.parent.byteorder + dtype.char
        bits_per_sample = self.bits_per_sample
        lsb2msb = self.fill_order == 'lsb2msb'

        offsets, byte_counts = self_.offsets_byte_counts

        if self.is_tiled:
            tile_width = self.tile_width
            tile_length = self.tile_length
            tile_depth = self.tile_depth if 'tile_depth' in tags else 1
            tw = (image_width + tile_width - 1) // tile_width
            tl = (image_length + tile_length - 1) // tile_length
            td = (image_depth + tile_depth - 1) // tile_depth
            shape = (shape[0], shape[1],
                     td*tile_depth, tl*tile_length, tw*tile_width, shape[-1])
            tile_shape = (tile_depth, tile_length, tile_width, shape[-1])
            runlen = tile_width
        else:
            runlen = image_width

        if memmap and self.is_memmappable(rgbonly, colormapped):
            result = fh.memmap_array(typecode, shape, offset=offsets[0])
        elif self.is_contiguous:
            fh.seek(offsets[0])
            result = fh.read_array(typecode, product(shape))
            result = result.astype('=' + dtype.char)
            if lsb2msb:
                reverse_bitorder(result)
        else:
            if self.is_contig:
                runlen *= self.samples_per_pixel
            if bits_per_sample in (8, 16, 32, 64, 128):
                if (bits_per_sample * runlen) % 8:
                    raise ValueError("data and sample size mismatch")

                def unpack(x, typecode=typecode):
                    if self.predictor == 'float':
                        # the floating point horizontal differencing decoder
                        # needs the raw byte order
                        typecode = dtype.char
                    try:
                        return numpy.fromstring(x, typecode)
                    except ValueError as e:
                        # strips may be missing EOI
                        warnings.warn("unpack: %s" % e)
                        xlen = ((len(x) // (bits_per_sample // 8)) *
                                (bits_per_sample // 8))
                        return numpy.fromstring(x[:xlen], typecode)

            elif isinstance(bits_per_sample, tuple):
                def unpack(x):
                    return unpack_rgb(x, typecode, bits_per_sample)
            else:
                def unpack(x):
                    return unpack_ints(x, typecode, bits_per_sample, runlen)

            decompress = CONST.TIFF_DECOMPESSORS[self.compression]
            if self.compression == 'jpeg':
                table = self.jpeg_tables if 'jpeg_tables' in tags else b''

                def decompress(x):
                    return decode_jpeg(x, table, self.photometric)

            if self.is_tiled:
                result = numpy.empty(shape, dtype)
                tw, tl, td, pl = 0, 0, 0, 0
                for offset, bytecount in zip(offsets, byte_counts):
                    fh.seek(offset)
                    tile = fh.read(bytecount)
                    if lsb2msb:
                        tile = reverse_bitorder(tile)
                    tile = decompress(tile)
                    tile = unpack(tile)
                    try:
                        tile.shape = tile_shape
                    except ValueError:
                        # incomplete tiles; see gdal issue #1179
                        warnings.warn("invalid tile data")
                        t = numpy.zeros(tile_shape, dtype).reshape(-1)
                        s = min(tile.size, t.size)
                        t[:s] = tile[:s]
                        tile = t.reshape(tile_shape)
                    if self.predictor == 'horizontal':
                        numpy.cumsum(tile, axis=-2, dtype=dtype, out=tile)
                    elif self.predictor == 'float':
                        raise NotImplementedError()
                    result[0, pl, td:td+tile_depth,
                           tl:tl+tile_length, tw:tw+tile_width, :] = tile
                    del tile
                    tw += tile_width
                    if tw >= shape[4]:
                        tw, tl = 0, tl + tile_length
                        if tl >= shape[3]:
                            tl, td = 0, td + tile_depth
                            if td >= shape[2]:
                                td, pl = 0, pl + 1
                result = result[...,
                                :image_depth, :image_length, :image_width, :]
            else:
                strip_size = self.rows_per_strip * self.image_width
                if self.planar_configuration == 'contig':
                    strip_size *= self.samples_per_pixel
                result = numpy.empty(shape, dtype).reshape(-1)
                index = 0
                for offset, bytecount in zip(offsets, byte_counts):
                    fh.seek(offset)
                    strip = fh.read(bytecount)
                    if lsb2msb:
                        strip = reverse_bitorder(strip)
                    strip = decompress(strip)
                    strip = unpack(strip)
                    size = min(result.size, strip.size, strip_size,
                               result.size - index)
                    result[index:index+size] = strip[:size]
                    del strip
                    index += size

        result.shape = self._shape

        if self.predictor and not (self.is_tiled and not self.is_contiguous):
            if self.parent.is_lsm and not self.compression:
                pass  # work around bug in LSM510 software
            elif self.predictor == 'horizontal':
                numpy.cumsum(result, axis=-2, dtype=dtype, out=result)
            elif self.predictor == 'float':
                result = decode_floats(result)
        if colormapped and self.is_indexed:
            if self.color_map.shape[1] >= 2**bits_per_sample:
                # FluoView and LSM might fail here
                result = apply_colormap(result[:, 0:1, :, :, :, 0:1],
                                        self.color_map)
        elif rgbonly and self.is_rgb and 'extra_samples' in tags:
            # return only RGB and first alpha channel if exists
            extra_samples = self.extra_samples
            if tags['extra_samples'].count == 1:
                extra_samples = (extra_samples,)
            for i, exs in enumerate(extra_samples):
                if exs in ('unassalpha', 'assocalpha', 'unspecified'):
                    if self.is_contig:
                        result = result[..., [0, 1, 2, 3+i]]
                    else:
                        result = result[:, [0, 1, 2, 3+i]]
                    break
            else:
                if self.is_contig:
                    result = result[..., :3]
                else:
                    result = result[:, :3]

        if squeeze:
            try:
                result.shape = self.shape
            except ValueError:
                warnings.warn("failed to reshape from %s to %s" % (
                    str(result.shape), str(self.shape)))

        if scale_mdgel and self.parent.is_mdgel:
            # MD Gel stores private metadata in the second page
            page1 = self.parent.pages[1]
            if page1.md_file_tag in (2, 128):
                scale = page1.md_scale_pixel
                scale = scale[0] / scale[1]  # rational
                result = result.astype('float32')
                if page1.md_file_tag == 2:
                    result **= 2  # squary root data format
                result *= scale

        if closed:
            # TODO: file should remain open if an exception occurred above
            fh.close()
        return result

    def aspage(self):
        return self

    @property
    def keyframe(self):
        return self

    @keyframe.setter
    def keyframe(self, index):
        return

    @lazyattr
    def offsets_byte_counts(self):
        """Return simplified offsets and byte_counts."""
        if self.is_contiguous:
            offset, byte_count = self.is_contiguous
            return [offset], [byte_count]
        return clean_offsets_counts(self.data_offsets, self.data_byte_counts)

    @lazyattr
    def is_contiguous(self):
        """Return offset and size of contiguous data, else None.

        Excludes prediction, fill_order, and colormapping.

        """
        if self.compression or self.bits_per_sample not in (8, 16, 32, 64):
            return
        if self.is_tiled:
            if (self.image_width != self.tile_width or
                    self.image_length % self.tile_length or
                    self.tile_width % 16 or self.tile_length % 16):
                return
            if ('image_depth' in self.tags and 'tile_depth' in self.tags and
                    (self.image_length != self.tile_length or
                     self.image_depth % self.tile_depth)):
                return

        offsets = self.data_offsets
        byte_counts = self.data_byte_counts
        if len(offsets) == 1:
            return offsets[0], byte_counts[0]
        if self.is_stk or all(offsets[i] + byte_counts[i] == offsets[i+1] or
                              byte_counts[i+1] == 0  # no data/ignore offset
                              for i in range(len(offsets)-1)):
            return offsets[0], sum(byte_counts)

    @lazyattr
    def is_final(self):
        """Return if page's image data is stored in final form.

        Excluding byte-swapping and color-mapping.

        """
        return (self.is_contiguous and self.fill_order == 'msb2lsb' and
                not self.predictor and not self.is_chroma_subsampled)

    def is_memmappable(self, rgbonly, colormapped):
        """Return if page's image data in file can be memory-mapped."""
        return (self.parent.filehandle.is_file and
                self.is_final and
                (self.bits_per_sample == 8 or self.parent.is_native) and
                not (rgbonly and 'extra_samples' in self.tags) and
                not (colormapped and self.is_indexed))

    def __getattr__(self, name):
        """Return and validate tag value."""
        if name in self.tags:
            tag = self.tags[name]
            if tag.code in CONST.TIFF_TAGS:
                (name, _, _, _, validate) = CONST.TIFF_TAGS[tag.code]
                if validate:
                    try:
                        if tag.count == 1:
                            value = validate[tag.value]
                        else:
                            value = tuple(validate[val] for val in tag.value)
                    except KeyError:
                        raise ValueError(
                            "%s.value (%s) not supported" % (name, tag.value))
                else:
                    value = tag.value
            else:
                value = tag.value
            setattr(self, name, value)
            return value
        if name in CONST.TIFF_TAGS_DEFAULTS:
            value = CONST.TIFF_TAGS_DEFAULTS[name]
            setattr(self, name, value)
            return value
        # if name in CONST.TIFF_TAGS_NAMES:
        raise AttributeError("'%s' object has no attribute '%s'" %
                             (self.__class__.__name__, name))

    def __str__(self):
        """Return string containing information about page."""
        s = '  '.join(s for s in (
            'x'.join(str(i) for i in self.shape),
            str(self.dtype),
            '%s bit' % str(self.bits_per_sample),
            self.photometric if 'photometric' in self.tags else '',
            self.compression if self.compression else 'raw',
            '|'.join(t for t in CONST.TIFF_PAGE_ATTRS
                     if getattr(self, 'is_' + t)),
            '|'.join(t for t in CONST.TIFF_FILE_ATTRS
                     if getattr(self, 'is_' + t))
            ) if s)
        return "TiffPage %i  %s" % (self.index, s)

    def info(self, verbose=True):
        """Return string with detailed information about page."""
        result = [str(self)]
        tags = self.tags
        result.append(
            '\n'.join(str(t)[:CONST.PRINT_LINE_WIDTH].lstrip()
                      for t in sorted(tags.values(), key=lambda x: x.code)))
        if verbose:
            for name in ('image_description', 'software', 'artist'):
                if name not in tags:
                    continue
                value = tags[name].value
                if len(value) < CONST.PRINT_LINE_WIDTH - len(name) - 20:
                    continue
                try:
                    result.append('%s\n%s' % (name.upper(), pprint(value)))
                except Exception:
                    pass
            if self.is_indexed:
                result.append('Color Map: %s, %s' % (self.color_map.shape,
                                                     self.color_map.dtype))
            for attr in ('exif_ifd', 'gps_ifd',
                         'andor_metadata', 'epics_metadata', 'mm_header',
                         'lsm_metadata', 'stk_metadata', 'nih_metadata',
                         'imagej_metadata', 'micromanager_metadata',
                         'tvips_metadata', 'sfeg_metadata', 'sem_metadata',
                         'metaseries_metadata', 'helios_metadata',
                         'fluoview_metadata', 'scanimage_metadata',
                         'pilatus_metadata'
                         ):
                if hasattr(self, attr) and getattr(self, attr, False):
                    result.append('\n'.join((attr.upper(),
                                             pprint(getattr(self, attr)))))

        return '\n\n'.join(result)

    @property
    def ndim(self):
        """Return number of array dimensions."""
        return len(self.shape)

    @property
    def size(self):
        """Return number of elements in array."""
        return product(self.shape)

    @lazyattr
    def andor_metadata(self):
        """Return consolidated metadata from Andor tags as dict.

        Remove Andor tags from self.tags.

        """
        if not self.is_andor:
            return
        tags = self.tags
        result = {'id': bytes2str(tags['andor'].value)}
        for tag in list(self.tags.values()):
            code = tag.code
            if not 4864 < code < 5031:
                continue
            key = CONST.ANDOR_TAGS.get(code, code)
            value = tag.value
            if isinstance(value, bytes):
                value = bytes2str(value)
            result[key] = value
            del tags[tag.name]
        return result

    @lazyattr
    def epics_metadata(self):
        """Return consolidated metadata from EPICS areaDetector tags as dict.

        Remove areaDetector tags from self.tags.

        """
        # TODO: obtain test file
        if not self.is_epics:
            return
        result = {}
        tags = self.tags
        for tag in list(self.tags.values()):
            code = tag.code
            if not 65000 < code < 65500:
                continue
            value = bytes2str(tag.value)
            if code == 65000:
                result['timeStamp'] = float(value)
            elif code == 65001:
                result['uniqueID'] = int(value)
            elif code == 65002:
                result['epicsTS'] = int(value)
            elif code == 65003:
                result['epicsTS'] = int(value)
            else:
                key, value = value.split(':')
                result[key] = astype(value)
            del tags[tag.name]
        return result

    @lazyattr
    def lsm_metadata(self):
        """Return LSM metadata from lsm_info tag and subrecords as dict."""
        if not self.is_lsm:
            return
        fh = self.parent.filehandle
        result = recarray2dict(self.lsm_info)
        # read LSM info subrecords at offsets
        for name, reader in CONST.LSM_INFO_READERS.items():
            offset = result.get('offset_' + name, 0)
            if offset < 8:
                continue
            fh.seek(offset)
            try:
                result[name] = reader(fh)
            except ValueError:
                pass
        return result

    @lazyattr
    def stk_metadata(self):
        """Return STK metadata from UIC tags as dict."""
        if not self.is_stk:
            return
        tags = self.tags
        result = {}
        result['number_planes'] = tags['uic2tag'].count
        if 'image_description' in tags:
            result['plane_descriptions'] = self.image_description.split(b'\0')
            # result['plane_descriptions'] = stk_description_metadata(
            #    self.image_description)
        if 'uic1tag' in tags:
            result.update(tags['uic1tag'].value)
        if 'uic3tag' in tags:
            result.update(tags['uic3tag'].value)  # wavelengths
        if 'uic4tag' in tags:
            result.update(tags['uic4tag'].value)  # override uic1 tags
        uic2tag = tags['uic2tag'].value
        result['z_distance'] = uic2tag['z_distance']
        result['time_created'] = uic2tag['time_created']
        result['time_modified'] = uic2tag['time_modified']
        try:
            result['datetime_created'] = numpy.array(
                [julian_datetime(*dt) for dt in
                 zip(uic2tag['date_created'], uic2tag['time_created'])],
                dtype='datetime64[ns]')
            result['datetime_modified'] = numpy.array(
                [julian_datetime(*dt) for dt in
                 zip(uic2tag['date_modified'], uic2tag['time_modified'])],
                dtype='datetime64[ns]')
        except ValueError as e:
            warnings.warn("stk_metadata: %s" % e)
        return result

    @lazyattr
    def imagej_metadata(self):
        """Return consolidated ImageJ metadata as dict."""
        if not self.is_imagej:
            return
        result = imagej_description_metadata(self.is_imagej)
        if 'imagej_metadata' in self.tags:
            try:
                result.update(imagej_metadata(
                    self.tags['imagej_metadata'].value,
                    self.tags['imagej_byte_counts'].value,
                    self.parent.byteorder))
            except Exception as e:
                warnings.warn(str(e))
        return result

    @lazyattr
    def metaseries_metadata(self):
        """Return MetaSeries metadata from image description as dict."""
        if not self.is_metaseries:
            return
        return metaseries_description_metadata(self.image_description)

    @lazyattr
    def fluoview_metadata(self):
        """Return FluoView metadata from image description as dict."""
        if not self.is_fluoview:
            return
        return fluoview_description_metadata(self.image_description)

    @lazyattr
    def scanimage_metadata(self):
        """Return ScanImage metadata from image description as dict."""
        if not self.is_scanimage:
            return
        # TODO: scanimage_artist_metadata
        return scanimage_description_metadata(self.image_description)

    @lazyattr
    def pilatus_metadata(self):
        """Return Pilatus metadata from image description as dict."""
        if not self.is_pilatus:
            return
        return pilatus_description_metadata(self.image_description)

    @lazyattr
    def is_indexed(self):
        """Page contains indexed, palette-colored image.

        Disable color-mapping for OME, LSM, STK, and ImageJ hyperstacks.

        """
        if (self.is_stk
                or self.is_lsm or (self.index and self.parent.is_lsm)
                or self.is_ome or (self.index and self.parent.is_ome)):
            return False
        if self.is_imagej:
            if b'mode' in self.is_imagej:
                return False
        elif (self.index and self.parent.is_imagej):
            return self.parent.pages[0].is_indexed
        return ('photometric' in self.tags and
                self.tags['photometric'].value == 3)

    @property
    def is_rgb(self):
        """Page contains RGB image."""
        return ('photometric' in self.tags and
                self.tags['photometric'].value == 2)

    @property
    def is_contig(self):
        """Page contains contiguous image."""
        if 'planar_configuration' in self.tags:
            return self.tags['planar_configuration'].value == 1
        return True

    @lazyattr
    def is_tiled(self):
        """Page contains tiled image."""
        return 'tile_width' in self.tags

    @property
    def is_reduced(self):
        """Page is reduced image of another image."""
        return ('new_subfile_type' in self.tags and
                self.tags['new_subfile_type'].value & 1)

    @property
    def is_chroma_subsampled(self):
        """Page contains chroma subsampled image."""
        return ('ycbcr_subsampling' in self.tags and
                self.tags['ycbcr_subsampling'].value != (1, 1))

    @lazyattr
    def is_imagej(self):
        """Return ImageJ description if exists, else None."""
        if 'image_description' in self.tags:
            description = self.tags['image_description'].value
            if description[:7] == b'ImageJ=':
                return description
            if 'image_description_1' in self.tags:
                # Micromanager
                description = self.tags['image_description_1'].value
                if description[:7] == b'ImageJ=':
                    return description

    @lazyattr
    def is_shaped(self):
        """Return description containing array shape if exists, else None."""
        if 'image_description' in self.tags:
            description = self.tags['image_description'].value
            if description[:1] == b'{' and b'"shape":' in description:
                return description
            if description[:6] == b'shape=':
                return description
            if 'image_description_1' in self.tags:
                description = self.tags['image_description_1'].value
                if description[:1] == b'{' and b'"shape":' in description:
                    return description
                if description[:6] == b'shape=':
                    return description

    @property
    def is_mdgel(self):
        """Page contains md_file_tag tag."""
        return 'md_file_tag' in self.tags

    @property
    def is_mediacy(self):
        """Page contains Media Cybernetics Id tag."""
        return ('mc_id' in self.tags and
                self.tags['mc_id'].value.startswith(b'MC TIFF'))

    @property
    def is_stk(self):
        """Page contains UIC2Tag tag."""
        return 'uic2tag' in self.tags

    @property
    def is_lsm(self):
        """Page contains LSM_INFO tag."""
        return 'lsm_info' in self.tags

    @property
    def is_fluoview(self):
        """Page contains FluoView MM_STAMP tag."""
        return 'mm_stamp' in self.tags

    @property
    def is_nih(self):
        """Page contains NIH image header."""
        return 'nih_metadata' in self.tags

    @property
    def is_sgi(self):
        """Page contains SGI image and tile depth tags."""
        return 'image_depth' in self.tags and 'tile_depth' in self.tags

    @property
    def is_vista(self):
        """Software tag is 'ISS Vista'."""
        return ('software' in self.tags and
                self.tags['software'].value == b'ISS Vista')

    @property
    def is_metaseries(self):
        """Page contains MDS MetaSeries metadata in image_description tag."""
        if (self.index > 1
                or 'image_description' not in self.tags
                or 'software' not in self.tags
                or self.tags['software'].value != b'MetaSeries'):
            return False
        d = self.tags['image_description'].value.strip()
        return d.startswith(b'<MetaData>') and d.endswith(b'</MetaData>')

    @property
    def is_ome(self):
        """Page contains OME-XML in image_description tag."""
        if self.index > 1 or 'image_description' not in self.tags:
            return False
        d = self.tags['image_description'].value.strip()
        return d.startswith(b'<?xml version=') and d.endswith(b'</OME>')

    @property
    def is_scn(self):
        """Page contains Leica SCN XML in image_description tag."""
        if self.index > 1 or 'image_description' not in self.tags:
            return False
        d = self.tags['image_description'].value.strip()
        return d.startswith(b'<?xml version=') and d.endswith(b'</scn>')

    @property
    def is_micromanager(self):
        """Page contains Micro-Manager metadata."""
        return 'micromanager_metadata' in self.tags

    @property
    def is_andor(self):
        """Page contains Andor Technology tags."""
        return 'andor' in self.tags

    @property
    def is_pilatus(self):
        """Page contains Pilatus tags."""
        return ('software' in self.tags and
                self.software.startswith(b'TVX TIFF'))

    @property
    def is_epics(self):
        """Page contains EPICS areaDetector tags."""
        return ('image_description' in self.tags and
                self.image_description == b'EPICS areaDetector')

    @property
    def is_tvips(self):
        """Page contains TVIPS metadata."""
        return 'tvips_metadata' in self.tags

    @property
    def is_fei(self):
        """Page contains SFEG or HELIOS metadata."""
        return 'sfeg_metadata' in self.tags or 'helios_metadata' in self.tags

    @property
    def is_sem(self):
        """Page contains Zeiss SEM metadata."""
        return 'sem_metadata' in self.tags

    @property
    def is_svs(self):
        """Page contains Aperio metadata."""
        return ('image_description' in self.tags and
                self.image_description.startswith(b'Aperio Image Library'))

    @property
    def is_scanimage(self):
        """Page contains ScanImage metadata."""
        return (('image_description' in self.tags and
                 self.image_description.startswith(b'state.config')) or
                ('software' in self.tags and
                 self.software.startswith(b'SI.LINE_FORMAT_VERSION')))


class TiffFrame(object):
    """Lightweight TIFF image file directory (IFD).

    Only a limited number of tag values are read from file, e.g. strip_offsets,
    and strip_byte_counts. Other tag values are assumed to be identical with a
    specified TiffPage instance, the keyframe.

    This is intended to reduce resource usage and speed up reading data from
    file, not for introspection of metadata.

    Not compatible with Python 2.

    """
    __slots__ = ('keyframe', 'parent', 'index', 'offset',
                 'data_offsets', 'data_byte_counts',
                 'image_description', 'image_description_1',
                 # 'x_position', 'y_position',
                 'page_name', 'page_number', 'datetime')

    tags = {}  # TiffFrame instances have no tags

    def __init__(self, parent, index, keyframe):
        """Read specified tags from file.

        The file handle position must be at the offset to a valid IFD.

        """
        self.keyframe = keyframe
        self.parent = parent
        self.index = index

        unpack = struct.unpack
        fh = parent.filehandle
        self.offset = fh.tell()
        try:
            tagno = unpack(parent.tagno_format, fh.read(parent.tagno_size))[0]
            if tagno > 4096:
                raise ValueError("suspicious number of tags")
        except Exception:
            raise ValueError("corrupted page list at offset %i" % self.offset)

        attrs = {}
        tag_codes = CONST.TIFF_FRAME_TAGS
        tag_size = parent.tag_size
        code_format = parent.tag_format1[:2]

        for _ in range(tagno):
            data = fh.read(tag_size)
            code = unpack(code_format, data[:2])[0]
            if code not in tag_codes:
                continue
            fh.seek(-tag_size, 1)
            try:
                tag = TiffTag(parent)
            except TiffTag.Error as e:
                warnings.warn(str(e))
                continue
            if code == 273 or code == 324:
                attrs['data_offsets'] = tag.value
            elif code == 279 or code == 325:
                attrs['data_byte_counts'] = tag.value
            else:
                tagname = tag.name
                if tagname not in attrs:
                    attrs[tagname] = tag.value
                else:
                    # some files contain multiple tags with same code
                    i = 1
                    while True:
                        name = "%s_%i" % (tagname, i)
                        if name not in attrs:
                            attrs[name] = tag.value
                            break

        for attr, value in attrs.items():
            setattr(self, attr, value)

    def aspage(self):
        """Return TiffPage from file."""
        self.parent.filehandle.seek(self.offset)
        return TiffPage(self.parent, index=self.index, keyframe=None)

    def asarray(self, *args, **kwargs):
        """Read image data from file and return as numpy array."""
        # TODO: fix TypeError on Python 2
        #   "TypeError: unbound method asarray() must be called with TiffPage
        #   instance as first argument (got TiffFrame instance instead)"
        kwargs['validate'] = False
        return TiffPage.asarray(self, *args, **kwargs)

    @property
    def offsets_byte_counts(self):
        """Return simplified offsets and byte_counts."""
        if self.keyframe.is_contiguous:
            return self.data_offsets[:1], self.keyframe.is_contiguous[1:]
        return clean_offsets_counts(self.data_offsets, self.data_byte_counts)

    @property
    def is_contiguous(self):
        """Return offset and size of contiguous data, else None."""
        if self.keyframe.is_contiguous:
            return self.data_offsets[0], self.keyframe.is_contiguous[1]

    def is_memmappable(self, rgbonly, colormapped):
        """Return if page's image data in file can be memory-mapped."""
        return self.keyframe.is_memmappable(rgbonly, colormapped)

    def __getattr__(self, name):
        """Return attribute from keyframe."""
        if name in CONST.TIFF_FRAME_ATTRS:
            return getattr(self.keyframe, name)
        raise AttributeError("'%s' object has no attribute '%s'" %
                             (self.__class__.__name__, name))

    def __str__(self):
        """Return string containing information about frame."""
        s = '  '.join(s for s in (
            'x'.join(str(i) for i in self.shape),
            str(self.dtype)))
        return "TiffFrame %i  %s" % (self.index, s)

    def info(self, verbose=True):
        """Return string with detailed information about frame."""
        result = [str(self)]
        names = ['data_offsets', 'data_byte_count'] + [
            CONST.TIFF_TAGS[i][0] for i in sorted(CONST.TIFF_FRAME_TAGS)]
        for name in names:
            if getattr(self, name, False):
                result.append('%s %s' % (name, getattr(self, name)))
        return '\n'.join(line[:CONST.PRINT_LINE_WIDTH] for line in result)

    @property
    def is_shaped(self):
        """Return description containing array shape if exists, else None."""
        d = getattr(self, 'image_description', False)
        if d:
            if b'"shape":' in d or d.startswith(b'shape=('):
                return d
            d = getattr(self, 'image_description_1', False)
            if d and (b'"shape":' in d or d.startswith(b'shape=(')):
                return d


class TiffTag(object):
    """TIFF tag structure.

    Attributes
    ----------
    name : string
        Attribute name of tag.
    code : int
        Decimal code of tag.
    dtype : str
        Datatype of tag data. One of TIFF_DATA_TYPES.
    count : int
        Number of values.
    value : various types
        Tag data as Python object.
    value_offset : int
        Location of value in file.
    offset : int
        Location of tag in file.

    All attributes are read-only.

    """
    __slots__ = ('code', 'name', 'count', 'dtype', 'offset',
                 'value', 'value_offset', '_value', '_type')

    class Error(Exception):
        pass

    def __init__(self, parent, **kwargs):
        """Initialize instance from file.

        The file handle position must be at an offset to a TIFF tag header.

        """
        fh = parent.filehandle
        byteorder = parent.byteorder
        unpack = struct.unpack
        tiff_tags = CONST.TIFF_TAGS
        tiff_custom_tags = CONST.TIFF_CUSTOM_TAGS
        offset_size = parent.offset_size

        self.offset = fh.tell()
        self.value_offset = self.offset + offset_size + 4

        data = fh.read(parent.tag_size)
        code, dtype = unpack(parent.tag_format1, data[:4])
        count, value = unpack(parent.tag_format2, data[4:])
        self._value = value
        self._type = dtype

        if code in tiff_tags:
            name, _, _, count_, _ = tiff_tags[code]
            if count_ and count_ != count:
                count = count_
                warnings.warn("incorrect count for tag '%s'" % name)
        elif code in tiff_custom_tags:
            name = tiff_custom_tags[code][0]
        else:
            name = str(code)

        try:
            dtype = CONST.TIFF_DATA_TYPES[self._type]
        except KeyError:
            raise TiffTag.Error("unknown tag data type %i" % self._type)

        fmt = '%s%i%s' % (byteorder, count * int(dtype[0]), dtype[1])
        size = struct.calcsize(fmt)
        if size > offset_size or code in tiff_custom_tags:
            pos = fh.tell()
            self.value_offset = offset = unpack(parent.offset_format, value)[0]
            if offset < 8 or offset > fh.size - size:
                raise TiffTag.Error("invalid tag value offset")
            # if offset % 2:
            #     warnings.warn("tag value does not begin on word boundary")
            fh.seek(offset)
            if code in tiff_custom_tags:
                readfunc = tiff_custom_tags[code][1]
                value = readfunc(fh, byteorder, dtype, count, offset_size)
            elif code in tiff_tags or dtype[-1] == 's':
                value = unpack(fmt, fh.read(size))
            else:
                value = read_numpy(fh, byteorder, dtype, count, offset_size)
            fh.seek(pos)
        else:
            value = unpack(fmt, value[:size])

        if code not in tiff_custom_tags and code not in CONST.TIFF_TAGS_TUPLE:
            if len(value) == 1:
                value = value[0]

        if self._type != 7 and dtype[-1] == 's' and isinstance(value, bytes):
            # TIFF ASCII fields can contain multiple strings,
            #   each terminated with a NUL
            value = stripascii(value)

        self.code = code
        self.name = name
        self.dtype = dtype
        self.count = count
        self.value = value

    def _fix_lsm_bitspersample(self, parent):
        """Correct LSM bitspersample tag.

        Old LSM writers may use a separate region for two 16-bit values,
        although they fit into the tag value element of the tag.

        """
        if self.code == 258 and self.count == 2:
            # TODO: test this case; need example file
            warnings.warn("correcting LSM bitspersample tag")
            tof = parent.offset_format[parent.offset_size]
            self.value_offset = struct.unpack(tof, self._value)[0]
            parent.filehandle.seek(self.value_offset)
            self.value = struct.unpack("<HH", parent.filehandle.read(4))

    def as_str(self):
        """Return value as human readable string."""
        return ((str(self.value).split('\n', 1)[0]) if (self._type != 7)
                else '<undefined>')

    def __str__(self):
        """Return string containing information about tag."""
        value = ((str(self.value).split('\n', 1)[0]) if (self._type != 7)
                 else '<undefined>')
        tcode = "%i%s" % (self.count * int(self.dtype[0]), self.dtype[1])
        line = "TiffTag %i  %s  %s  %s" % (self.code, self.name, tcode, value)
        return line


class TiffPageSeries(object):
    """Series of TIFF pages with compatible shape and data type.

    Attributes
    ----------
    pages : list of TiffPage
        Sequence of TiffPages in series.
    dtype : numpy.dtype or str
        Data type of the image array in series.
    shape : tuple
        Dimensions of the image array in series.
    axes : str
        Labels of axes in shape. See TiffPage.axes.
    offset : int or None
        Position of image data in file if memory-mappable, else None.

    """
    def __init__(self, pages, shape, dtype, axes,
                 parent=None, name=None, stype=None):
        self.index = 0
        self.pages = pages
        self.shape = tuple(shape)
        self.axes = ''.join(axes)
        self.dtype = numpy.dtype(dtype)
        self.stype = stype if stype else ''
        self.name = name if name else ''
        if parent:
            self.parent = parent
        elif len(pages):
            self.parent = pages[0].parent
        else:
            self.parent = None

    def asarray(self, memmap=False):
        """Return image data from series of TIFF pages as numpy array.

        Parameters
        ----------
        memmap : bool
            If True, return an array stored in a binary file on disk
            if possible.

        """
        if self.parent:
            return self.parent.asarray(series=self, memmap=memmap)

    @lazyattr
    def offset(self):
        """Return offset to series data in file, if any."""
        if not self.pages:
            return

        pos = 0
        for page in self.pages:
            if page is None:
                return
            if not page.is_final:
                return
            if not pos:
                pos = page.is_contiguous[0] + page.is_contiguous[1]
                continue
            if pos != page.is_contiguous[0]:
                return
            pos += page.is_contiguous[1]

        page = self.pages[0]
        offset = page.is_contiguous[0]
        if (page.is_imagej or page.is_shaped) and len(self.pages) == 1:
            # truncated files
            return offset
        if pos == offset + product(self.shape) * self.dtype.itemsize:
            return offset

    @property
    def ndim(self):
        """Return number of array dimensions."""
        return len(self.shape)

    @property
    def size(self):
        """Return number of elements in array."""
        return int(product(self.shape))

    def __len__(self):
        """Return number of TiffPages in series."""
        return len(self.pages)

    def __getitem__(self, key):
        """Return specified TiffPage."""
        return self.pages[key]

    def __iter__(self):
        """Return iterator over TiffPages in series."""
        return iter(self.pages)

    def __str__(self):
        """Return string with information about series."""
        s = '  '.join(s for s in (
            snipstr("'%s'" % self.name, 20) if self.name else '',
            'x'.join(str(i) for i in self.shape),
            str(self.dtype),
            self.axes,
            self.stype.lower(),
            '%i pages' % len(self.pages),
            ('offset=%i' % self.offset) if self.offset else '') if s)
        return 'TiffPageSeries %i  %s' % (self.index, s)


class TiffSequence(object):
    """Sequence of image files.

    The data in all files must match.

    Attributes
    ----------
    files : list
        List of file names.
    shape : tuple
        Shape of image sequence.
    axes : str
        Labels of axes in shape.

    Examples
    --------
    >>> imsave('temp_C001T001.tif', numpy.random.rand(64, 64))
    >>> imsave('temp_C001T002.tif', numpy.random.rand(64, 64))
    >>> tifs = TiffSequence("temp_C001*.tif")
    >>> tifs.shape
    (1, 2)
    >>> tifs.axes
    'CT'
    >>> data = tifs.asarray()
    >>> data.shape
    (1, 2, 64, 64)

    """
    _patterns = {
        'axes': r"""
            # matches Olympus OIF and Leica TIFF series
            _?(?:(q|l|p|a|c|t|x|y|z|ch|tp)(\d{1,4}))
            _?(?:(q|l|p|a|c|t|x|y|z|ch|tp)(\d{1,4}))?
            _?(?:(q|l|p|a|c|t|x|y|z|ch|tp)(\d{1,4}))?
            _?(?:(q|l|p|a|c|t|x|y|z|ch|tp)(\d{1,4}))?
            _?(?:(q|l|p|a|c|t|x|y|z|ch|tp)(\d{1,4}))?
            _?(?:(q|l|p|a|c|t|x|y|z|ch|tp)(\d{1,4}))?
            _?(?:(q|l|p|a|c|t|x|y|z|ch|tp)(\d{1,4}))?
            """}

    class ParseError(Exception):
        pass

    def __init__(self, files, imread=TiffFile, pattern='axes',
                 *args, **kwargs):
        """Initialize instance from multiple files.

        Parameters
        ----------
        files : str, or sequence of str
            Glob pattern or sequence of file names.
            Binary streams are not supported.
        imread : function or class
            Image read function or class with asarray function returning numpy
            array from single file.
        pattern : str
            Regular expression pattern that matches axes names and sequence
            indices in file names.
            By default, this matches Olympus OIF and Leica TIFF series.

        """
        if isinstance(files, basestring):
            files = natural_sorted(glob.glob(files))
        files = list(files)
        if not files:
            raise ValueError("no files found")
        if not isinstance(files[0], basestring):
            raise ValueError("not a file name")
        self.files = files

        if hasattr(imread, 'asarray'):
            # redefine imread
            _imread = imread

            def imread(fname, *args, **kwargs):
                with _imread(fname) as im:
                    return im.asarray(*args, **kwargs)

        self.imread = imread

        self.pattern = self._patterns.get(pattern, pattern)
        try:
            self._parse()
            if not self.axes:
                self.axes = 'I'
        except self.ParseError:
            self.axes = 'I'
            self.shape = (len(files),)
            self._start_index = (0,)
            self._indices = tuple((i,) for i in range(len(files)))

    def __str__(self):
        """Return string with information about image sequence."""
        return "\n".join([
            self.files[0],
            '* files: %i' % len(self.files),
            '* axes: %s' % self.axes,
            '* shape: %s' % str(self.shape)])

    def __len__(self):
        return len(self.files)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        pass

    def asarray(self, memmap=False, tempdir=None, *args, **kwargs):
        """Read image data from all files and return as single numpy array.

        If memmap is True, return an array stored in a binary file on disk.
        The args and kwargs parameters are passed to the imread function.

        Raise IndexError or ValueError if image shapes do not match.

        """
        im = self.imread(self.files[0], *args, **kwargs)
        shape = self.shape + im.shape
        if memmap:
            with tempfile.NamedTemporaryFile(dir=tempdir) as fh:
                result = numpy.memmap(fh, dtype=im.dtype, shape=shape)
        else:
            result = numpy.zeros(shape, dtype=im.dtype)
        result = result.reshape(-1, *im.shape)
        for index, fname in zip(self._indices, self.files):
            index = [i-j for i, j in zip(index, self._start_index)]
            index = numpy.ravel_multi_index(index, self.shape)
            im = self.imread(fname, *args, **kwargs)
            result[index] = im
        result.shape = shape
        return result

    def _parse(self):
        """Get axes and shape from file names."""
        if not self.pattern:
            raise self.ParseError("invalid pattern")
        pattern = re.compile(self.pattern, re.IGNORECASE | re.VERBOSE)
        matches = pattern.findall(self.files[0])
        if not matches:
            raise self.ParseError("pattern does not match file names")
        matches = matches[-1]
        if len(matches) % 2:
            raise self.ParseError("pattern does not match axis name and index")
        axes = ''.join(m for m in matches[::2] if m)
        if not axes:
            raise self.ParseError("pattern does not match file names")

        indices = []
        for fname in self.files:
            matches = pattern.findall(fname)[-1]
            if axes != ''.join(m for m in matches[::2] if m):
                raise ValueError("axes do not match within the image sequence")
            indices.append([int(m) for m in matches[1::2] if m])
        shape = tuple(numpy.max(indices, axis=0))
        start_index = tuple(numpy.min(indices, axis=0))
        shape = tuple(i-j+1 for i, j in zip(shape, start_index))
        if product(shape) != len(self.files):
            warnings.warn("files are missing. Missing data are zeroed")

        self.axes = axes.upper()
        self.shape = shape
        self._indices = indices
        self._start_index = start_index


class FileHandle(object):
    """Binary file handle.

    A limited, special purpose file handler that can:

    * handle embedded files (for CZI within CZI files)
    * re-open closed files (for multi file formats, such as OME-TIFF)
    * read and write numpy arrays and records from file like objects

    Only 'rb' and 'wb' modes are supported. Concurrently reading and writing
    of the same stream is untested.

    When initialized from another file handle, do not use it unless this
    FileHandle is closed.

    Attributes
    ----------
    name : str
        Name of the file.
    path : str
        Absolute path to file.
    size : int
        Size of file in bytes.
    is_file : bool
        If True, file has a filno and can be memory-mapped.

    All attributes are read-only.

    """
    __slots__ = ('_fh', '_file', '_mode', '_name', '_dir',
                 '_offset', '_size', '_close', 'is_file')

    def __init__(self, file, mode='rb', name=None, offset=None, size=None):
        """Initialize file handle from file name or another file handle.

        Parameters
        ----------
        file : str, binary stream, or FileHandle
            File name or seekable binary stream, such as a open file
            or BytesIO.
        mode : str
            File open mode in case 'file' is a file name. Must be 'rb' or 'wb'.
        name : str
            Optional name of file in case 'file' is a binary stream.
        offset : int
            Optional start position of embedded file. By default, this is
            the current file position.
        size : int
            Optional size of embedded file. By default, this is the number
            of bytes from the 'offset' to the end of the file.

        """
        self._fh = None
        self._file = file
        self._mode = mode
        self._name = name
        self._dir = ''
        self._offset = offset
        self._size = size
        self._close = True
        self.is_file = False
        self.open()

    def open(self):
        """Open or re-open file."""
        if self._fh:
            return  # file is open

        if isinstance(self._file, basestring):
            # file name
            self._file = os.path.realpath(self._file)
            self._dir, self._name = os.path.split(self._file)
            self._fh = open(self._file, self._mode)
            self._close = True
            if self._offset is None:
                self._offset = 0
        elif isinstance(self._file, FileHandle):
            # FileHandle
            self._fh = self._file._fh
            if self._offset is None:
                self._offset = 0
            self._offset += self._file._offset
            self._close = False
            if not self._name:
                if self._offset:
                    name, ext = os.path.splitext(self._file._name)
                    self._name = "%s@%i%s" % (name, self._offset, ext)
                else:
                    self._name = self._file._name
            if self._mode and self._mode != self._file._mode:
                raise ValueError('FileHandle has wrong mode')
            self._mode = self._file._mode
            self._dir = self._file._dir
        elif hasattr(self._file, 'seek'):
            # binary stream: open file, BytesIO
            try:
                self._file.tell()
            except Exception:
                raise ValueError("binary stream is not seekable")
            self._fh = self._file
            if self._offset is None:
                self._offset = self._file.tell()
            self._close = False
            if not self._name:
                try:
                    self._dir, self._name = os.path.split(self._fh.name)
                except AttributeError:
                    self._name = "Unnamed binary stream"
            try:
                self._mode = self._fh.mode
            except AttributeError:
                pass
        else:
            raise ValueError("The first parameter must be a file name, "
                             "seekable binary stream, or FileHandle")

        if self._offset:
            self._fh.seek(self._offset)

        if self._size is None:
            pos = self._fh.tell()
            self._fh.seek(self._offset, 2)
            self._size = self._fh.tell()
            self._fh.seek(pos)

        try:
            self._fh.fileno()
            self.is_file = True
        except Exception:
            self.is_file = False

    def read(self, size=-1):
        """Read 'size' bytes from file, or until EOF is reached."""
        if size < 0 and self._offset:
            size = self._size
        return self._fh.read(size)

    def write(self, bytestring):
        """Write bytestring to file."""
        return self._fh.write(bytestring)

    def flush(self):
        """Flush write buffers if applicable."""
        return self._fh.flush()

    def memmap_array(self, dtype, shape, offset=0, mode='r', order='C'):
        """Return numpy.memmap of data stored in file."""
        if not self.is_file:
            raise ValueError("Can not memory-map file without fileno")
        return numpy.memmap(self._fh, dtype=dtype, mode=mode,
                            offset=self._offset + offset,
                            shape=shape, order=order)

    def read_array(self, dtype, count=-1, sep=""):
        """Return numpy array from file.

        Work around numpy issue #2230, "numpy.fromfile does not accept
        StringIO object" https://github.com/numpy/numpy/issues/2230.

        """
        dtype = numpy.dtype(dtype)
        try:
            return numpy.fromfile(self._fh, dtype, count, sep)
        except IOError:
            if count < 0:
                size = self._size
            else:
                size = count * dtype.itemsize
            data = self._fh.read(size)
            return numpy.fromstring(data, dtype, count, sep)

    def read_record(self, dtype, shape=1, byteorder=None):
        """Return numpy record from file."""
        try:
            rec = numpy.rec.fromfile(self._fh, dtype, shape,
                                     byteorder=byteorder)
        except Exception:
            dtype = numpy.dtype(dtype)
            if shape is None:
                shape = self._size // dtype.itemsize
            size = product(sequence(shape)) * dtype.itemsize
            data = self._fh.read(size)
            return numpy.rec.fromstring(data, dtype, shape,
                                        byteorder=byteorder)
        return rec[0] if shape == 1 else rec

    def write_empty(self, size):
        """Append size bytes to file. Position must be at end of file."""
        if size < 1:
            return
        self._fh.seek(size-1, 1)
        self._fh.write(b'\x00')

    def write_array(self, data):
        """Write numpy array to binary file."""
        try:
            data.tofile(self._fh)
        except Exception:
            # BytesIO
            self._fh.write(data.tostring())

    def tell(self):
        """Return file's current position."""
        return self._fh.tell() - self._offset

    def seek(self, offset, whence=0):
        """Set file's current position."""
        if self._offset:
            if whence == 0:
                self._fh.seek(self._offset + offset, whence)
                return
            elif whence == 2 and self._size > 0:
                self._fh.seek(self._offset + self._size + offset, 0)
                return
        self._fh.seek(offset, whence)

    def close(self):
        """Close file."""
        if self._close and self._fh:
            self._fh.close()
            self._fh = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __getattr__(self, name):
        """Return attribute from underlying file object."""
        if self._offset:
            warnings.warn(
                "FileHandle: '%s' not implemented for embedded files" % name)
        return getattr(self._fh, name)

    @property
    def name(self):
        return self._name

    @property
    def dirname(self):
        return self._dir

    @property
    def path(self):
        return os.path.join(self._dir, self._name)

    @property
    def size(self):
        return self._size

    @property
    def closed(self):
        return self._fh is None


class LazyConst(object):
    """Class whose attributes are computed on first access from its methods."""
    def __init__(self, cls):
        self._cls = cls
        self.__doc__ = getattr(cls, '__doc__')

    def __getattr__(self, name):
        func = getattr(self._cls, name)
        if not callable(func):
            return func
        try:
            value = func()
        except TypeError:
            # Python 2 unbound method
            value = func.__func__()
        setattr(self, name, value)
        return value


@LazyConst
class CONST(object):
    """Namespace for module constants."""

    def TIFF_TAGS():
        # Map TIFF tag code to
        #        (attribute name, default value, type, count, validator)
        return {
            254: ('new_subfile_type', 0, 4, 1, CONST.TIFF_SUBFILE_TYPES),
            255: ('subfile_type', None, 3, 1,
                  {0: 'undefined', 1: 'image', 2: 'reduced_image', 3: 'page'}),
            256: ('image_width', None, 4, 1, None),
            257: ('image_length', None, 4, 1, None),
            258: ('bits_per_sample', 1, 3, None, None),
            259: ('compression', 1, 3, 1, CONST.TIFF_COMPESSIONS),
            262: ('photometric', None, 3, 1, CONST.TIFF_PHOTOMETRICS),
            266: ('fill_order', 1, 3, 1, {1: 'msb2lsb', 2: 'lsb2msb'}),
            269: ('document_name', None, 2, None, None),
            270: ('image_description', None, 2, None, None),
            271: ('make', None, 2, None, None),
            272: ('model', None, 2, None, None),
            273: ('strip_offsets', None, 4, None, None),
            274: ('orientation', 1, 3, 1, CONST.TIFF_ORIENTATIONS),
            277: ('samples_per_pixel', 1, 3, 1, None),
            278: ('rows_per_strip', 2**32-1, 4, 1, None),
            279: ('strip_byte_counts', None, 4, None, None),
            280: ('min_sample_value', None, 3, None, None),
            281: ('max_sample_value', None, 3, None, None),  # 2**bitspersample
            282: ('x_resolution', None, 5, 1, None),
            283: ('y_resolution', None, 5, 1, None),
            284: ('planar_configuration', 1, 3, 1,
                  {1: 'contig', 2: 'separate'}),
            285: ('page_name', None, 2, None, None),
            286: ('x_position', None, 5, 1, None),
            287: ('y_position', None, 5, 1, None),
            292: ('group3_options', 0, 4, 1, CONST.TIFF_GROUP3_OPTIONS),
            296: ('resolution_unit', 2, 4, 1,
                  {1: None, 2: 'inch', 3: 'centimeter'}),
            297: ('page_number', None, 3, 2, None),
            301: ('transfer_function', None, 3, 3*256, None),
            305: ('software', None, 2, None, None),
            306: ('datetime', None, 2, None, None),
            315: ('artist', None, 2, None, None),
            316: ('host_computer', None, 2, None, None),
            317: ('predictor', 1, 3, 1,
                  {1: None, 2: 'horizontal', 3: 'float'}),
            318: ('white_point', None, 5, 2, None),
            319: ('primary_chromaticities', None, 5, 6, None),
            320: ('color_map', None, 3, None, None),
            322: ('tile_width', None, 4, 1, None),
            323: ('tile_length', None, 4, 1, None),
            324: ('tile_offsets', None, 4, None, None),
            325: ('tile_byte_counts', None, 4, None, None),
            330: ('sub_ifds', None, 4, None, None),
            336: ('dot_range', None, None, None, None),
            338: ('extra_samples', None, 3, None,
                  {0: 'unspecified', 1: 'assocalpha', 2: 'unassalpha'}),
            339: ('sample_format', 1, 3, None, CONST.TIFF_SAMPLE_FORMATS),
            340: ('smin_sample_value', None, None, None, None),
            341: ('smax_sample_value', None, None, None, None),
            346: ('indexed', 0, 3, 1, None),
            347: ('jpeg_tables', None, 7, None, None),
            513: ('jpeg_interchange_format', None, 4, 1, None),
            514: ('jpeg_interchange_format_length', None, 4, 1, None),
            529: ('ycbcr_coefficients', None, 5, 3, None),
            530: ('ycbcr_subsampling', (1, 1), 3, 2, None),
            531: ('ycbcr_positioning', (1, 1), 3, 1, None),
            532: ('reference_black_white', None, 5, 1, None),
            4864: ('andor', None, 2, None, None),
            32995: ('sgi_matteing', None, None, 1, None),  # use extra_samples
            32996: ('sgi_datatype', None, None, None, None),  # "
            32997: ('image_depth', 1, 4, 1, None),
            32998: ('tile_depth', None, 4, 1, None),
            33432: ('copyright', None, 1, None, None),
            33445: ('md_file_tag', None, 4, 1, None),
            33446: ('md_scale_pixel', None, 5, 1, None),
            33447: ('md_color_table', None, 3, None, None),
            33448: ('md_lab_name', None, 2, None, None),
            33449: ('md_sample_info', None, 2, None, None),
            33450: ('md_prep_date', None, 2, None, None),
            33451: ('md_prep_time', None, 2, None, None),
            33452: ('md_file_units', None, 2, None, None),
            33550: ('model_pixel_scale', None, 12, 3, None),
            33922: ('model_tie_point', None, 12, None, None),
            34735: ('geo_key_directory', None, 3, None, None),
            34736: ('geo_double_params', None, 12, None, None),
            34737: ('geo_ascii_params', None, 2, None, None),
            37510: ('user_comment', None, None, None, None),
            42112: ('gdal_metadata', None, 2, None, None),
            42113: ('gdal_nodata', None, 2, None, None),
            50289: ('mc_xy_position', None, 12, 2, None),
            50290: ('mc_z_position', None, 12, 1, None),
            50291: ('mc_xy_calibration', None, 12, 3, None),
            50292: ('mc_lens_lem_na_n', None, 12, 3, None),
            50293: ('mc_channel_name', None, 1, None, None),
            50294: ('mc_ex_wavelength', None, 12, 1, None),
            50295: ('mc_time_stamp', None, 12, 1, None),
            50838: ('imagej_byte_counts', None, None, None, None),
            51023: ('fibics_xml', None, 2, None, None),
            65200: ('flex_xml', None, 2, None, None),
        }

    def TIFF_CUSTOM_TAGS():
        # Map custom TIFF tag codes to attribute names and import functions
        return {
            700: ('xmp', read_bytes),
            34377: ('photoshop', read_numpy),
            33723: ('iptc', read_bytes),
            34675: ('icc_profile', read_bytes),
            33628: ('uic1tag', read_uic1tag),  # Universal Imaging Corp STK
            33629: ('uic2tag', read_uic2tag),
            33630: ('uic3tag', read_uic3tag),
            33631: ('uic4tag', read_uic4tag),
            34118: ('sem_metadata', read_sem_metadata),  # Zeiss SEM
            34361: ('mm_header', read_mm_header),  # Olympus FluoView
            34362: ('mm_stamp', read_mm_stamp),
            34386: ('mm_user_block', read_bytes),
            34412: ('lsm_info', read_lsm_info),  # Carl Zeiss LSM
            34680: ('sfeg_metadata', read_fei_metadata),  # S-FEG
            34682: ('helios_metadata', read_fei_metadata),  # Helios NanoLab
            37706: ('tvips_metadata', read_tvips_header),  # TVIPS EMMENU
            43314: ('nih_metadata', read_nih_image_header),
            # 40001: ('mc_ipwinscal', read_bytes),
            40100: ('mc_id_old', read_bytes),
            50288: ('mc_id', read_bytes),
            50296: ('mc_frame_properties', read_bytes),
            50839: ('imagej_metadata', read_bytes),
            51123: ('micromanager_metadata', read_json),
            34665: ('exif_ifd', read_exif_ifd),
            34853: ('gps_ifd', read_gps_ifd),
            40965: ('interoperability_ifd', read_interoperability_ifd)
        }

    def TIFF_TAGS_NAMES():
        return dict((v[0], c) for c, v in CONST.TIFF_TAGS.items())

    def TIFF_TAGS_DEFAULTS():
        # Tag default values
        return dict((name, validate[default] if validate else default)
                    for code, (name, default, dtype, count, validate)
                    in CONST.TIFF_TAGS.items()
                    if default is not None)

    def TIFF_TAGS_TUPLE():
        # Tags whose values must be stored as tuples
        return frozenset((273, 279, 324, 325, 530, 531))

    def TIFF_DATA_TYPES():
        # Map TIFF data types to numpy
        return {
            1: '1B',   # BYTE 8-bit unsigned integer.
            2: '1s',   # ASCII 8-bit byte that contains a 7-bit ASCII code;
                       #   the last byte must be NULL (binary zero).
            3: '1H',   # SHORT 16-bit (2-byte) unsigned integer
            4: '1I',   # LONG 32-bit (4-byte) unsigned integer.
            5: '2I',   # RATIONAL Two LONGs: the first represents the numerator
                       #   of a fraction; the second, the denominator.
            6: '1b',   # SBYTE An 8-bit signed (twos-complement) integer.
            7: '1s',   # UNDEFINED An 8-bit byte that may contain anything,
                       #   depending on the definition of the field.
            8: '1h',   # SSHORT A 16-bit (2-byte) signed (twos-complement)
                       #   integer.
            9: '1i',   # SLONG A 32-bit (4-byte) signed (twos-complement)
                       #   integer.
            10: '2i',  # SRATIONAL Two SLONGs: the first represents the
                       #   numerator of a fraction, the second the denominator.
            11: '1f',  # FLOAT Single precision (4-byte) IEEE format.
            12: '1d',  # DOUBLE Double precision (8-byte) IEEE format.
            13: '1I',  # IFD unsigned 4 byte IFD offset.
            # 14: '',   # UNICODE
            # 15: '',   # COMPLEX
            16: '1Q',  # LONG8 unsigned 8 byte integer (BigTiff)
            17: '1q',  # SLONG8 signed 8 byte integer (BigTiff)
            18: '1Q',  # IFD8 unsigned 8 byte IFD offset (BigTiff)
        }

    def TIFF_DATA_DTYPES():
        # Map numpy data types to TIFF
        return {'B': 1, 's': 2, 'H': 3, 'I': 4, '2I': 5, 'b': 6,
                'h': 8, 'i': 9, '2i': 10, 'f': 11, 'd': 12, 'Q': 16, 'q': 17}

    def TIFF_SAMPLE_FORMATS():
        return {
            1: 'uint',
            2: 'int',
            3: 'float',
            # 4: 'void',
            # 5: 'complex_int',
            6: 'complex',
        }

    def TIFF_SAMPLE_DTYPES():
        # Map TIFF sample formats and bits per sample to numpy dtype
        return {
            ('uint', 1): '?',  # bitmap
            ('uint', 2): 'B',
            ('uint', 3): 'B',
            ('uint', 4): 'B',
            ('uint', 5): 'B',
            ('uint', 6): 'B',
            ('uint', 7): 'B',
            ('uint', 8): 'B',
            ('uint', 9): 'H',
            ('uint', 10): 'H',
            ('uint', 11): 'H',
            ('uint', 12): 'H',
            ('uint', 13): 'H',
            ('uint', 14): 'H',
            ('uint', 15): 'H',
            ('uint', 16): 'H',
            ('uint', 17): 'I',
            ('uint', 18): 'I',
            ('uint', 19): 'I',
            ('uint', 20): 'I',
            ('uint', 21): 'I',
            ('uint', 22): 'I',
            ('uint', 23): 'I',
            ('uint', 24): 'I',
            ('uint', 25): 'I',
            ('uint', 26): 'I',
            ('uint', 27): 'I',
            ('uint', 28): 'I',
            ('uint', 29): 'I',
            ('uint', 30): 'I',
            ('uint', 31): 'I',
            ('uint', 32): 'I',
            ('uint', 64): 'Q',
            ('int', 8): 'b',
            ('int', 16): 'h',
            ('int', 32): 'i',
            ('int', 64): 'q',
            ('float', 16): 'e',
            ('float', 32): 'f',
            ('float', 64): 'd',
            ('complex', 64): 'F',
            ('complex', 128): 'D',
            ('uint', (5, 6, 5)): 'B',
        }

    def TIFF_PHOTOMETRICS():
        return {
            0: 'miniswhite',
            1: 'minisblack',
            2: 'rgb',
            3: 'palette',
            4: 'mask',
            5: 'separated',  # CMYK
            6: 'ycbcr',
            8: 'cielab',
            9: 'icclab',
            10: 'itulab',
            32803: 'cfa',  # Color Filter Array
            32844: 'logl',
            32845: 'logluv',
            34892: 'linear_raw'
        }

    def TIFF_COMPESSIONS():
        return {
            1: None,
            2: 'ccittrle',
            3: 'ccittfax3',
            4: 'ccittfax4',
            5: 'lzw',
            6: 'ojpeg',
            7: 'jpeg',
            8: 'adobe_deflate',
            9: 't85',
            10: 't43',
            32766: 'next',
            32771: 'ccittrlew',
            32773: 'packbits',
            32809: 'thunderscan',
            32895: 'it8ctpad',
            32896: 'it8lw',
            32897: 'it8mp',
            32898: 'it8bl',
            32908: 'pixarfilm',
            32909: 'pixarlog',
            32946: 'deflate',
            32947: 'dcs',
            33003: 'aperio_jp2000_ycbcr',
            33005: 'aperio_jp2000_rgb',
            34661: 'jbig',
            34676: 'sgilog',
            34677: 'sgilog24',
            34712: 'jp2000',
            34713: 'nef',
            34925: 'lzma',
        }

    def TIFF_DECOMPESSORS():
        decompressors = {
            None: lambda x: x,
            'adobe_deflate': zlib.decompress,
            'deflate': zlib.decompress,
            'packbits': decode_packbits,
            'lzw': decode_lzw,
            # 'jpeg': decode_jpeg
        }
        if lzma:
            decompressors['lzma'] = lzma.decompress
        return decompressors

    def TIFF_ORIENTATIONS():
        return {
            1: 'top_left',
            2: 'top_right',
            3: 'bottom_right',
            4: 'bottom_left',
            5: 'left_top',
            6: 'right_top',
            7: 'right_bottom',
            8: 'left_bottom',
        }

    class TIFF_SUBFILE_TYPES(object):
        def __getitem__(self, key):
            result = []
            if key & 1:
                result.append('reduced_image')
            if key & 2:
                result.append('page')
            if key & 4:
                result.append('mask')
            return tuple(result)

    class TIFF_GROUP3_OPTIONS(object):
        def __getitem__(self, key):
            result = []
            if key & 1:
                result.append('2dencoding')
            if key & 2:
                result.append('uncompressed')
            if key & 4:
                result.append('fillbits')
            return tuple(result)

    def TIFF_FRAME_TAGS():
        # Tags to be read from file by TiffFrame
        # return frozenset({324, 325, 270, 273, 279, 285, 286, 287, 297, 306})
        codes = CONST.TIFF_TAGS_NAMES
        s = set(codes[name] for name in TiffFrame.__slots__ if name in codes)
        s.update({273, 279, 324, 325})
        return frozenset(s)

    def TIFF_FRAME_ATTRS():
        # Attributes that a TiffFrame shares with keyframe
        return frozenset('shape ndim size dtype axes '
                         'is_indexed is_final'.split())

    def TIFF_PAGE_ATTRS():
        # TiffPage attributes
        return frozenset('reduced sgi tiled indexed contiguous '
                         'chroma_subsampled'.split())

    def TIFF_FILE_ATTRS():
        # TiffFile 'is_\*' attributes derived from first TiffPage
        return frozenset('shaped ome imagej stk lsm fluoview nih vista '
                         'micromanager metaseries mdgel mediacy tvips fei '
                         'sem scn svs scanimage andor epics pilatus'.split())

    def TIFF_FILE_EXTENSIONS():
        # TIFF file extensions
        return tuple('tif tiff ome.tif lsm stk '
                     'gel seq svs bif tf8 tf2 btf'.split())

    def TIFF_FILEOPEN_TYPES():
        # String for use in Windows File Open box
        return [("%s files" % ext.upper(), "*.%s" % ext)
                for ext in CONST.TIFF_FILE_EXTENSIONS] + [("allfiles", "*")]

    def AXES_LABELS():
        # TODO: is there a standard for character axes labels?
        axes = {
            'X': 'width',
            'Y': 'height',
            'Z': 'depth',
            'S': 'sample',  # rgb(a)
            'I': 'series',  # general sequence, plane, page, IFD
            'T': 'time',
            'C': 'channel',  # color, emission wavelength
            'A': 'angle',
            'P': 'phase',  # formerly F    # P is Position in LSM!
            'R': 'tile',  # region, point, mosaic
            'H': 'lifetime',  # histogram
            'E': 'lambda',  # excitation wavelength
            'L': 'exposure',  # lux
            'V': 'event',
            'Q': 'other',
            'M': 'mosaic',  # LSM 6
        }
        axes.update(dict((v, k) for k, v in axes.items()))
        return axes

    def ANDOR_TAGS():
        # Andor Technology tags #4864 - 5030
        # TODO: obtain specification for Andor tags
        return {
            4864: 'id',
            4869: 'temperature',
            4876: 'exposure_time',
            4878: 'kinetic_cycle_time',
            4879: 'accumulations',
            4881: 'acquisition_cycle_time',
            4882: 'readout_time',
            4884: 'photon_counting',
            4885: 'em_dac_level',
            4890: 'frames',
            4896: 'horizontal_flip',
            4897: 'vertical_flip',
            4898: 'clockwise',
            4899: 'counter_clockwise',
            4904: 'vertical_clock_voltage',
            4905: 'vertical_shift_speed',
            4907: 'pre_amp_setting',
            4908: 'camera_serial',
            4911: 'actual_temperature',
            4912: 'baseline_clamp',
            4913: 'prescans',
            4914: 'model',
            4915: 'chip_size_x',
            4916: 'chip_size_y',
            4944: 'baseline_offset',
            4966: 'software_version',
        }

    def EXIF_TAGS():
        return {
            33434: 'ExposureTime',
            33437: 'FNumber',
            34850: 'ExposureProgram',
            34852: 'SpectralSensitivity',
            34855: 'ISOSpeedRatings',
            34856: 'OECF',
            36864: 'ExifVersion',
            36867: 'DateTimeOriginal',
            36868: 'DateTimeDigitized',
            36880: 'OffsetTime',
            36881: 'OffsetTimeOriginal',
            36882: 'OffsetTimeDigitized',
            34868: 'ISOSpeedLatitudeyyy',
            34869: 'ISOSpeedLatitudezzz',
            37121: 'ComponentsConfiguration',
            37122: 'CompressedBitsPerPixel',
            37377: 'ShutterSpeedValue',
            37378: 'ApertureValue',
            37379: 'BrightnessValue',
            37380: 'ExposureBiasValue',
            37381: 'MaxApertureValue',
            37382: 'SubjectDistance',
            37383: 'MeteringMode',
            37384: 'LightSource',
            37385: 'Flash',
            37386: 'FocalLength',
            37396: 'SubjectArea',
            37500: 'MakerNote',
            37510: 'UserComment',
            37520: 'SubsecTime',
            37521: 'SubsecTimeOriginal',
            37522: 'SubsecTimeDigitized',
            37888: 'Temperature',
            37889: 'Humidity',
            37890: 'Pressure',
            37891: 'WaterDepth',
            37892: 'Acceleration',
            37893: 'CameraElevationAngle',
            40960: 'FlashpixVersion',
            40961: 'ColorSpace',
            40962: 'PixelXDimension',
            40963: 'PixelYDimension',
            40964: 'RelatedSoundFile',
            41483: 'FlashEnergy',
            41484: 'SpatialFrequencyResponse',
            41486: 'FocalPlaneXResolution',
            41487: 'FocalPlaneYResolution',
            41488: 'FocalPlaneResolutionUnit',
            41492: 'SubjectLocation',
            41493: 'ExposureIndex',
            41495: 'SensingMethod',
            41728: 'FileSource',
            41729: 'SceneType',
            41730: 'CFAPattern',
            41985: 'CustomRendered',
            41986: 'ExposureMode',
            41987: 'WhiteBalance',
            41988: 'DigitalZoomRatio',
            41989: 'FocalLengthIn35mmFilm',
            41990: 'SceneCaptureType',
            41991: 'GainControl',
            41992: 'Contrast',
            41993: 'Saturation',
            41994: 'Sharpness',
            41995: 'DeviceSettingDescription',
            41996: 'SubjectDistanceRange',
            42016: 'ImageUniqueID',
            42032: 'CameraOwnerName',
            42033: 'BodySerialNumber',
            42034: 'LensSpecification',
            42035: 'LensMake',
            42036: 'LensModel',
            42037: 'LensSerialNumber',
        }

    def GPS_TAGS():
        return {
            0: 'GPSVersionID',
            1: 'GPSLatitudeRef',
            2: 'GPSLatitude',
            3: 'GPSLongitudeRef',
            4: 'GPSLongitude',
            5: 'GPSAltitudeRef',
            6: 'GPSAltitude',
            7: 'GPSTimeStamp',
            8: 'GPSSatellites',
            9: 'GPSStatus',
            10: 'GPSMeasureMode',
            11: 'GPSDOP',
            12: 'GPSSpeedRef',
            13: 'GPSSpeed',
            14: 'GPSTrackRef',
            15: 'GPSTrack',
            16: 'GPSImgDirectionRef',
            17: 'GPSImgDirection',
            18: 'GPSMapDatum',
            19: 'GPSDestLatitudeRef',
            20: 'GPSDestLatitude',
            21: 'GPSDestLongitudeRef',
            22: 'GPSDestLongitude',
            23: 'GPSDestBearingRef',
            24: 'GPSDestBearing',
            25: 'GPSDestDistanceRef',
            26: 'GPSDestDistance',
            27: 'GPSProcessingMethod',
            28: 'GPSAreaInformation',
            29: 'GPSDateStamp',
            30: 'GPSDifferential',
            31: 'GPSHPositioningError',
        }

    def LSM_INFO():
        return [
            ('magic_number', 'u4'),
            ('structure_size', 'i4'),
            ('dimension_x', 'i4'),
            ('dimension_y', 'i4'),
            ('dimension_z', 'i4'),
            ('dimension_channels', 'i4'),
            ('dimension_time', 'i4'),
            ('data_type', 'i4'),  # LSM_DATA_TYPES
            ('thumbnail_x', 'i4'),
            ('thumbnail_y', 'i4'),
            ('voxel_size_x', 'f8'),
            ('voxel_size_y', 'f8'),
            ('voxel_size_z', 'f8'),
            ('origin_x', 'f8'),
            ('origin_y', 'f8'),
            ('origin_z', 'f8'),
            ('scan_type', 'u2'),
            ('spectral_scan', 'u2'),
            ('type_of_data', 'u4'),  # LSM_TYPE_OF_DATA
            ('offset_vector_overlay', 'u4'),
            ('offset_input_lut', 'u4'),
            ('offset_output_lut', 'u4'),
            ('offset_channel_colors', 'u4'),
            ('time_interval', 'f8'),
            ('offset_channel_data_types', 'u4'),
            ('offset_scan_info', 'u4'),  # LSM_SCAN_INFO
            ('offset_ks_data', 'u4'),
            ('offset_time_stamps', 'u4'),
            ('offset_event_list', 'u4'),
            ('offset_roi', 'u4'),
            ('offset_bleach_roi', 'u4'),
            ('offset_next_recording', 'u4'),
            # LSM 2.0 ends here
            ('display_aspect_x', 'f8'),
            ('display_aspect_y', 'f8'),
            ('display_aspect_z', 'f8'),
            ('display_aspect_time', 'f8'),
            ('offset_mean_of_roi_overlay', 'u4'),
            ('offset_topo_isoline_overlay', 'u4'),
            ('offset_topo_profile_overlay', 'u4'),
            ('offset_linescan_overlay', 'u4'),
            ('offset_toolbar_flags', 'u4'),
            ('offset_channel_wavelength', 'u4'),
            ('offset_channel_factors', 'u4'),
            ('objective_sphere_correction', 'f8'),
            ('offset_unmix_parameters', 'u4'),
            # LSM 3.2, 4.0 end here
            ('offset_acquisition_parameters', 'u4'),
            ('offset_characteristics', 'u4'),
            ('offset_palette', 'u4'),
            ('time_difference_x', 'f8'),
            ('time_difference_y', 'f8'),
            ('time_difference_z', 'f8'),
            ('internal_use_1', 'u4'),
            ('dimension_p', 'i4'),
            ('dimension_m', 'i4'),
            ('dimensions_reserved', '16i4'),
            ('offset_tile_positions', 'u4'),
            ('reserved_1', '9u4'),
            ('offset_positions', 'u4'),
            ('reserved_2', '21u4'),  # must be 0
        ]

    def LSM_INFO_READERS():
        # Import functions for LSM_INFO sub-records
        # TODO: read more LSM_INFO sub-records
        return {
            'scan_info': read_lsm_scan_info,
            'time_stamps': read_lsm_time_stamps,
            'event_list': read_lsm_event_list,
            'channel_colors': read_lsm_floatpairs,
            'positions': read_lsm_floatpairs,
            'tile_positions': read_lsm_floatpairs,
        }

    def LSM_SCAN_TYPES():
        # Map lsm_info.scan_type to dimension order
        return {
            0: 'XYZCT',  # x-y-z scan
            1: 'XYZCT',  # z scan (x-z plane)
            2: 'XYZCT',  # line scan
            3: 'XYTCZ',  # time series x-y
            4: 'XYZTC',  # time series x-z
            5: 'XYTCZ',  # time series 'Mean of ROIs'
            6: 'XYZTC',  # time series x-y-z
            7: 'XYCTZ',  # spline scan
            8: 'XYCZT',  # spline scan x-z
            9: 'XYTCZ',  # time series spline plane x-z
            10: 'XYZCT',  # point mode
        }

    def LSM_DIMENSIONS():
        # Map dimension codes to lsm_info attribute
        return {
            'X': 'dimension_x',
            'Y': 'dimension_y',
            'Z': 'dimension_z',
            'C': 'dimension_channels',
            'T': 'dimension_time',
            'P': 'dimension_p',
            'M': 'dimension_m',
        }

    def LSM_DATA_TYPES():
        # Description of lsm_info.data_type
        return {
            0: 'varying data types',
            1: '8 bit unsigned integer',
            2: '12 bit unsigned integer',
            5: '32 bit float',
        }

    def LSM_TYPE_OF_DATA():
        # Description of lsm_info.type_of_data
        return {
            0: 'Original scan data',
            1: 'Calculated data',
            2: '3D reconstruction',
            3: 'Topography height map',
        }

    def LSM_SCAN_INFO_ARRAYS():
        return {
            0x20000000: "tracks",
            0x30000000: "lasers",
            0x60000000: "detection_channels",
            0x80000000: "illumination_channels",
            0xa0000000: "beam_splitters",
            0xc0000000: "data_channels",
            0x11000000: "timers",
            0x13000000: "markers",
        }

    def LSM_SCAN_INFO_STRUCTS():
        return {
            # 0x10000000: "recording",
            0x40000000: "track",
            0x50000000: "laser",
            0x70000000: "detection_channel",
            0x90000000: "illumination_channel",
            0xb0000000: "beam_splitter",
            0xd0000000: "data_channel",
            0x12000000: "timer",
            0x14000000: "marker",
        }

    def LSM_SCAN_INFO_ATTRIBUTES():
        return {
            # recording
            0x10000001: "name",
            0x10000002: "description",
            0x10000003: "notes",
            0x10000004: "objective",
            0x10000005: "processing_summary",
            0x10000006: "special_scan_mode",
            0x10000007: "scan_type",
            0x10000008: "scan_mode",
            0x10000009: "number_of_stacks",
            0x1000000a: "lines_per_plane",
            0x1000000b: "samples_per_line",
            0x1000000c: "planes_per_volume",
            0x1000000d: "images_width",
            0x1000000e: "images_height",
            0x1000000f: "images_number_planes",
            0x10000010: "images_number_stacks",
            0x10000011: "images_number_channels",
            0x10000012: "linscan_xy_size",
            0x10000013: "scan_direction",
            0x10000014: "time_series",
            0x10000015: "original_scan_data",
            0x10000016: "zoom_x",
            0x10000017: "zoom_y",
            0x10000018: "zoom_z",
            0x10000019: "sample_0x",
            0x1000001a: "sample_0y",
            0x1000001b: "sample_0z",
            0x1000001c: "sample_spacing",
            0x1000001d: "line_spacing",
            0x1000001e: "plane_spacing",
            0x1000001f: "plane_width",
            0x10000020: "plane_height",
            0x10000021: "volume_depth",
            0x10000023: "nutation",
            0x10000034: "rotation",
            0x10000035: "precession",
            0x10000036: "sample_0time",
            0x10000037: "start_scan_trigger_in",
            0x10000038: "start_scan_trigger_out",
            0x10000039: "start_scan_event",
            0x10000040: "start_scan_time",
            0x10000041: "stop_scan_trigger_in",
            0x10000042: "stop_scan_trigger_out",
            0x10000043: "stop_scan_event",
            0x10000044: "stop_scan_time",
            0x10000045: "use_rois",
            0x10000046: "use_reduced_memory_rois",
            0x10000047: "user",
            0x10000048: "use_bc_correction",
            0x10000049: "position_bc_correction1",
            0x10000050: "position_bc_correction2",
            0x10000051: "interpolation_y",
            0x10000052: "camera_binning",
            0x10000053: "camera_supersampling",
            0x10000054: "camera_frame_width",
            0x10000055: "camera_frame_height",
            0x10000056: "camera_offset_x",
            0x10000057: "camera_offset_y",
            0x10000059: "rt_binning",
            0x1000005a: "rt_frame_width",
            0x1000005b: "rt_frame_height",
            0x1000005c: "rt_region_width",
            0x1000005d: "rt_region_height",
            0x1000005e: "rt_offset_x",
            0x1000005f: "rt_offset_y",
            0x10000060: "rt_zoom",
            0x10000061: "rt_line_period",
            0x10000062: "prescan",
            0x10000063: "scan_direction_z",
            # track
            0x40000001: "multiplex_type",  # 0 after line; 1 after frame
            0x40000002: "multiplex_order",
            0x40000003: "sampling_mode",  # 0 sample; 1 line avg; 2 frame avg
            0x40000004: "sampling_method",  # 1 mean; 2 sum
            0x40000005: "sampling_number",
            0x40000006: "acquire",
            0x40000007: "sample_observation_time",
            0x4000000b: "time_between_stacks",
            0x4000000c: "name",
            0x4000000d: "collimator1_name",
            0x4000000e: "collimator1_position",
            0x4000000f: "collimator2_name",
            0x40000010: "collimator2_position",
            0x40000011: "is_bleach_track",
            0x40000012: "is_bleach_after_scan_number",
            0x40000013: "bleach_scan_number",
            0x40000014: "trigger_in",
            0x40000015: "trigger_out",
            0x40000016: "is_ratio_track",
            0x40000017: "bleach_count",
            0x40000018: "spi_center_wavelength",
            0x40000019: "pixel_time",
            0x40000021: "condensor_frontlens",
            0x40000023: "field_stop_value",
            0x40000024: "id_condensor_aperture",
            0x40000025: "condensor_aperture",
            0x40000026: "id_condensor_revolver",
            0x40000027: "condensor_filter",
            0x40000028: "id_transmission_filter1",
            0x40000029: "id_transmission1",
            0x40000030: "id_transmission_filter2",
            0x40000031: "id_transmission2",
            0x40000032: "repeat_bleach",
            0x40000033: "enable_spot_bleach_pos",
            0x40000034: "spot_bleach_posx",
            0x40000035: "spot_bleach_posy",
            0x40000036: "spot_bleach_posz",
            0x40000037: "id_tubelens",
            0x40000038: "id_tubelens_position",
            0x40000039: "transmitted_light",
            0x4000003a: "reflected_light",
            0x4000003b: "simultan_grab_and_bleach",
            0x4000003c: "bleach_pixel_time",
            # laser
            0x50000001: "name",
            0x50000002: "acquire",
            0x50000003: "power",
            # detection_channel
            0x70000001: "integration_mode",
            0x70000002: "special_mode",
            0x70000003: "detector_gain_first",
            0x70000004: "detector_gain_last",
            0x70000005: "amplifier_gain_first",
            0x70000006: "amplifier_gain_last",
            0x70000007: "amplifier_offs_first",
            0x70000008: "amplifier_offs_last",
            0x70000009: "pinhole_diameter",
            0x7000000a: "counting_trigger",
            0x7000000b: "acquire",
            0x7000000c: "point_detector_name",
            0x7000000d: "amplifier_name",
            0x7000000e: "pinhole_name",
            0x7000000f: "filter_set_name",
            0x70000010: "filter_name",
            0x70000013: "integrator_name",
            0x70000014: "channel_name",
            0x70000015: "detector_gain_bc1",
            0x70000016: "detector_gain_bc2",
            0x70000017: "amplifier_gain_bc1",
            0x70000018: "amplifier_gain_bc2",
            0x70000019: "amplifier_offset_bc1",
            0x70000020: "amplifier_offset_bc2",
            0x70000021: "spectral_scan_channels",
            0x70000022: "spi_wavelength_start",
            0x70000023: "spi_wavelength_stop",
            0x70000026: "dye_name",
            0x70000027: "dye_folder",
            # illumination_channel
            0x90000001: "name",
            0x90000002: "power",
            0x90000003: "wavelength",
            0x90000004: "aquire",
            0x90000005: "detchannel_name",
            0x90000006: "power_bc1",
            0x90000007: "power_bc2",
            # beam_splitter
            0xb0000001: "filter_set",
            0xb0000002: "filter",
            0xb0000003: "name",
            # data_channel
            0xd0000001: "name",
            0xd0000003: "acquire",
            0xd0000004: "color",
            0xd0000005: "sample_type",
            0xd0000006: "bits_per_sample",
            0xd0000007: "ratio_type",
            0xd0000008: "ratio_track1",
            0xd0000009: "ratio_track2",
            0xd000000a: "ratio_channel1",
            0xd000000b: "ratio_channel2",
            0xd000000c: "ratio_const1",
            0xd000000d: "ratio_const2",
            0xd000000e: "ratio_const3",
            0xd000000f: "ratio_const4",
            0xd0000010: "ratio_const5",
            0xd0000011: "ratio_const6",
            0xd0000012: "ratio_first_images1",
            0xd0000013: "ratio_first_images2",
            0xd0000014: "dye_name",
            0xd0000015: "dye_folder",
            0xd0000016: "spectrum",
            0xd0000017: "acquire",
            # timer
            0x12000001: "name",
            0x12000002: "description",
            0x12000003: "interval",
            0x12000004: "trigger_in",
            0x12000005: "trigger_out",
            0x12000006: "activation_time",
            0x12000007: "activation_number",
            # marker
            0x14000001: "name",
            0x14000002: "description",
            0x14000003: "trigger_in",
            0x14000004: "trigger_out",
        }

    def NIH_IMAGE_HEADER():
        return [
            ('fileid', 'a8'),
            ('nlines', 'i2'),
            ('pixelsperline', 'i2'),
            ('version', 'i2'),
            ('oldlutmode', 'i2'),
            ('oldncolors', 'i2'),
            ('colors', 'u1', (3, 32)),
            ('oldcolorstart', 'i2'),
            ('colorwidth', 'i2'),
            ('extracolors', 'u2', (6, 3)),
            ('nextracolors', 'i2'),
            ('foregroundindex', 'i2'),
            ('backgroundindex', 'i2'),
            ('xscale', 'f8'),
            ('_x0', 'i2'),
            ('_x1', 'i2'),
            ('units_t', 'i2'),  # NIH_UNITS_TYPE
            ('p1', [('x', 'i2'), ('y', 'i2')]),
            ('p2', [('x', 'i2'), ('y', 'i2')]),
            ('curvefit_t', 'i2'),  # NIH_CURVEFIT_TYPE
            ('ncoefficients', 'i2'),
            ('coeff', 'f8', 6),
            ('_um_len', 'u1'),
            ('um', 'a15'),
            ('_x2', 'u1'),
            ('binarypic', 'b1'),
            ('slicestart', 'i2'),
            ('sliceend', 'i2'),
            ('scalemagnification', 'f4'),
            ('nslices', 'i2'),
            ('slicespacing', 'f4'),
            ('currentslice', 'i2'),
            ('frameinterval', 'f4'),
            ('pixelaspectratio', 'f4'),
            ('colorstart', 'i2'),
            ('colorend', 'i2'),
            ('ncolors', 'i2'),
            ('fill1', '3u2'),
            ('fill2', '3u2'),
            ('colortable_t', 'u1'),  # NIH_COLORTABLE_TYPE
            ('lutmode_t', 'u1'),  # NIH_LUTMODE_TYPE
            ('invertedtable', 'b1'),
            ('zeroclip', 'b1'),
            ('_xunit_len', 'u1'),
            ('xunit', 'a11'),
            ('stacktype_t', 'i2'),  # NIH_STACKTYPE_TYPE
        ]

    def NIH_COLORTABLE_TYPE():
        return ('CustomTable', 'AppleDefault', 'Pseudo20', 'Pseudo32',
                'Rainbow', 'Fire1', 'Fire2', 'Ice', 'Grays', 'Spectrum')

    def NIH_LUTMODE_TYPE():
        return ('PseudoColor', 'OldAppleDefault', 'OldSpectrum', 'GrayScale',
                'ColorLut', 'CustomGrayscale')

    def NIH_CURVEFIT_TYPE():
        return ('StraightLine', 'Poly2', 'Poly3', 'Poly4', 'Poly5', 'ExpoFit',
                'PowerFit', 'LogFit', 'RodbardFit', 'SpareFit1',
                'Uncalibrated', 'UncalibratedOD')

    def NIH_UNITS_TYPE():
        return ('Nanometers', 'Micrometers', 'Millimeters', 'Centimeters',
                'Meters', 'Kilometers', 'Inches', 'Feet', 'Miles', 'Pixels',
                'OtherUnits')

    def NIH_STACKTYPE_TYPE():
        return ('VolumeStack', 'RGBStack', 'MovieStack', 'HSVStack')

    def TVIPS_HEADER_V1():
        # TVIPS metadata from EMMENU Help file
        return [
            ('version', 'i4'),
            ('comment_v1', 'a80'),
            ('high_tension', 'i4'),
            ('spherical_aberration', 'i4'),
            ('illumination_aperture', 'i4'),
            ('magnification', 'i4'),
            ('post-magnification', 'i4'),
            ('focal_length', 'i4'),
            ('defocus', 'i4'),
            ('astigmatism', 'i4'),
            ('astigmatism_direction', 'i4'),
            ('biprism_voltage', 'i4'),
            ('specimen_tilt_angle', 'i4'),
            ('specimen_tilt_direction', 'i4'),
            ('illumination_tilt_direction', 'i4'),
            ('illumination_tilt_angle', 'i4'),
            ('image_mode', 'i4'),
            ('energy_spread', 'i4'),
            ('chromatic_aberration', 'i4'),
            ('shutter_type', 'i4'),
            ('defocus_spread', 'i4'),
            ('ccd_number', 'i4'),
            ('ccd_size', 'i4'),
            ('offset_x_v1', 'i4'),
            ('offset_y_v1', 'i4'),
            ('physical_pixel_size', 'i4'),
            ('binning', 'i4'),
            ('readout_speed', 'i4'),
            ('gain_v1', 'i4'),
            ('sensitivity_v1', 'i4'),
            ('exposure_time_v1', 'i4'),
            ('flat_corrected', 'i4'),
            ('dead_px_corrected', 'i4'),
            ('image_mean', 'i4'),
            ('image_std', 'i4'),
            ('displacement_x', 'i4'),
            ('displacement_y', 'i4'),
            ('date_v1', 'i4'),
            ('time_v1', 'i4'),
            ('image_min', 'i4'),
            ('image_max', 'i4'),
            ('image_statistics_quality', 'i4'),
        ]

    def TVIPS_HEADER_V2():
        return [
            ('image_name', 'V160'),  # utf16
            ('image_folder', 'V160'),
            ('image_size_x', 'i4'),
            ('image_size_y', 'i4'),
            ('image_size_z', 'i4'),
            ('image_size_e', 'i4'),
            ('image_data_type', 'i4'),
            ('date', 'i4'),
            ('time', 'i4'),
            ('comment', 'V1024'),
            ('image_history', 'V1024'),
            ('scaling', '16f4'),
            ('image_statistics', '16c16'),
            ('image_type', 'i4'),
            ('image_display_type', 'i4'),
            ('pixel_size_x', 'f4'),  # distance between two px in x, [nm]
            ('pixel_size_y', 'f4'),  # distance between two px in y, [nm]
            ('image_distance_z', 'f4'),
            ('image_distance_e', 'f4'),
            ('image_misc', '32f4'),
            ('tem_type', 'V160'),
            ('tem_high_tension', 'f4'),
            ('tem_aberrations', '32f4'),
            ('tem_energy', '32f4'),
            ('tem_mode', 'i4'),
            ('tem_magnification', 'f4'),
            ('tem_magnification_correction', 'f4'),
            ('post_magnification', 'f4'),
            ('tem_stage_type', 'i4'),
            ('tem_stage_position', '5f4'),  # x, y, z, a, b
            ('tem_image_shift', '2f4'),
            ('tem_beam_shift', '2f4'),
            ('tem_beam_tilt', '2f4'),
            ('tiling_parameters', '7f4'),  # 0: tiling? 1:x 2:y 3: max x
                                           # 4: max y 5: overlap x 6: overlap y
            ('tem_illumination', '3f4'),  # 0: spotsize 1: intensity
            ('tem_shutter', 'i4'),
            ('tem_misc', '32f4'),
            ('camera_type', 'V160'),
            ('physical_pixel_size_x', 'f4'),
            ('physical_pixel_size_y', 'f4'),
            ('offset_x', 'i4'),
            ('offset_y', 'i4'),
            ('binning_x', 'i4'),
            ('binning_y', 'i4'),
            ('exposure_time', 'f4'),
            ('gain', 'f4'),
            ('readout_rate', 'f4'),
            ('flatfield_description', 'V160'),
            ('sensitivity', 'f4'),
            ('dose', 'f4'),
            ('cam_misc', '32f4'),
            ('fei_microscope_information', 'V1024'),
            ('fei_specimen_information', 'V1024'),
            ('magic', 'u4'),
        ]

    def FLUOVIEW_MM_HEADER():
        # Olympus FluoView MM header
        MM_DIMENSION = [
            ('name', 'a16'),
            ('size', 'i4'),
            ('origin', 'f8'),
            ('resolution', 'f8'),
            ('unit', 'a64')]
        return [
            ('header_flag', 'i2'),
            ('image_type', 'u1'),
            ('image_name', 'a257'),
            ('offset_data', 'u4'),
            ('palette_size', 'i4'),
            ('offset_palette0', 'u4'),
            ('offset_palette1', 'u4'),
            ('comment_size', 'i4'),
            ('offset_comment', 'u4'),
            ('dimensions', MM_DIMENSION, 10),
            ('offset_position', 'u4'),
            ('map_type', 'i2'),
            ('map_min', 'f8'),
            ('map_max', 'f8'),
            ('min_value', 'f8'),
            ('max_value', 'f8'),
            ('offset_map', 'u4'),
            ('gamma', 'f8'),
            ('offset', 'f8'),
            ('gray_channel', MM_DIMENSION),
            ('offset_thumbnail', 'u4'),
            ('voice_field', 'i4'),
            ('offset_voice_field', 'u4'),
        ]

    def FLUOVIEW_DIMENSIONS():
        # Map fluoview_mm_header.dimensions to axes characters
        return {
            b'X': 'X',
            b'Y': 'Y',
            b'Z': 'Z',
            b'T': 'T',
            b'CH': 'C',
            b'WAVELENGTH': 'C',
            b'TIME': 'T',
            b'XY': 'R',
            b'EVENT': 'V',
            b'EXPOSURE': 'L',
        }

    def UIC_TAGS():
        # Map Universal Imaging Corporation MetaMorph internal tag ids to
        # name and type
        from fractions import Fraction

        return [
            ('auto_scale', int),
            ('min_scale', int),
            ('max_scale', int),
            ('spatial_calibration', int),
            ('x_calibration', Fraction),
            ('y_calibration', Fraction),
            ('calibration_units', str),
            ('name', str),
            ('thresh_state', int),
            ('thresh_state_red', int),
            ('tagid_10', None),  # undefined
            ('thresh_state_green', int),
            ('thresh_state_blue', int),
            ('thresh_state_lo', int),
            ('thresh_state_hi', int),
            ('zoom', int),
            ('create_time', julian_datetime),
            ('last_saved_time', julian_datetime),
            ('current_buffer', int),
            ('gray_fit', None),
            ('gray_point_count', None),
            ('gray_x', Fraction),
            ('gray_y', Fraction),
            ('gray_min', Fraction),
            ('gray_max', Fraction),
            ('gray_unit_name', str),
            ('standard_lut', int),
            ('wavelength', int),
            ('stage_position', '(%i,2,2)u4'),  # N xy positions as fract
            ('camera_chip_offset', '(%i,2,2)u4'),  # N xy offsets as fract
            ('overlay_mask', None),
            ('overlay_compress', None),
            ('overlay', None),
            ('special_overlay_mask', None),
            ('special_overlay_compress', None),
            ('special_overlay', None),
            ('image_property', read_uic_image_property),
            ('stage_label', '%ip'),  # N str
            ('autoscale_lo_info', Fraction),
            ('autoscale_hi_info', Fraction),
            ('absolute_z', '(%i,2)u4'),  # N fractions
            ('absolute_z_valid', '(%i,)u4'),  # N long
            ('gamma', 'I'),  # 'I' uses offset
            ('gamma_red', 'I'),
            ('gamma_green', 'I'),
            ('gamma_blue', 'I'),
            ('camera_bin', '2I'),
            ('new_lut', int),
            ('image_property_ex', None),
            ('plane_property', int),
            ('user_lut_table', '(256,3)u1'),
            ('red_autoscale_info', int),
            ('red_autoscale_lo_info', Fraction),
            ('red_autoscale_hi_info', Fraction),
            ('red_minscale_info', int),
            ('red_maxscale_info', int),
            ('green_autoscale_info', int),
            ('green_autoscale_lo_info', Fraction),
            ('green_autoscale_hi_info', Fraction),
            ('green_minscale_info', int),
            ('green_maxscale_info', int),
            ('blue_autoscale_info', int),
            ('blue_autoscale_lo_info', Fraction),
            ('blue_autoscale_hi_info', Fraction),
            ('blue_min_scale_info', int),
            ('blue_max_scale_info', int),
            # ('overlay_plane_color', read_uic_overlay_plane_color),
        ]

    def PILATUS_HEADER():
        # PILATUS CBF Header Specification, Version 1.4
        # Map key to [value_indices], type
        return {
            'Detector': ([slice(1, None)], str),
            'Pixel_size': ([1, 4], float),
            'Silicon': ([3], float),
            'Exposure_time': ([1], float),
            'Exposure_period': ([1], float),
            'Tau': ([1], float),
            'Count_cutoff': ([1], int),
            'Threshold_setting': ([1], float),
            'Gain_setting': ([1, 2], str),
            'N_excluded_pixels': ([1], int),
            'Excluded_pixels': ([1], str),
            'Flat_field': ([1], str),
            'Trim_file': ([1], str),
            'Image_path': ([1], str),
            # optional
            'Wavelength': ([1], float),
            'Energy_range': ([1, 2], float),
            'Detector_distance': ([1], float),
            'Detector_Voffset': ([1], float),
            'Beam_xy': ([1, 2], float),
            'Flux': ([1], str),
            'Filter_transmission': ([1], float),
            'Start_angle': ([1], float),
            'Angle_increment': ([1], float),
            'Detector_2theta': ([1], float),
            'Polarization': ([1], float),
            'Alpha': ([1], float),
            'Kappa': ([1], float),
            'Phi': ([1], float),
            'Phi_increment': ([1], float),
            'Chi': ([1], float),
            'Chi_increment': ([1], float),
            'Oscillation_axis': ([slice(1, None)], str),
            'N_oscillations': ([1], int),
            'Start_position': ([1], float),
            'Position_increment': ([1], float),
            'Shutter_time': ([1], float),
            'Omega': ([1], float),
            'Omega_increment': ([1], float)
        }

    def REVERSE_BITORDER_BYTES():
        # Bytes with reversed bitorder
        return (
            b'\x00\x80@\xc0 \xa0`\xe0\x10\x90P\xd00\xb0p\xf0\x08\x88H\xc8('
            b'\xa8h\xe8\x18\x98X\xd88\xb8x\xf8\x04\x84D\xc4$\xa4d\xe4\x14'
            b'\x94T\xd44\xb4t\xf4\x0c\x8cL\xcc,\xacl\xec\x1c\x9c\\\xdc<\xbc|'
            b'\xfc\x02\x82B\xc2"\xa2b\xe2\x12\x92R\xd22\xb2r\xf2\n\x8aJ\xca*'
            b'\xaaj\xea\x1a\x9aZ\xda:\xbaz\xfa\x06\x86F\xc6&\xa6f\xe6\x16'
            b'\x96V\xd66\xb6v\xf6\x0e\x8eN\xce.\xaen\xee\x1e\x9e^\xde>\xbe~'
            b'\xfe\x01\x81A\xc1!\xa1a\xe1\x11\x91Q\xd11\xb1q\xf1\t\x89I\xc9)'
            b'\xa9i\xe9\x19\x99Y\xd99\xb9y\xf9\x05\x85E\xc5%\xa5e\xe5\x15'
            b'\x95U\xd55\xb5u\xf5\r\x8dM\xcd-\xadm\xed\x1d\x9d]\xdd=\xbd}'
            b'\xfd\x03\x83C\xc3#\xa3c\xe3\x13\x93S\xd33\xb3s\xf3\x0b\x8bK'
            b'\xcb+\xabk\xeb\x1b\x9b[\xdb;\xbb{\xfb\x07\x87G\xc7\'\xa7g\xe7'
            b'\x17\x97W\xd77\xb7w\xf7\x0f\x8fO\xcf/\xafo\xef\x1f\x9f_'
            b'\xdf?\xbf\x7f\xff')

    def REVERSE_BITORDER_ARRAY():
        # Numpy array of bytes with reversed bitorder
        return numpy.fromstring(CONST.REVERSE_BITORDER_BYTES, dtype='uint8')

    def ALLOCATIONGRANULARITY():
        # alignment for writing contiguous data to TIFF
        import mmap  # delayed import
        return mmap.ALLOCATIONGRANULARITY

    # Max line length of printed output
    PRINT_LINE_WIDTH = 100

    # Max number of lines to print
    PRINT_MAX_LINES = 512


def read_tags(fh, byteorder, offset_size, tag_names, custom_tags=None):
    """Read tags from chain of IFDs and return as list of dicts.

    The file handle position must be at a valid IFD header.

    """
    if offset_size == 4:
        offset_format = byteorder+'I'
        tagno_size = 2
        tagno_format = byteorder+'H'
        tag_size = 12
        tag_format1 = byteorder+'HH'
        tag_format2 = byteorder+'I4s'
    elif offset_size == 8:
        offset_format = byteorder+'Q'
        tagno_size = 8
        tagno_format = byteorder+'Q'
        tag_size = 20
        tag_format1 = byteorder+'HH'
        tag_format2 = byteorder+'Q8s'
    else:
        raise ValueError("invalid offset size")

    if custom_tags is None:
        custom_tags = {}

    result = []
    unpack = struct.unpack
    offset = fh.tell()
    while True:
        # loop over IFDs
        try:
            tagno = unpack(tagno_format, fh.read(tagno_size))[0]
            if tagno > 4096:
                raise ValueError("suspicious number of tags")
        except Exception:
            warnings.warn("corrupted tag list at offset %i" % offset)
            break

        tags = {}
        for _ in range(tagno):
            # read tags
            data = fh.read(tag_size)
            code, _type = unpack(tag_format1, data[:4])
            count, value = unpack(tag_format2, data[4:])
            name = tag_names.get(code, str(code))
            try:
                dtype = CONST.TIFF_DATA_TYPES[_type]
            except KeyError:
                raise TiffTag.Error("unknown tag data type %i" % _type)

            fmt = '%s%i%s' % (byteorder, count * int(dtype[0]), dtype[1])
            size = struct.calcsize(fmt)
            if size > offset_size or code in custom_tags:
                pos = fh.tell()
                offset = unpack(offset_format, value)[0]
                if offset < 8 or offset > fh.size - size:
                    raise TiffTag.Error("invalid tag value offset")
                fh.seek(offset)
                if code in custom_tags:
                    readfunc = custom_tags[code][1]
                    value = readfunc(fh, byteorder, dtype, count, offset_size)
                elif code in tag_names or dtype[-1] == 's':
                    value = unpack(fmt, fh.read(size))
                else:
                    value = read_numpy(fh, byteorder, dtype, count,
                                       offset_size)
                fh.seek(pos)
            else:
                value = unpack(fmt, value[:size])

            if code not in custom_tags and code not in CONST.TIFF_TAGS_TUPLE:
                if len(value) == 1:
                    value = value[0]
            if _type != 7 and dtype[-1] == 's' and isinstance(value, bytes):
                # TIFF ASCII fields can contain multiple strings,
                #   each terminated with a NUL
                value = stripascii(value)

            tags[name] = value

        result.append(tags)
        # read offset to next page
        offset = unpack(offset_format, fh.read(offset_size))[0]
        if offset == 0:
            break
        if offset >= fh.size:
            warnings.warn("invalid page offset (%i)" % offset)
            break
        fh.seek(offset)

    return result


def read_exif_ifd(fh, byteorder, dtype, count, offset_size):
    """Read EXIF tags from file and return as dict."""
    return read_tags(fh, byteorder, offset_size, CONST.EXIF_TAGS)


def read_gps_ifd(fh, byteorder, dtype, count, offset_size):
    """Read GPS tags from file and return as dict."""
    return read_tags(fh, byteorder, offset_size, CONST.GPS_TAGS)


def read_interoperability_ifd(fh, byteorder, dtype, count, offset_size):
    """Read Interoperability tags from file and return as dict."""
    tag_names = {1: 'InteroperabilityIndex'}
    return read_tags(fh, byteorder, offset_size, tag_names)


def read_bytes(fh, byteorder, dtype, count, offset_size):
    """Read tag data from file and return as byte string."""
    dtype = 'b' if dtype[-1] == 's' else byteorder+dtype[-1]
    return fh.read_array(dtype, count).tostring()


def read_numpy(fh, byteorder, dtype, count, offset_size):
    """Read tag data from file and return as numpy array."""
    dtype = 'b' if dtype[-1] == 's' else byteorder+dtype[-1]
    return fh.read_array(dtype, count)


def read_json(fh, byteorder, dtype, count, offset_size):
    """Read JSON tag data from file and return as object."""
    data = fh.read(count)
    try:
        return json.loads(unicode(stripnull(data), 'utf-8'))
    except ValueError:
        warnings.warn("invalid JSON '%s'" % data)


def read_mm_header(fh, byteorder, dtype, count, offset_size):
    """Read mm_header tag from file and return as numpy.rec.array."""
    return fh.read_record(CONST.FLUOVIEW_MM_HEADER, byteorder=byteorder)


def read_mm_stamp(fh, byteorder, dtype, count, offset_size):
    """Read MM_STAMP tag from file and return as numpy.ndarray."""
    return fh.read_array(byteorder+'f8', 8)


def read_uic1tag(fh, byteorder, dtype, count, offset_size, plane_count=None):
    """Read MetaMorph STK UIC1Tag from file and return as dict.

    Return empty dictionary if plane_count is unknown.

    """
    assert dtype in ('2I', '1I') and byteorder == '<'
    result = {}
    if dtype == '2I':
        # pre MetaMorph 2.5 (not tested)
        values = fh.read_array('<u4', 2*count).reshape(count, 2)
        result = {'z_distance': values[:, 0] / values[:, 1]}
    elif plane_count:
        for _ in range(count):
            tagid = struct.unpack('<I', fh.read(4))[0]
            if tagid in (28, 29, 37, 40, 41):
                # silently skip unexpected tags
                fh.read(4)
                continue
            name, value = read_uic_tag(fh, tagid, plane_count, offset=True)
            result[name] = value
    return result


def read_uic2tag(fh, byteorder, dtype, plane_count, offset_size):
    """Read MetaMorph STK UIC2Tag from file and return as dict."""
    assert dtype == '2I' and byteorder == '<'
    values = fh.read_array('<u4', 6*plane_count).reshape(plane_count, 6)
    return {
        'z_distance': values[:, 0] / values[:, 1],
        'date_created': values[:, 2],  # julian days
        'time_created': values[:, 3],  # milliseconds
        'date_modified': values[:, 4],  # julian days
        'time_modified': values[:, 5]}  # milliseconds


def read_uic3tag(fh, byteorder, dtype, plane_count, offset_size):
    """Read MetaMorph STK UIC3Tag from file and return as dict."""
    assert dtype == '2I' and byteorder == '<'
    values = fh.read_array('<u4', 2*plane_count).reshape(plane_count, 2)
    return {'wavelengths': values[:, 0] / values[:, 1]}


def read_uic4tag(fh, byteorder, dtype, plane_count, offset_size):
    """Read MetaMorph STK UIC4Tag from file and return as dict."""
    assert dtype == '1I' and byteorder == '<'
    result = {}
    while True:
        tagid = struct.unpack('<H', fh.read(2))[0]
        if tagid == 0:
            break
        name, value = read_uic_tag(fh, tagid, plane_count, offset=False)
        result[name] = value
    return result


def read_uic_tag(fh, tagid, plane_count, offset):
    """Read a single UIC tag value from file and return tag name and value.

    UIC1Tags use an offset.

    """
    def read_int(count=1):
        value = struct.unpack('<%iI' % count, fh.read(4*count))
        return value[0] if count == 1 else value

    try:
        name, dtype = CONST.UIC_TAGS[tagid]
    except IndexError:
        # unknown tag
        return '_tagid_%i' % tagid, read_int()

    Fraction = CONST.UIC_TAGS[4][1]

    if offset:
        pos = fh.tell()
        if dtype not in (int, None):
            off = read_int()
            if off < 8:
                if dtype is str:
                    return name, ''
                warnings.warn("invalid offset for uic tag '%s': %i" %
                              (name, off))
                return name, off
            fh.seek(off)

    if dtype is None:
        # skip
        name = '_' + name
        value = read_int()
    elif dtype is int:
        # int
        value = read_int()
    elif dtype is Fraction:
        # fraction
        value = read_int(2)
        value = value[0] / value[1]
    elif dtype is julian_datetime:
        # datetime
        value = julian_datetime(*read_int(2))
    elif dtype is read_uic_image_property:
        # ImagePropertyEx
        value = read_uic_image_property(fh)
    elif dtype is str:
        # pascal string
        size = read_int()
        if 0 <= size < 2**10:
            value = struct.unpack('%is' % size, fh.read(size))[0][:-1]
            value = stripnull(value)
        elif offset:
            value = ''
            warnings.warn("corrupt string in uic tag '%s'" % name)
        else:
            raise ValueError("invalid string size %i" % size)
    elif dtype == '%ip':
        # sequence of pascal strings
        value = []
        for _ in range(plane_count):
            size = read_int()
            if 0 <= size < 2**10:
                string = struct.unpack('%is' % size, fh.read(size))[0][:-1]
                string = stripnull(string)
                value.append(string)
            elif offset:
                warnings.warn("corrupt string in uic tag '%s'" % name)
            else:
                raise ValueError("invalid string size %i" % size)
    else:
        # struct or numpy type
        dtype = '<' + dtype
        if '%i' in dtype:
            dtype = dtype % plane_count
        if '(' in dtype:
            # numpy type
            value = fh.read_array(dtype, 1)[0]
            if value.shape[-1] == 2:
                # assume fractions
                value = value[..., 0] / value[..., 1]
        else:
            # struct format
            value = struct.unpack(dtype, fh.read(struct.calcsize(dtype)))
            if len(value) == 1:
                value = value[0]

    if offset:
        fh.seek(pos + 4)

    return name, value


def read_uic_image_property(fh):
    """Read UIC ImagePropertyEx tag from file and return as dict."""
    # TODO: test this
    size = struct.unpack('B', fh.read(1))[0]
    name = struct.unpack('%is' % size, fh.read(size))[0][:-1]
    flags, prop = struct.unpack('<IB', fh.read(5))
    if prop == 1:
        value = struct.unpack('II', fh.read(8))
        value = value[0] / value[1]
    else:
        size = struct.unpack('B', fh.read(1))[0]
        value = struct.unpack('%is' % size, fh.read(size))[0]
    return dict(name=name, flags=flags, value=value)


def read_lsm_info(fh, byteorder, dtype, count, offset_size):
    """Read LSM_INFO tag from file and return as numpy.rec.array."""
    assert byteorder == '<'
    magic_number, structure_size = struct.unpack('<II', fh.read(8))
    if magic_number not in (50350412, 67127628):
        raise ValueError("invalid LSM_INFO structure")
    fh.seek(-8, 1)

    if structure_size < numpy.dtype(CONST.LSM_INFO).itemsize:
        # adjust structure according to structure_size
        lsm_info = []
        size = 0
        for name, dtype in CONST.LSM_INFO:
            size += numpy.dtype(dtype).itemsize
            if size > structure_size:
                break
            lsm_info.append((name, dtype))
    else:
        lsm_info = CONST.LSM_INFO

    return fh.read_record(lsm_info, byteorder=byteorder)


def read_lsm_floatpairs(fh):
    """Read LSM sequence of float pairs from file and return as list."""
    size = struct.unpack('<i', fh.read(4))[0]
    return fh.read_array('<2f8', count=size)


def read_lsm_positions(fh):
    """Read LSM positions from file and return as list."""
    size = struct.unpack('<I', fh.read(4))[0]
    return fh.read_array('<2f8', count=size)


def read_lsm_time_stamps(fh):
    """Read LSM time stamps from file and return as list."""
    size, count = struct.unpack('<ii', fh.read(8))
    if size != (8 + 8 * count):
        raise ValueError("lsm_time_stamps block is too short")
    # return struct.unpack('<%dd' % count, fh.read(8*count))
    return fh.read_array('<f8', count=count)


def read_lsm_event_list(fh):
    """Read LSM events from file and return as list of (time, type, text)."""
    count = struct.unpack('<II', fh.read(8))[1]
    events = []
    while count > 0:
        esize, etime, etype = struct.unpack('<IdI', fh.read(16))
        etext = stripnull(fh.read(esize - 16))
        events.append((etime, etype, etext))
        count -= 1
    return events


def read_lsm_scan_info(fh):
    """Read LSM scan information from file and return as dict."""
    block = {}
    blocks = [block]
    unpack = struct.unpack
    if 0x10000000 != struct.unpack('<I', fh.read(4))[0]:
        # not a Recording sub block
        raise ValueError("not a lsm_scan_info structure")
    fh.read(8)
    while True:
        entry, dtype, size = unpack('<III', fh.read(12))
        if dtype == 2:
            # ascii
            value = stripnull(fh.read(size))
        elif dtype == 4:
            # long
            value = unpack('<i', fh.read(4))[0]
        elif dtype == 5:
            # rational
            value = unpack('<d', fh.read(8))[0]
        else:
            value = 0
        if entry in CONST.LSM_SCAN_INFO_ARRAYS:
            blocks.append(block)
            name = CONST.LSM_SCAN_INFO_ARRAYS[entry]
            newobj = []
            block[name] = newobj
            block = newobj
        elif entry in CONST.LSM_SCAN_INFO_STRUCTS:
            blocks.append(block)
            newobj = {}
            block.append(newobj)
            block = newobj
        elif entry in CONST.LSM_SCAN_INFO_ATTRIBUTES:
            name = CONST.LSM_SCAN_INFO_ATTRIBUTES[entry]
            block[name] = value
        elif entry == 0xffffffff:
            # end sub block
            block = blocks.pop()
        else:
            # unknown entry
            block["entry_0x%x" % entry] = value
        if not blocks:
            break
    return block


def read_tvips_header(fh, byteorder, dtype, count, offset_size):
    """Read TVIPS EM-MENU headers and return as dict."""
    result = {}
    header = fh.read_record(CONST.TVIPS_HEADER_V1, byteorder=byteorder)
    if header.version == 2:
        header = fh.read_record(CONST.TVIPS_HEADER_V2, byteorder=byteorder)
        if header.magic != int(0xaaaaaaaa):
            raise ValueError("invalid TVIPS v2 magic number")
        # decode utf16 strings
        for name, typestr in CONST.TVIPS_HEADER_V2:
            if typestr.startswith('V'):
                s = header[name].tostring().decode('utf16', errors='ignore')
                result[name] = stripnull(s, null='\0')
            else:
                result[name] = header[name]
        # convert nm to m
        for axis in 'xy':
            header['physical_pixel_size_' + axis] /= 1e9
            header['pixel_size_' + axis] /= 1e9
    elif header.version == 1:
        for name, typestr in CONST.TVIPS_HEADER_V2:
            result[name] = header[name]
    else:
        raise ValueError("unknown TVIPS header version")
    return result


def read_fei_metadata(fh, byteorder, dtype, count, offset_size):
    """Read FEI SFEG/HELIOS headers and return as nested dict."""
    result = {}
    section = {}
    for line in fh.read(count).splitlines():
        line = line.strip()
        if line.startswith(b'['):
            section = {}
            result[bytes2str(line[1:-1])] = section
            continue
        try:
            key, value = line.split(b'=')
        except ValueError:
            continue
        section[bytes2str(key)] = astype(value)
    return result


def read_sem_metadata(fh, byteorder, dtype, count, offset_size):
    """Read Zeiss SEM tag and return as dict."""
    result = {'': ()}
    key = None
    for line in fh.read(count).splitlines():
        line = line.decode('cp1252')
        if line.isupper():
            key = line.lower()
        elif key:
            try:
                name, value = line.split('=')
            except ValueError:
                continue
            value = value.strip()
            unit = ''
            try:
                v, u = value.split()
                number = astype(v, (int, float))
                if number != v:
                    value = number
                    unit = u
            except Exception:
                number = astype(value, (int, float))
                if number != value:
                    value = number
                if value in ('No', 'Off'):
                    value = False
                elif value in ('Yes', 'On'):
                    value = True
            result[key] = (name.strip(), value)
            if unit:
                result[key] += (unit,)
            key = None
        else:
            result[''] += (astype(line, (int, float)),)
    return result


def read_nih_image_header(fh, byteorder, dtype, count, offset_size):
    """Read NIH_IMAGE_HEADER tag from file and return as dict."""
    a = fh.read_record(CONST.NIH_IMAGE_HEADER, byteorder=byteorder)
    a = a.newbyteorder(byteorder)
    a.xunit = a.xunit[:a._xunit_len]
    a.um = a.um[:a._um_len]
    return recarray2dict(a)


def read_scanimage_metadata(fh):
    """Read ScanImage BigTIFF v3 static and ROI metadata from open file.

    Return non-varying frame data as dict and ROI group data as JSON.

    The settings can be used to read image data and metadata without parsing
    the TIFF file.

    Raise ValueError if file does not contain valid ScanImage v3 metadata.

    """
    fh.seek(0)
    try:
        byteorder, version = struct.unpack('<2sH', fh.read(4))
        if byteorder != b'II' or version != 43:
            raise Exception
        fh.seek(16)
        magic, version, size0, size1 = struct.unpack('<IIII', fh.read(16))
        if magic != 117637889 or version != 3:
            raise Exception
    except Exception:
        raise ValueError("not a ScanImage BigTIFF v3 file")

    frame_data = matlabstr2py(bytes2str(fh.read(size0)[:-1]))
    roi_data = read_json(fh, '<', None, size1, None)
    return frame_data, roi_data


def read_micromanager_metadata(fh):
    """Read MicroManager non-TIFF settings from open file and return as dict.

    The settings can be used to read image data without parsing the TIFF file.

    Raise ValueError if the file does not contain valid MicroManager metadata.

    """
    fh.seek(0)
    try:
        byteorder = {b'II': '<', b'MM': '>'}[fh.read(2)]
    except IndexError:
        raise ValueError("not a MicroManager TIFF file")

    result = {}
    fh.seek(8)
    (index_header, index_offset, display_header, display_offset,
     comments_header, comments_offset, summary_header, summary_length
     ) = struct.unpack(byteorder + "IIIIIIII", fh.read(32))

    if summary_header != 2355492:
        raise ValueError("invalid MicroManager summary_header")
    result['summary'] = read_json(fh, byteorder, None, summary_length, None)

    if index_header != 54773648:
        raise ValueError("invalid MicroManager index_header")
    fh.seek(index_offset)
    header, count = struct.unpack(byteorder + "II", fh.read(8))
    if header != 3453623:
        raise ValueError("invalid MicroManager index_header")
    data = struct.unpack(byteorder + "IIIII"*count, fh.read(20*count))
    result['index_map'] = {
        'channel': data[::5], 'slice': data[1::5], 'frame': data[2::5],
        'position': data[3::5], 'offset': data[4::5]}

    if display_header != 483765892:
        raise ValueError("invalid MicroManager display_header")
    fh.seek(display_offset)
    header, count = struct.unpack(byteorder + "II", fh.read(8))
    if header != 347834724:
        raise ValueError("invalid MicroManager display_header")
    result['display_settings'] = read_json(fh, byteorder, None, count, None)

    if comments_header != 99384722:
        raise ValueError("invalid MicroManager comments_header")
    fh.seek(comments_offset)
    header, count = struct.unpack(byteorder + "II", fh.read(8))
    if header != 84720485:
        raise ValueError("invalid MicroManager comments_header")
    result['comments'] = read_json(fh, byteorder, None, count, None)

    return result


def read_metaseries_catalog(fh):
    """Read MetaSeries non-TIFF hint catalog from file.

    Raise ValueError if the file does not contain a valid hint catalog.

    """
    # TODO: implement read_metaseries_catalog
    raise NotImplementedError()


def imagej_metadata(data, bytecounts, byteorder):
    """Return ImageJ metadata tag value as dict.

    The 'info' string can have multiple formats, e.g. OIF or ScanImage,
    that might be parsed into dicts using the matlabstr2py or
    oiffile.SettingsFile functions.

    """
    def read_string(data, byteorder):
        return data.decode('utf-16' + {'>': 'be', '<': 'le'}[byteorder])

    def read_double(data, byteorder):
        return struct.unpack(byteorder+('d' * (len(data) // 8)), data)

    def read_bytes(data, byteorder):
        return numpy.fromstring(data, 'uint8')

    metadata_types = {  # big endian
        b'info': ('info', read_string),
        b'labl': ('labels', read_string),
        b'rang': ('ranges', read_double),
        b'luts': ('luts', read_bytes),
        b'roi ': ('roi', read_bytes),
        b'over': ('overlays', read_bytes)}
    metadata_types.update(  # little endian
        dict((k[::-1], v) for k, v in metadata_types.items()))

    if not bytecounts:
        raise ValueError("no ImageJ metadata")

    if not data[:4] in (b'IJIJ', b'JIJI'):
        raise ValueError("invalid ImageJ metadata")

    header_size = bytecounts[0]
    if header_size < 12 or header_size > 804:
        raise ValueError("invalid ImageJ metadata header size")

    ntypes = (header_size - 4) // 8
    header = struct.unpack(byteorder+'4sI'*ntypes, data[4:4+ntypes*8])
    pos = 4 + ntypes * 8
    counter = 0
    result = {}
    for mtype, count in zip(header[::2], header[1::2]):
        values = []
        name, func = metadata_types.get(mtype, (bytes2str(mtype), read_bytes))
        for _ in range(count):
            counter += 1
            pos1 = pos + bytecounts[counter]
            values.append(func(data[pos:pos1], byteorder))
            pos = pos1
        result[name.strip()] = values[0] if count == 1 else values
    return result


def imagej_description_metadata(description):
    """Return metatata from ImageJ image description as dict.

    Raise ValueError if not a valid ImageJ description.

    >>> description = b'ImageJ=1.11a\\nimages=510\\nhyperstack=true\\n'
    >>> imagej_description_metadata(description)  # doctest: +SKIP
    {'ImageJ': '1.11a', 'images': 510, 'hyperstack': True}

    """
    def _bool(val):
        return {b'true': True, b'false': False}[val.lower()]

    result = {}
    for line in description.splitlines():
        try:
            key, val = line.split(b'=')
        except Exception:
            continue
        key = key.strip()
        val = val.strip()
        for dtype in (int, float, _bool, bytes2str):
            try:
                val = dtype(val)
                break
            except Exception:
                pass
        result[bytes2str(key)] = val

    if 'ImageJ' not in result:
        raise ValueError("not a ImageJ image description")
    return result


def imagej_description(shape, rgb=None, colormaped=False, version='1.11a',
                       hyperstack=None, mode=None, loop=None, **kwargs):
    """Return ImageJ image description from data shape.

    ImageJ can handle up to 6 dimensions in order TZCYXS.

    >>> imagej_description((51, 5, 2, 196, 171))  # doctest: +SKIP
    ImageJ=1.11a
    images=510
    channels=2
    slices=5
    frames=51
    hyperstack=true
    mode=grayscale
    loop=false

    """
    if colormaped:
        raise NotImplementedError("ImageJ colormapping not supported")
    shape = imagej_shape(shape, rgb=rgb)
    rgb = shape[-1] in (3, 4)

    result = ['ImageJ=%s' % version]
    append = []
    result.append('images=%i' % product(shape[:-3]))
    if hyperstack is None:
        hyperstack = True
        append.append('hyperstack=true')
    else:
        append.append('hyperstack=%s' % bool(hyperstack))
    if shape[2] > 1:
        result.append('channels=%i' % shape[2])
    if mode is None and not rgb:
        mode = 'grayscale'
    if hyperstack and mode:
        append.append('mode=%s' % mode)
    if shape[1] > 1:
        result.append('slices=%i' % shape[1])
    if shape[0] > 1:
        result.append("frames=%i" % shape[0])
        if loop is None:
            append.append('loop=false')
    if loop is not None:
        append.append('loop=%s' % bool(loop))
    for key, value in kwargs.items():
        append.append('%s=%s' % (key.lower(), value))

    return str2bytes('\n'.join(result + append + ['']))


def imagej_shape(shape, rgb=None):
    """Return shape normalized to 6D ImageJ hyperstack TZCYXS.

    Raise ValueError if not a valid ImageJ hyperstack shape.

    >>> imagej_shape((2, 3, 4, 5, 3), False)
    (2, 3, 4, 5, 3, 1)

    """
    shape = tuple(int(i) for i in shape)
    ndim = len(shape)
    if 1 > ndim > 6:
        raise ValueError("invalid ImageJ hyperstack: not 2 to 6 dimensional")
    if rgb is None:
        rgb = shape[-1] in (3, 4) and ndim > 2
    if rgb and shape[-1] not in (3, 4):
        raise ValueError("invalid ImageJ hyperstack: not a RGB image")
    if not rgb and ndim == 6 and shape[-1] != 1:
        raise ValueError("invalid ImageJ hyperstack: not a non-RGB image")
    if rgb or shape[-1] == 1:
        return (1, ) * (6 - ndim) + shape
    else:
        return (1, ) * (5 - ndim) + shape + (1,)


def json_description(shape, colormaped=False, **metadata):
    """Return JSON image description from data shape and other meta data.

    Return UTF-8 encoded JSON.

    >>> json_description((256, 256, 3), axes='YXS')  # doctest: +SKIP
    b'{"shape": [256, 256, 3], "axes": "YXS"}'

    """
    if colormaped:
        shape = shape + (3,)
    metadata.update({'shape': shape})
    return json.dumps(metadata).encode('utf-8')


def json_description_metadata(description):
    """Return metatata from JSON formated image description as dict.

    Raise ValuError if description is of unknown format.

    >>> description = b'{"shape": [256, 256, 3], "axes": "YXS"}'
    >>> json_description_metadata(description)  # doctest: +SKIP
    {'shape': [256, 256, 3], 'axes': 'YXS'}
    >>> json_description_metadata(b'shape=(256, 256, 3)')
    {'shape': (256, 256, 3)}

    """
    if description[:6] == b'shape=':
        # old style 'shaped' description; not JSON
        shape = tuple(int(i) for i in description[7:-1].split(b','))
        return dict(shape=shape)
    if description[:1] == b'{' and description[-1:] == b'}':
        # JSON description
        return json.loads(description.decode('utf-8'))
    raise ValueError("invalid JSON image description", description)


def fluoview_description_metadata(description, ignore_sections=None):
    """Return metatata from FluoView image description as dict.

    The FluoView image description format is unspecified. Expect failures.

    >>> descr = (b'[Intensity Mapping]\\nMap Ch0: Range=00000 to 02047\\n'
    ...          b'[Intensity Mapping End]')
    >>> fluoview_description_metadata(descr)
    {'Intensity Mapping': {'Map Ch0: Range': '00000 to 02047'}}

    """
    if not description.startswith(b'['):
        raise ValueError("invalid FluoView image description")
    if ignore_sections is None:
        ignore_sections = {'Region Info (Fields)', 'Protocol Description'}

    description = bytes2str(description)
    result = {}
    sections = [result]
    comment = False
    for line in description.splitlines():
        if not comment:
            line = line.strip()
        if not line:
            continue
        if line[0] == '[':
            if line[-5:] == ' End]':
                # close section
                del sections[-1]
                section = sections[-1]
                name = line[1:-5]
                if comment:
                    section[name] = '\n'.join(section[name])
                if name[:4] == 'LUT ':
                    a = numpy.array(section[name], dtype='uint8')
                    a.shape = -1, 3
                    section[name] = a
                continue
            # new section
            comment = False
            name = line[1:-1]
            if name[:4] == 'LUT ':
                section = []
            elif name in ignore_sections:
                section = []
                comment = True
            else:
                section = {}
            sections.append(section)
            result[name] = section
            continue
        # add entry
        if comment:
            section.append(line)
            continue
        line = line.split('=', 1)
        if len(line) == 1:
            section[line[0].strip()] = None
            continue
        key, value = line
        if key[:4] == 'RGB ':
            section.extend(int(rgb) for rgb in value.split())
        else:
            section[key.strip()] = astype(value.strip())
    return result


def pilatus_description_metadata(description):
    """Return metatata from Pilatus image description as dict.

    Return metadata from Pilatus pixel array detectors by Dectris, created
    by camserver or TVX software.

    >>> pilatus_description_metadata(b'# Pixel_size 172e-6 m x 172e-6 m')
    {'Pixel_size': (0.000172, 0.000172)}

    """
    if not description.startswith(b'# '):
        raise ValueError("invalid Pilatus header")
    result = {}
    description = bytes2str(description)
    for c in '#:=,()':
        description = description.replace(c, ' ')
    for line in description.split('\n'):
        if line[:2] != '  ':
            continue
        line = line.split()
        name = line[0]
        if line[0] not in CONST.PILATUS_HEADER:
            try:
                result['DateTime'] = datetime.datetime.strptime(
                    ' '.join(line), '%Y-%m-%dT%H %M %S.%f')
            except Exception:
                result[name] = ' '.join(line[1:])
            continue
        indices, dtype = CONST.PILATUS_HEADER[line[0]]
        if isinstance(indices[0], slice):
            # assumes one slice
            values = line[indices[0]]
        else:
            values = [line[i] for i in indices]
        if dtype is float and values[0] == 'not':
            values = ['NaN']
        values = tuple(dtype(v) for v in values)
        if dtype == str:
            values = ' '.join(values)
        elif len(values) == 1:
            values = values[0]
        result[name] = values
    return result


def svs_description_metadata(description):
    """Return metatata from Aperio image description as dict.

    The Aperio image description format is unspecified. Expect failures.

    >>> svs_description_metadata(b'Aperio Image Library v1.0')
    {'Aperio Image Library': 'v1.0'}

    """
    if not description.startswith(b'Aperio Image Library '):
        raise ValueError("invalid Aperio image description")
    result = {}
    description = bytes2str(description)
    lines = description.split('\n')
    key, value = lines[0].strip().rsplit(None, 1)  # 'Aperio Image Library'
    result[key.strip()] = value.strip()
    if len(lines) == 1:
        return result
    items = lines[1].split('|')
    result[''] = items[0].strip()  # TODO: parse this?
    for item in items[1:]:
        key, value = item.split(' = ')
        result[key.strip()] = astype(value.strip())
    return result


def stk_description_metadata(description):
    """Return metadata from MetaMorph image description as list of dict.

    The MetaMorph image description format is unspecified. Expect failures.

    """
    description = description.strip()
    if not description:
        return []
    try:
        description = bytes2str(description)
    except UnicodeDecodeError:
        warnings.warn("failed to parse MetaMorph image description")
        return []
    result = []
    for plane in description.split('\x00'):
        d = {}
        for line in plane.split('\r\n'):
            line = line.split(':', 1)
            if len(line) > 1:
                name, value = line
                d[name.strip()] = astype(value.strip())
            else:
                value = line[0].strip()
                if value:
                    if '' in d:
                        d[''].append(value)
                    else:
                        d[''] = [value]
        result.append(d)
    return result


def metaseries_description_metadata(description):
    """Return metatata from MetaSeries image description as dict."""
    if not description.startswith(b'<MetaData>'):
        raise ValueError("invalid MetaSeries image description")

    description = bytes2str(description)

    from xml.etree import cElementTree as etree  # delayed import
    root = etree.fromstring(description)
    types = {'float': float, 'int': int,
             'bool': lambda x: asbool(x, 'on', 'off')}

    def parse(root, result):
        # recursive
        for child in root:
            attrib = child.attrib
            if not attrib:
                result[child.tag] = parse(child, {})
                continue
            if 'id' in attrib:
                i = attrib['id']
                t = attrib['type']
                v = attrib['value']
                if t in types:
                    result[i] = types[t](v)
                else:
                    result[i] = v
        return result

    adict = parse(root, {})
    if 'Description' in adict:
        adict['Description'] = adict['Description'].replace('&#13;&#10;', '\n')
    return adict


def scanimage_description_metadata(description):
    """Return metatata from ScanImage image description as dict."""
    return matlabstr2py(bytes2str(description))


def scanimage_artist_metadata(artist):
    """Return metatata from ScanImage artist tag as dict."""
    try:
        return json.loads(unicode(stripnull(artist), 'utf-8'))
    except ValueError:
        warnings.warn("invalid JSON '%s'" % artist)


def _replace_by(module_function, package=__package__, warn=None, prefix='_'):
    """Try replace decorated function by module.function."""
    def _warn(e, warn):
        if warn is None:
            warn = "\n  Functionality might be degraded or be slow.\n"
        elif warn is True:
            warn = ''
        elif not warn:
            return
        warnings.warn("%s%s" % (e, warn))

    try:
        from importlib import import_module
    except ImportError as e:
        _warn(e, warn)
        return lambda func: func

    def decorate(func, module_function=module_function, warn=warn):
        module, function = module_function.split('.')
        try:
            if package:
                module = import_module('.' + module, package=package)
            else:
                module = import_module(module)
        except Exception as e:
            _warn(e, warn)
            return func
        try:
            func, oldfunc = getattr(module, function), func
        except Exception as e:
            _warn(e, warn)
            return func
        globals()[prefix + func.__name__] = oldfunc
        return func

    return decorate


def decode_floats(data):
    """Decode floating point horizontal differencing.

    The TIFF predictor type 3 reorders the bytes of the image values and
    applies horizontal byte differencing to improve compression of floating
    point images. The ordering of interleaved color channels is preserved.

    Parameters
    ----------
    data : numpy.ndarray
        The image to be decoded. The dtype must be a floating point.
        The shape must include the number of contiguous samples per pixel
        even if 1.

    """
    shape = data.shape
    dtype = data.dtype
    if len(shape) < 3:
        raise ValueError('invalid data shape')
    if dtype.char not in 'dfe':
        raise ValueError('not a floating point image')
    littleendian = data.dtype.byteorder == '<' or (
        sys.byteorder == 'little' and data.dtype.byteorder == '=')
    # undo horizontal byte differencing
    data = data.view('uint8')
    data.shape = shape[:-2] + (-1,) + shape[-1:]
    numpy.cumsum(data, axis=-2, dtype='uint8', out=data)
    # reorder bytes
    if littleendian:
        data.shape = shape[:-2] + (-1,) + shape[-2:]
    data = numpy.swapaxes(data, -3, -2)
    data = numpy.swapaxes(data, -2, -1)
    data = data[..., ::-1]
    # back to float
    data = numpy.ascontiguousarray(data)
    data = data.view(dtype)
    data.shape = shape
    return data


def decode_jpeg(encoded, tables=b'', photometric=None,
                ycbcr_subsampling=None, ycbcr_positioning=None):
    """Decode JPEG encoded byte string (using _czifile extension module)."""
    from czifile import _czifile
    image = _czifile.decode_jpeg(encoded, tables)
    if photometric == 'rgb' and ycbcr_subsampling and ycbcr_positioning:
        # TODO: convert YCbCr to RGB
        pass
    return image.tostring()


@_replace_by('_tifffile.decode_packbits')
def decode_packbits(encoded):
    """Decompress PackBits encoded byte string.

    PackBits is a simple byte-oriented run-length compression scheme.

    """
    func = ord if sys.version[0] == '2' else lambda x: x
    result = []
    result_extend = result.extend
    i = 0
    try:
        while True:
            n = func(encoded[i]) + 1
            i += 1
            if n < 129:
                result_extend(encoded[i:i+n])
                i += n
            elif n > 129:
                result_extend(encoded[i:i+1] * (258-n))
                i += 1
    except IndexError:
        pass
    return b''.join(result) if sys.version[0] == '2' else bytes(result)


@_replace_by('_tifffile.decode_lzw')
def decode_lzw(encoded):
    """Decompress LZW (Lempel-Ziv-Welch) encoded TIFF strip (byte string).

    The strip must begin with a CLEAR code and end with an EOI code.

    This is an implementation of the LZW decoding algorithm described in (1).
    It is not compatible with old style LZW compressed files like quad-lzw.tif.

    """
    len_encoded = len(encoded)
    bitcount_max = len_encoded * 8
    unpack = struct.unpack

    if sys.version[0] == '2':
        newtable = [chr(i) for i in range(256)]
    else:
        newtable = [bytes([i]) for i in range(256)]
    newtable.extend((0, 0))

    def next_code():
        """Return integer of 'bitw' bits at 'bitcount' position in encoded."""
        start = bitcount // 8
        s = encoded[start:start+4]
        try:
            code = unpack('>I', s)[0]
        except Exception:
            code = unpack('>I', s + b'\x00'*(4-len(s)))[0]
        code <<= bitcount % 8
        code &= mask
        return code >> shr

    switchbitch = {  # code: bit-width, shr-bits, bit-mask
        255: (9, 23, int(9*'1'+'0'*23, 2)),
        511: (10, 22, int(10*'1'+'0'*22, 2)),
        1023: (11, 21, int(11*'1'+'0'*21, 2)),
        2047: (12, 20, int(12*'1'+'0'*20, 2)), }
    bitw, shr, mask = switchbitch[255]
    bitcount = 0

    if len_encoded < 4:
        raise ValueError("strip must be at least 4 characters long")

    if next_code() != 256:
        raise ValueError("strip must begin with CLEAR code")

    code = 0
    oldcode = 0
    result = []
    result_append = result.append
    while True:
        code = next_code()  # ~5% faster when inlining this function
        bitcount += bitw
        if code == 257 or bitcount >= bitcount_max:  # EOI
            break
        if code == 256:  # CLEAR
            table = newtable[:]
            table_append = table.append
            lentable = 258
            bitw, shr, mask = switchbitch[255]
            code = next_code()
            bitcount += bitw
            if code == 257:  # EOI
                break
            result_append(table[code])
        else:
            if code < lentable:
                decoded = table[code]
                newcode = table[oldcode] + decoded[:1]
            else:
                newcode = table[oldcode]
                newcode += newcode[:1]
                decoded = newcode
            result_append(decoded)
            table_append(newcode)
            lentable += 1
        oldcode = code
        if lentable in switchbitch:
            bitw, shr, mask = switchbitch[lentable]

    if code != 257:
        warnings.warn("unexpected end of lzw stream (code %i)" % code)

    return b''.join(result)


@_replace_by('_tifffile.unpack_ints')
def unpack_ints(data, dtype, itemsize, runlen=0):
    """Decompress byte string to array of integers of any bit size <= 32.

    This Python implementation is slow and only handles itemsizes 1, 2, 4, 8,
    16, 32, and 64.

    Parameters
    ----------
    data : byte str
        Data to decompress.
    dtype : numpy.dtype or str
        A numpy boolean or integer type.
    itemsize : int
        Number of bits per integer.
    runlen : int
        Number of consecutive integers, after which to start at next byte.

    Examples
    --------
    >>> unpack_ints(b'a', 'B', 1)
    array([0, 1, 1, 0, 0, 0, 0, 1], dtype=uint8)
    >>> unpack_ints(b'ab', 'B', 2)
    array([1, 2, 0, 1, 1, 2, 0, 2], dtype=uint8)

    """
    if itemsize == 1:  # bitarray
        data = numpy.fromstring(data, '|B')
        data = numpy.unpackbits(data)
        if runlen % 8:
            data = data.reshape(-1, runlen + (8 - runlen % 8))
            data = data[:, :runlen].reshape(-1)
        return data.astype(dtype)

    dtype = numpy.dtype(dtype)
    if itemsize in (8, 16, 32, 64):
        return numpy.fromstring(data, dtype)
    if itemsize not in (1, 2, 4, 8, 16, 32):
        raise ValueError("itemsize not supported: %i" % itemsize)
    if dtype.kind not in "biu":
        raise ValueError("invalid dtype")

    itembytes = next(i for i in (1, 2, 4, 8) if 8 * i >= itemsize)
    if itembytes != dtype.itemsize:
        raise ValueError("dtype.itemsize too small")
    if runlen == 0:
        runlen = (8 * len(data)) // itemsize
    skipbits = runlen * itemsize % 8
    if skipbits:
        skipbits = 8 - skipbits
    shrbits = itembytes*8 - itemsize
    bitmask = int(itemsize*'1'+'0'*shrbits, 2)
    dtypestr = '>' + dtype.char  # dtype always big endian?

    unpack = struct.unpack
    l = runlen * (len(data)*8 // (runlen*itemsize + skipbits))
    result = numpy.empty((l,), dtype)
    bitcount = 0
    for i in range(l):
        start = bitcount // 8
        s = data[start:start+itembytes]
        try:
            code = unpack(dtypestr, s)[0]
        except Exception:
            code = unpack(dtypestr, s + b'\x00'*(itembytes-len(s)))[0]
        code <<= bitcount % 8
        code &= bitmask
        result[i] = code >> shrbits
        bitcount += itemsize
        if (i+1) % runlen == 0:
            bitcount += skipbits
    return result


def unpack_rgb(data, dtype='<B', bitspersample=(5, 6, 5), rescale=True):
    """Return array from byte string containing packed samples.

    Use to unpack RGB565 or RGB555 to RGB888 format.

    Parameters
    ----------
    data : byte str
        The data to be decoded. Samples in each pixel are stored consecutively.
        Pixels are aligned to 8, 16, or 32 bit boundaries.
    dtype : numpy.dtype
        The sample data type. The byteorder applies also to the data stream.
    bitspersample : tuple
        Number of bits for each sample in a pixel.
    rescale : bool
        Upscale samples to the number of bits in dtype.

    Returns
    -------
    result : ndarray
        Flattened array of unpacked samples of native dtype.

    Examples
    --------
    >>> data = struct.pack('BBBB', 0x21, 0x08, 0xff, 0xff)
    >>> print(unpack_rgb(data, '<B', (5, 6, 5), False))
    [ 1  1  1 31 63 31]
    >>> print(unpack_rgb(data, '<B', (5, 6, 5)))
    [  8   4   8 255 255 255]
    >>> print(unpack_rgb(data, '<B', (5, 5, 5)))
    [ 16   8   8 255 255 255]

    """
    dtype = numpy.dtype(dtype)
    bits = int(numpy.sum(bitspersample))
    if not (bits <= 32 and all(i <= dtype.itemsize*8 for i in bitspersample)):
        raise ValueError("sample size not supported %s" % str(bitspersample))
    dt = next(i for i in 'BHI' if numpy.dtype(i).itemsize*8 >= bits)
    data = numpy.fromstring(data, dtype.byteorder+dt)
    result = numpy.empty((data.size, len(bitspersample)), dtype.char)
    for i, bps in enumerate(bitspersample):
        t = data >> int(numpy.sum(bitspersample[i+1:]))
        t &= int('0b'+'1'*bps, 2)
        if rescale:
            o = ((dtype.itemsize * 8) // bps + 1) * bps
            if o > data.dtype.itemsize * 8:
                t = t.astype('I')
            t *= (2**o - 1) // (2**bps - 1)
            t //= 2**(o - (dtype.itemsize * 8))
        result[:, i] = t
    return result.reshape(-1)


@_replace_by('_tifffile.reverse_bitorder')
def reverse_bitorder(data):
    """Reverse bits in each byte of byte string or numpy array.

    Decode data where pixels with lower column values are stored in the
    lower-order bits of the bytes (fill_order == 'lsb2msb').

    Parameters
    ----------
    data : byte string or ndarray
        The data to be bit reversed. If byte string, a new bit-reversed byte
        string is returned. Numpy arrays are bit-reversed in-place.

    Examples
    --------
    >>> reverse_bitorder(b'\\x01\\x64')
    b'\\x80&'
    >>> data = numpy.array([1, 666], dtype='uint16')
    >>> reverse_bitorder(data)
    >>> data
    array([  128, 16473], dtype=uint16)

    """
    try:
        view = data.view('uint8')
        numpy.take(CONST.REVERSE_BITORDER_ARRAY, view, out=view)
    except AttributeError:
        return data.translate(CONST.REVERSE_BITORDER_BYTES)
    except ValueError:
        raise NotImplementedError("slices of arrays not supported")


def apply_colormap(image, colormap, contig=True):
    """Return palette-colored image.

    The image values are used to index the colormap on axis 1. The returned
    image is of shape image.shape+colormap.shape[0] and dtype colormap.dtype.

    Parameters
    ----------
    image : numpy.ndarray
        Indexes into the colormap.
    colormap : numpy.ndarray
        RGB lookup table aka palette of shape (3, 2**bits_per_sample).
    contig : bool
        If True, return a contiguous array.

    Examples
    --------
    >>> image = numpy.arange(256, dtype='uint8')
    >>> colormap = numpy.vstack([image, image, image]).astype('uint16') * 256
    >>> apply_colormap(image, colormap)[-1]
    array([65280, 65280, 65280], dtype=uint16)

    """
    image = numpy.take(colormap, image, axis=1)
    image = numpy.rollaxis(image, 0, image.ndim)
    if contig:
        image = numpy.ascontiguousarray(image)
    return image


def reorient(image, orientation):
    """Return reoriented view of image array.

    Parameters
    ----------
    image : numpy.ndarray
        Non-squeezed output of asarray() functions.
        Axes -3 and -2 must be image length and width respectively.
    orientation : int or str
        One of TIFF_ORIENTATIONS keys or values.

    """
    o = CONST.TIFF_ORIENTATIONS.get(orientation, orientation)
    if o == 'top_left':
        return image
    elif o == 'top_right':
        return image[..., ::-1, :]
    elif o == 'bottom_left':
        return image[..., ::-1, :, :]
    elif o == 'bottom_right':
        return image[..., ::-1, ::-1, :]
    elif o == 'left_top':
        return numpy.swapaxes(image, -3, -2)
    elif o == 'right_top':
        return numpy.swapaxes(image, -3, -2)[..., ::-1, :]
    elif o == 'left_bottom':
        return numpy.swapaxes(image, -3, -2)[..., ::-1, :, :]
    elif o == 'right_bottom':
        return numpy.swapaxes(image, -3, -2)[..., ::-1, ::-1, :]


def repeat_nd(a, repeats):
    """Return read-only view into input array with elements repeated.

    Zoom nD image by integer factors using nearest neighbor interpolation
    (box filter).

    Parameters
    ----------
    a : array_like
        Input array.
    repeats : sequence of int
        The number of repetitions to apply along each dimension of input array.

    Example
    -------
    >>> repeat_nd([[1, 2], [3, 4]], (2, 2))
    array([[1, 1, 2, 2],
           [1, 1, 2, 2],
           [3, 3, 4, 4],
           [3, 3, 4, 4]])

    """
    a = numpy.asarray(a)
    reshape = []
    shape = []
    strides = []
    for i, j, k in zip(a.strides, a.shape, repeats):
        shape.extend((j, k))
        strides.extend((i, 0))
        reshape.append(j * k)
    return numpy.lib.stride_tricks.as_strided(
        a, shape, strides, writeable=False).reshape(reshape)


def reshape_nd(data_or_shape, ndim):
    """Return image array or shape with at least ndim dimensions.

    Prepend 1s to image shape as necessary.

    >>> reshape_nd(numpy.empty(0), 1).shape
    (0,)
    >>> reshape_nd(numpy.empty(1), 2).shape
    (1, 1)
    >>> reshape_nd(numpy.empty((2, 3)), 3).shape
    (1, 2, 3)
    >>> reshape_nd(numpy.empty((3, 4, 5)), 3).shape
    (3, 4, 5)
    >>> reshape_nd((2, 3), 3)
    (1, 2, 3)

    """
    is_shape = isinstance(data_or_shape, tuple)
    shape = data_or_shape if is_shape else data_or_shape.shape
    if len(shape) >= ndim:
        return data_or_shape
    shape = (1,) * (ndim - len(shape)) + shape
    return shape if is_shape else data_or_shape.reshape(shape)


def squeeze_axes(shape, axes, skip='XY'):
    """Return shape and axes with single-dimensional entries removed.

    Remove unused dimensions unless their axes are listed in 'skip'.

    >>> squeeze_axes((5, 1, 2, 1, 1), 'TZYXC')
    ((5, 2, 1), 'TYX')

    """
    if len(shape) != len(axes):
        raise ValueError("dimensions of axes and shape do not match")
    shape, axes = zip(*(i for i in zip(shape, axes)
                        if i[0] > 1 or i[1] in skip))
    return tuple(shape), ''.join(axes)


def transpose_axes(image, axes, asaxes='CTZYX'):
    """Return image with its axes permuted to match specified axes.

    A view is returned if possible.

    >>> transpose_axes(numpy.zeros((2, 3, 4, 5)), 'TYXC', asaxes='CTZYX').shape
    (5, 2, 1, 3, 4)

    """
    for ax in axes:
        if ax not in asaxes:
            raise ValueError("unknown axis %s" % ax)
    # add missing axes to image
    shape = image.shape
    for ax in reversed(asaxes):
        if ax not in axes:
            axes = ax + axes
            shape = (1,) + shape
    image = image.reshape(shape)
    # transpose axes
    image = image.transpose([axes.index(ax) for ax in asaxes])
    return image


def reshape_axes(axes, shape, newshape, unknown='Q'):
    """Return axes matching new shape.

    Unknown dimensions are labelled 'Q'.

    >>> reshape_axes('YXS', (219, 301, 1), (219, 301))
    'YX'
    >>> reshape_axes('IYX', (12, 219, 301), (3, 4, 219, 1, 301, 1))
    'QQYQXQ'

    """
    shape = tuple(shape)
    newshape = tuple(newshape)
    if len(axes) != len(shape):
        raise ValueError("axes do not match shape")

    size = product(shape)
    newsize = product(newshape)
    if size != newsize:
        raise ValueError("can not reshape %s to %s" % (shape, newshape))
    if not axes or not newshape:
        return ''

    lendiff = max(0, len(shape) - len(newshape))
    if lendiff:
        newshape = newshape + (1,) * lendiff

    i = len(shape)-1
    prodns = 1
    prods = 1
    result = []
    for ns in newshape[::-1]:
        prodns *= ns
        while i > 0 and shape[i] == 1 and ns != 1:
            i -= 1
        if ns == shape[i] and prodns == prods*shape[i]:
            prods *= shape[i]
            result.append(axes[i])
            i -= 1
        else:
            result.append(unknown)

    return ''.join(reversed(result[lendiff:]))


def stack_pages(pages, memmap=False, tempdir=None, *args, **kwargs):
    """Read data from sequence of TiffPage and stack them vertically.

    If memmap is True, return an array stored in a binary file on disk.
    Additional parameters are passsed to the page asarray function.

    """
    if len(pages) == 0:
        raise ValueError("no pages")

    if len(pages) == 1:
        return pages[0].asarray(memmap=memmap, *args, **kwargs)

    data0 = pages[0].asarray(*args, **kwargs)
    shape = (len(pages),) + data0.shape
    if memmap:
        with tempfile.NamedTemporaryFile(dir=tempdir) as fh:
            data = numpy.memmap(fh, dtype=data0.dtype, shape=shape)
    else:
        data = numpy.empty(shape, dtype=data0.dtype)

    data[0] = data0
    if memmap:
        data.flush()
    del data0
    for i, page in enumerate(pages[1:]):
        data[i+1] = page.asarray(*args, **kwargs)
        if memmap:
            data.flush()

    return data


def clean_offsets_counts(offsets, counts):
    """Return cleaned offsets and byte counts.

    Remove zero offsets and counts. Use to sanitize _offsets and _byte_counts
    tag values for strips or tiles.

    """
    offsets = list(offsets)
    counts = list(counts)
    assert len(offsets) == len(counts)
    j = 0
    for i, (o, b) in enumerate(zip(offsets, counts)):
        if o > 0 and b > 0:
            if i > j:
                offsets[j] = o
                counts[j] = b
            j += 1
        elif b > 0 and o <= 0:
            raise ValueError("invalid offset")
        else:
            warnings.warn("empty byte count")
    if j == 0:
        j = 1
    return offsets[:j], counts[:j]


def matlabstr2py(s):
    """Return Python object from Matlab string representation.

    Return str, bool, int, float, list (Matlab arrays or cells), or
    dict (Matlab structures) types.

    Use to access ScanImage metadata.

    >>> matlabstr2py('1')
    1
    >>> matlabstr2py("['x y z' true false; 1 2.0 -3e4; NaN Inf @class]")
    [['x y z', True, False], [1, 2.0, -30000.0], [nan, inf, '@class']]
    >>> d = matlabstr2py("SI.hChannels.channelType = {'stripe' 'stripe'}\\n"
    ...                  "SI.hChannels.channelsActive = 2")
    >>> d['SI.hChannels.channelType']
    ['stripe', 'stripe']

    """
    # TODO: handle invalid input
    # TODO: review unboxing of multidimensional arrays

    def lex(s):
        # return sequence of tokens from matlab string representation
        tokens = ['[']
        while True:
            t, i = next_token(s)
            if t is None:
                break
            if t == ';':
                tokens.extend((']', '['))
            elif t == '[':
                tokens.extend(('[', '['))
            elif t == ']':
                tokens.extend((']', ']'))
            else:
                tokens.append(t)
            s = s[i:]
        tokens.append(']')
        return tokens

    def next_token(s):
        # return next token in matlab string
        length = len(s)
        if length == 0:
            return None, 0
        i = 0
        while i < length and s[i] == ' ':
            i += 1
        if i == length:
            return None, i
        if s[i] in '{[;]}':
            return s[i], i + 1
        if s[i] == "'":
            j = i + 1
            while j < length and s[j] != "'":
                j += 1
            return s[i: j+1], j + 1
        j = i
        while j < length and not s[j] in ' {[;]}':
            j += 1
        return s[i:j], j

    def value(s, fail=False):
        # return Python value of token
        s = s.strip()
        if not s:
            return s
        if len(s) == 1:
            try:
                return int(s)
            except Exception:
                if fail:
                    raise ValueError()
                return s
        if s[0] == "'":
            if fail and s[-1] != "'" or "'" in s[1:-1]:
                raise ValueError()
            return s[1:-1]
        if fail and any(i in s for i in " ';[]{}"):
            raise ValueError()
        if s[0] == '@':
            return s
        if s == 'true':
            return True
        if s == 'false':
            return False
        if '.' in s or 'e' in s:
            return float(s)
        try:
            return int(s)
        except Exception:
            pass
        try:
            return float(s)  # nan, inf
        except Exception:
            if fail:
                raise ValueError()
        return s

    def parse(s):
        # return Python value from string representation of Matlab value
        s = s.strip()
        try:
            return value(s, fail=True)
        except ValueError:
            pass
        result = add2 = []
        levels = [add2]
        for t in lex(s):
            if t in '[{':
                add2 = []
                levels.append(add2)
            elif t in ']}':
                x = levels.pop()
                if len(x) == 1 and isinstance(x[0], list):
                    x = x[0]
                add2 = levels[-1]
                add2.append(x)
            else:
                add2.append(value(t))
        if len(result) == 1 and isinstance(result[0], list):
            result = result[0]
        return result

    if '\r' in s or '\n' in s:
        # structure
        d = {}
        for line in s.splitlines():
            if not line.strip():
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            if any(c in k for c in " ';[]{}"):
                continue
            d[k] = parse(v.strip())
        return d
    else:
        return parse(s)


def stripnull(string, null=b'\x00'):
    """Return string truncated at first null character.

    Clean NULL terminated C strings. For unicode strings use null='\\0'.

    >>> stripnull(b'string\\x00')
    b'string'
    >>> stripnull('string\\x00', null='\\0')
    'string'

    """
    i = string.find(null)
    return string if (i < 0) else string[:i]


def stripascii(string):
    """Return string truncated at last byte that is 7-bit ASCII.

    Clean NULL separated and terminated TIFF strings.

    >>> stripascii(b'string\\x00string\\n\\x01\\x00')
    b'string\\x00string\\n'
    >>> stripascii(b'\\x00')
    b''

    """
    # TODO: pythonize this
    i = len(string)
    while i:
        i -= 1
        if 8 < byte2int(string[i]) < 127:
            break
    else:
        i = -1
    return string[:i+1]


def asbool(value, true=(b'true', u'true'), false=(b'false', u'false')):
    """Return string as bool if possible, else raise TypeError.

    >>> asbool(b' False ')
    False

    """
    value = value.strip().lower()
    if value in true:  # might raise UnicodeWarning/BytesWarning
        return True
    if value in false:
        return False
    raise TypeError()


def astype(value, types=None):
    """Return argument as one of types if possible.

    >>> astype('42')
    42
    >>> astype('3.14')
    3.14
    >>> astype('True')
    True
    >>> astype(b'Neee-Wom')
    'Neee-Wom'

    """
    if types is None:
        types = int, float, asbool, bytes2str
    for typ in types:
        try:
            return typ(value)
        except (ValueError, TypeError, UnicodeEncodeError):
            pass
    return value


def format_size(size, threshold=1536):
    """Return file size as string from byte size.

    >>> format_size(1234)
    '1234 B'
    >>> format_size(12345678901)
    '11.50 GiB'

    """
    if size < threshold:
        return "%i B" % size
    for unit in ('KiB', 'MiB', 'GiB', 'TiB', 'PiB'):
        size /= 1024.0
        if size < threshold:
            return "%.2f %s" % (size, unit)


def sequence(value):
    """Return tuple containing value if value is not a sequence.

    >>> sequence(1)
    (1,)
    >>> sequence([1])
    [1]

    """
    try:
        len(value)
        return value
    except TypeError:
        return (value,)


def product(iterable):
    """Return product of sequence of numbers.

    Equivalent of functools.reduce(operator.mul, iterable, 1).
    Multiplying numpy integers might overflow.

    >>> product([2**8, 2**30])
    274877906944
    >>> product([])
    1

    """
    prod = 1
    for i in iterable:
        prod *= i
    return prod


def natural_sorted(iterable):
    """Return human sorted list of strings.

    E.g. for sorting file names.

    >>> natural_sorted(['f1', 'f2', 'f10'])
    ['f1', 'f2', 'f10']

    """
    def sortkey(x):
        return [(int(c) if c.isdigit() else c) for c in re.split(numbers, x)]

    numbers = re.compile(r'(\d+)')
    return sorted(iterable, key=sortkey)


def excel_datetime(timestamp, epoch=datetime.datetime.fromordinal(693594)):
    """Return datetime object from timestamp in Excel serial format.

    Convert LSM time stamps.

    >>> excel_datetime(40237.029999999795)
    datetime.datetime(2010, 2, 28, 0, 43, 11, 999982)

    """
    return epoch + datetime.timedelta(timestamp)


def julian_datetime(julianday, milisecond=0):
    """Return datetime from days since 1/1/4713 BC and ms since midnight.

    Convert Julian dates according to MetaMorph.

    >>> julian_datetime(2451576, 54362783)
    datetime.datetime(2000, 2, 2, 15, 6, 2, 783)

    """
    if julianday <= 1721423:
        # no datetime before year 1
        return None

    a = julianday + 1
    if a > 2299160:
        alpha = math.trunc((a - 1867216.25) / 36524.25)
        a += 1 + alpha - alpha // 4
    b = a + (1524 if a > 1721423 else 1158)
    c = math.trunc((b - 122.1) / 365.25)
    d = math.trunc(365.25 * c)
    e = math.trunc((b - d) / 30.6001)

    day = b - d - math.trunc(30.6001 * e)
    month = e - (1 if e < 13.5 else 13)
    year = c - (4716 if month > 2.5 else 4715)

    hour, milisecond = divmod(milisecond, 1000 * 60 * 60)
    minute, milisecond = divmod(milisecond, 1000 * 60)
    second, milisecond = divmod(milisecond, 1000)

    return datetime.datetime(year, month, day,
                             hour, minute, second, milisecond)


def byteorder_isnative(byteorder):
    """Return if byteorder matches the system's byteorder.

    >>> byteorder_isnative('=')
    True

    """
    if byteorder == '=' or byteorder == sys.byteorder:
        return True
    keys = {'big': '>', 'little': '<'}
    return keys.get(byteorder, byteorder) == keys[sys.byteorder]


def recarray2dict(recarray):
    """Return numpy.recarray as dict."""
    return dict((name, value.tolist() if value.ndim < 2 else value)
                for name, value in zip(recarray.dtype.names, recarray))


def pprint_xml(arg):
    """Return pretty formatted XML."""
    try:
        import lxml.etree as etree
        xml = etree.fromstring(arg)
        xml = etree.tostring(xml, pretty_print=True, encoding="unicode")
    except Exception:
        xml = bytes2str(arg).replace('><', '>\n<').replace('><', '>\n<')
    return xml.replace('  ', ' ').replace('\t', ' ')


def pprint(arg, maxlines=None, linewidth=None):
    """Return pretty formatted representation of object as string."""
    if maxlines is None:
        maxlines = CONST.PRINT_MAX_LINES
    elif not maxlines:
        maxlines = 2**32
    if linewidth is None:
        linewidth = CONST.PRINT_LINE_WIDTH
    elif not linewidth:
        linewidth = 2**32

    numpy.set_printoptions(threshold=100, linewidth=linewidth)

    if isinstance(arg, basestring):
        if arg[:5].lower() == b'<?xml':
            arg = pprint_xml(arg)
        elif isinstance(arg, bytes):
            arg = bytes2str(arg)
        arg = arg.replace('\r', '\n').replace('\n\n', '\n')
        arg = arg.rstrip()
    elif isinstance(arg, numpy.record):
        arg = arg.pprint()
    else:
        from pprint import pformat
        compact = {} if sys.version_info[0] == 2 else dict(compact=True)
        arg = pformat(arg, width=linewidth, **compact)
    argl = list(arg.splitlines())
    if len(argl) > maxlines:
        arg = "\n".join(argl[:maxlines] +
                        ['...truncated to %i lines.' % maxlines])
    return arg


def snipstr(string, length=16, ellipse=None):
    """Return string cut in middle to specified length.

    >>> snipstr('abcdefghijklmnop', 8)
    'abcd…nop'

    """
    size = len(string)
    if size <= length:
        return string
    if ellipse is None:
        if isinstance(string, bytes):
            ellipse = b'...'
        else:
            ellipse = u'\u2026'
    esize = len(ellipse)
    if length < esize + 1:
        return string[:length]
    if length < esize + 4:
        return string[:length-esize] + ellipse
    half = (length - esize) // 2
    return string[:half + (length-esize) % 2] + ellipse + string[-half:]


def parse_kwargs(kwargs, *keys, **keyvalues):
    """Return dict with keys from keys|keyvals and values from kwargs|keyvals.

    Existing keys are deleted from kwargs.

    >>> kwargs = {'one': 1, 'two': 2, 'four': 4}
    >>> kwargs2 = parse_kwargs(kwargs, 'two', 'three', four=None, five=5)
    >>> kwargs == {'one': 1}
    True
    >>> kwargs2 == {'two': 2, 'four': 4, 'five': 5}
    True

    """
    result = {}
    for key in keys:
        if key in kwargs:
            result[key] = kwargs[key]
            del kwargs[key]
    for key, value in keyvalues.items():
        if key in kwargs:
            result[key] = kwargs[key]
            del kwargs[key]
        else:
            result[key] = value
    return result


def update_kwargs(kwargs, **keyvalues):
    """Update dict with keys and values if keys do not already exist.

    >>> kwargs = {'one': 1, }
    >>> update_kwargs(kwargs, one=None, two=2)
    >>> kwargs == {'one': 1, 'two': 2}
    True

    """
    for key, value in keyvalues.items():
        if key not in kwargs:
            kwargs[key] = value


def lsm2bin(lsmfile, binfile=None, tile=(256, 256), verbose=True):
    """Convert [MP]TZCYX LSM file to series of BIN files.

    One BIN file containing 'ZCYX' data is created for each position, time,
    and tile. The position, time, and tile indices are encoded at the end
    of the filenames.

    """
    verbose = print_ if verbose else lambda *a, **b: None

    if binfile is None:
        binfile = lsmfile
    elif binfile.lower() == 'none':
        binfile = None
    if binfile:
        binfile += "_(z%ic%iy%ix%i)_m%%ip%%it%%03iy%%ix%%i.bin"

    verbose("\nOpening LSM file... ", end='', flush=True)
    start_time = time.time()

    with TiffFile(lsmfile) as lsm:
        if not lsm.is_lsm:
            verbose("\n", lsm, flush=True)
            raise ValueError("not a LSM file")
        series = lsm.series[0]  # first series contains the image data
        shape = series.shape
        axes = series.axes
        dtype = series.dtype
        size = product(shape) * dtype.itemsize

        verbose("%.3f s" % (time.time() - start_time))
        # verbose(lsm, flush=True)
        verbose("Image\n  axes:  %s\n  shape: %s\n  dtype: %s\n  size:  %s"
                % (axes, shape, dtype, format_size(size)), flush=True)
        if not series.axes.endswith('TZCYX'):
            raise ValueError("not a *TZCYX LSM file")

        verbose("Copying image from LSM to BIN files", end='', flush=True)
        start_time = time.time()
        tiles = shape[-2] // tile[-2], shape[-1] // tile[-1]
        if binfile:
            binfile = binfile % (shape[-4], shape[-3], tile[0], tile[1])
        shape = (1,) * (7-len(shape)) + shape
        # cache for ZCYX stacks and output files
        data = numpy.empty(shape[3:], dtype=dtype)
        out = numpy.empty((shape[-4], shape[-3], tile[0], tile[1]),
                          dtype=dtype)
        # iterate over Tiff pages containing data
        pages = iter(series.pages)
        for m in range(shape[0]):  # mosaic axis
            for p in range(shape[1]):  # position axis
                for t in range(shape[2]):  # time axis
                    for z in range(shape[3]):  # z slices
                        data[z] = next(pages).asarray()
                    for y in range(tiles[0]):  # tile y
                        for x in range(tiles[1]):  # tile x
                            out[:] = data[...,
                                          y*tile[0]:(y+1)*tile[0],
                                          x*tile[1]:(x+1)*tile[1]]
                            if binfile:
                                out.tofile(binfile % (m, p, t, y, x))
                            verbose('.', end='', flush=True)
        verbose(" %.3f s" % (time.time() - start_time))


def imshow(data, title=None, vmin=0, vmax=None, cmap=None,
           bitspersample=None, photometric='rgb', interpolation=None,
           dpi=96, figure=None, subplot=111, maxdim=32768, **kwargs):
    """Plot n-dimensional images using matplotlib.pyplot.

    Return figure, subplot and plot axis.
    Requires pyplot already imported C{from matplotlib import pyplot}.

    Parameters
    ----------
    bitspersample : int or None
        Number of bits per channel in integer RGB images.
    photometric : {'miniswhite', 'minisblack', 'rgb', or 'palette'}
        The color space of the image data.
    title : str
        Window and subplot title.
    figure : matplotlib.figure.Figure (optional).
        Matplotlib to use for plotting.
    subplot : int
        A matplotlib.pyplot.subplot axis.
    maxdim : int
        maximum image width and length.
    kwargs : optional
        Arguments for matplotlib.pyplot.imshow.

    """
    # TODO: show photometric == 'separated' (CMYK) as RGB
    isrgb = photometric in ('rgb', 'palette')

    data = data.squeeze()
    if photometric in ('miniswhite', 'minisblack', None):
        data = reshape_nd(data, 2)
    else:
        data = reshape_nd(data, 3)

    dims = data.ndim
    if dims < 2:
        raise ValueError("not an image")
    elif dims == 2:
        dims = 0
        isrgb = False
    else:
        if isrgb and data.shape[-3] in (3, 4):
            data = numpy.swapaxes(data, -3, -2)
            data = numpy.swapaxes(data, -2, -1)
        elif not isrgb and (data.shape[-1] < data.shape[-2] // 8 and
                            data.shape[-1] < data.shape[-3] // 8 and
                            data.shape[-1] < 5):
            data = numpy.swapaxes(data, -3, -1)
            data = numpy.swapaxes(data, -2, -1)
        isrgb = isrgb and data.shape[-1] in (3, 4)
        dims -= 3 if isrgb else 2

    if isrgb:
        data = data[..., :maxdim, :maxdim, :maxdim]
    else:
        data = data[..., :maxdim, :maxdim]

    if photometric == 'palette' and isrgb:
        datamax = data.max()
        if datamax > 255:
            data = data >> 8  # possible precision loss
        data = data.astype('B')
    elif data.dtype.kind in 'ui':
        if not (isrgb and data.dtype.itemsize <= 1) or bitspersample is None:
            try:
                bitspersample = int(math.ceil(math.log(data.max(), 2)))
            except Exception:
                bitspersample = data.dtype.itemsize * 8
        elif not isinstance(bitspersample, inttypes):
            # bitspersample can be tuple, e.g. (5, 6, 5)
            bitspersample = data.dtype.itemsize * 8
        datamax = 2**bitspersample
        if isrgb:
            if bitspersample < 8:
                data = data << (8 - bitspersample)
            elif bitspersample > 8:
                data = data >> (bitspersample - 8)  # precision loss
            data = data.astype('B')
    elif data.dtype.kind == 'f':
        datamax = data.max()
        if isrgb and datamax > 1.0:
            if data.dtype.char == 'd':
                data = data.astype('f')
                data /= datamax
            else:
                data = data / datamax
    elif data.dtype.kind == 'b':
        datamax = 1
    elif data.dtype.kind == 'c':
        data = numpy.absolute(data)
        datamax = data.max()

    if not isrgb:
        if vmax is None:
            vmax = datamax
        if vmin is None:
            if data.dtype.kind == 'i':
                dtmin = numpy.iinfo(data.dtype).min
                vmin = numpy.min(data)
                if vmin == dtmin:
                    vmin = numpy.min(data > dtmin)
            if data.dtype.kind == 'f':
                dtmin = numpy.finfo(data.dtype).min
                vmin = numpy.min(data)
                if vmin == dtmin:
                    vmin = numpy.min(data > dtmin)
            else:
                vmin = 0

    pyplot = sys.modules['matplotlib.pyplot']

    if figure is None:
        pyplot.rc('font', family='sans-serif', weight='normal', size=8)
        figure = pyplot.figure(dpi=dpi, figsize=(10.3, 6.3), frameon=True,
                               facecolor='1.0', edgecolor='w')
        try:
            figure.canvas.manager.window.title(title)
        except Exception:
            pass
        l = len(title.splitlines()) if title else 1
        pyplot.subplots_adjust(bottom=0.03*(dims+2), top=0.98-l*0.03,
                               left=0.1, right=0.95, hspace=0.05, wspace=0.0)
    subplot = pyplot.subplot(subplot)

    if title:
        try:
            title = unicode(title, 'Windows-1252')
        except TypeError:
            pass
        pyplot.title(title, size=11)

    if cmap is None:
        if data.dtype.kind in 'ubf' or vmin == 0:
            cmap = 'viridis'
        else:
            cmap = 'coolwarm'
        if photometric == 'miniswhite':
            cmap += '_r'

    image = pyplot.imshow(data[(0,) * dims].squeeze(), vmin=vmin, vmax=vmax,
                          cmap=cmap, interpolation=interpolation, **kwargs)

    if not isrgb:
        pyplot.colorbar()  # panchor=(0.55, 0.5), fraction=0.05

    def format_coord(x, y):
        # callback function to format coordinate display in toolbar
        x = int(x + 0.5)
        y = int(y + 0.5)
        try:
            if dims:
                return "%s @ %s [%4i, %4i]" % (cur_ax_dat[1][y, x],
                                               current, y, x)
            else:
                return "%s @ [%4i, %4i]" % (data[y, x], y, x)
        except IndexError:
            return ''

    def none(event):
        return ''

    subplot.format_coord = format_coord
    image.get_cursor_data = none
    image.format_cursor_data = none

    if dims:
        current = list((0,) * dims)
        cur_ax_dat = [0, data[tuple(current)].squeeze()]
        sliders = [pyplot.Slider(
            pyplot.axes([0.125, 0.03*(axis+1), 0.725, 0.025]),
            'Dimension %i' % axis, 0, data.shape[axis]-1, 0, facecolor='0.5',
            valfmt='%%.0f [%i]' % data.shape[axis]) for axis in range(dims)]
        for slider in sliders:
            slider.drawon = False

        def set_image(current, sliders=sliders, data=data):
            # change image and redraw canvas
            cur_ax_dat[1] = data[tuple(current)].squeeze()
            image.set_data(cur_ax_dat[1])
            for ctrl, index in zip(sliders, current):
                ctrl.eventson = False
                ctrl.set_val(index)
                ctrl.eventson = True
            figure.canvas.draw()

        def on_changed(index, axis, data=data, current=current):
            # callback function for slider change event
            index = int(round(index))
            cur_ax_dat[0] = axis
            if index == current[axis]:
                return
            if index >= data.shape[axis]:
                index = 0
            elif index < 0:
                index = data.shape[axis] - 1
            current[axis] = index
            set_image(current)

        def on_keypressed(event, data=data, current=current):
            # callback function for key press event
            key = event.key
            axis = cur_ax_dat[0]
            if str(key) in '0123456789':
                on_changed(key, axis)
            elif key == 'right':
                on_changed(current[axis] + 1, axis)
            elif key == 'left':
                on_changed(current[axis] - 1, axis)
            elif key == 'up':
                cur_ax_dat[0] = 0 if axis == len(data.shape)-1 else axis + 1
            elif key == 'down':
                cur_ax_dat[0] = len(data.shape)-1 if axis == 0 else axis - 1
            elif key == 'end':
                on_changed(data.shape[axis] - 1, axis)
            elif key == 'home':
                on_changed(0, axis)

        figure.canvas.mpl_connect('key_press_event', on_keypressed)
        for axis, ctrl in enumerate(sliders):
            ctrl.on_changed(lambda k, a=axis: on_changed(k, a))

    return figure, subplot, image


def _app_show():
    """Block the GUI. For use as skimage plugin."""
    pyplot = sys.modules['matplotlib.pyplot']
    pyplot.show()


def askopenfilename(**kwargs):
    """Return file name(s) from Tkinter's file open dialog."""
    try:
        from Tkinter import Tk
        import tkFileDialog as filedialog
    except ImportError:
        from tkinter import Tk, filedialog
    root = Tk()
    root.withdraw()
    root.update()
    filenames = filedialog.askopenfilename(**kwargs)
    root.destroy()
    return filenames


def main(argv=None):
    """Command line usage main function."""
    if float(sys.version[0:3]) < 2.7:
        print("This script requires Python version 2.7 or better.")
        print("This is Python version %s" % sys.version)
        return 0
    if argv is None:
        argv = sys.argv

    import optparse  # TODO: use argparse

    parser = optparse.OptionParser(
        usage="usage: %prog [options] path",
        description="Display image data in TIFF files.",
        version="%%prog %s" % __version__)
    opt = parser.add_option
    opt('-p', '--page', dest='page', type='int', default=-1,
        help="display single page")
    opt('-s', '--series', dest='series', type='int', default=-1,
        help="display series of pages of same shape")
    opt('--nomultifile', dest='nomultifile', action='store_true',
        default=False, help="do not read OME series from multiple files")
    opt('--noplots', dest='noplots', type='int', default=8,
        help="maximum number of plots")
    opt('--interpol', dest='interpol', metavar='INTERPOL', default='bilinear',
        help="image interpolation method")
    opt('--dpi', dest='dpi', type='int', default=96,
        help="plot resolution")
    opt('--vmin', dest='vmin', type='int', default=None,
        help="minimum value for colormapping")
    opt('--vmax', dest='vmax', type='int', default=None,
        help="maximum value for colormapping")
    opt('--debug', dest='debug', action='store_true', default=False,
        help="raise exception on failures")
    opt('--doctest', dest='doctest', action='store_true', default=False,
        help="runs the docstring examples")
    opt('-v', '--verbose', dest='verbose', action='store_true', default=True)
    opt('-q', '--quiet', dest='verbose', action='store_false')

    settings, path = parser.parse_args()
    path = ' '.join(path)

    if settings.doctest:
        import doctest
        doctest.testmod(optionflags=doctest.ELLIPSIS)
        return 0
    if not path:
        path = askopenfilename(title="Select a TIFF file",
                               filetypes=CONST.TIFF_FILEOPEN_TYPES)
        if not path:
            parser.error("No file specified")

    if any(i in path for i in '?*'):
        path = glob.glob(path)
        if not path:
            print('no files match the pattern')
            return 0
        # TODO: handle image sequences
        path = path[0]

    print("\nReading file structure...", end=' ')
    start = time.time()
    try:
        tif = TiffFile(path, multifile=not settings.nomultifile)
    except Exception as e:
        if settings.debug:
            raise
        else:
            print("\n", e)
            sys.exit(0)
    print("%.3f ms" % ((time.time()-start) * 1e3))

    if tif.is_ome:
        settings.norgb = True

    images = []
    if settings.noplots > 0:
        print("Reading image data... ", end=' ')

        def notnone(x):
            return next(i for i in x if i is not None)

        start = time.time()
        try:
            if settings.page >= 0:
                images = [(tif.asarray(key=settings.page),
                           tif[settings.page], None)]
            elif settings.series >= 0:
                images = [(tif.asarray(series=settings.series),
                           notnone(tif.series[settings.series].pages),
                           tif.series[settings.series])]
            else:
                images = []
                for i, s in enumerate(tif.series[:settings.noplots]):
                    try:
                        images.append((tif.asarray(series=i),
                                       notnone(s.pages),
                                       tif.series[i]))
                    except ValueError as e:
                        images.append((None, notnone(s.pages), None))
                        if settings.debug:
                            raise
                        else:
                            print("\n* series %i failed: %s... " % (i, e),
                                  end='')
            print("%.3f ms" % ((time.time()-start) * 1e3))
        except Exception as e:
            if settings.debug:
                raise
            else:
                print(e)

    tif.close()
    print()
    print(tif.info())
    print()

    if images and settings.noplots > 0:
        try:
            import matplotlib
            matplotlib.use('TkAgg')
            from matplotlib import pyplot
        except ImportError as e:
            warnings.warn("failed to import matplotlib.\n%s" % e)
        else:
            for img, page, series in images:
                if img is None:
                    continue
                vmin, vmax = settings.vmin, settings.vmax
                if 'gdal_nodata' in page.tags:
                    try:
                        vmin = numpy.min(img[img > float(page.gdal_nodata)])
                    except ValueError:
                        pass
                if page.is_stk:
                    try:
                        vmin = page.stk_metadata['min_scale']
                        vmax = page.stk_metadata['max_scale']
                    except KeyError:
                        pass
                    else:
                        if vmax <= vmin:
                            vmin, vmax = settings.vmin, settings.vmax
                if series:
                    title = "%s\n%s\n%s" % (str(tif), str(page), str(series))
                else:
                    title = "%s\n %s" % (str(tif), str(page))
                photometric = page.photometric
                if photometric == 'palette' and not page.is_indexed:
                    photometric = 'minisblack'
                imshow(img, title=title, vmin=vmin, vmax=vmax,
                       bitspersample=page.bits_per_sample,
                       photometric=photometric,
                       interpolation=settings.interpol,
                       dpi=settings.dpi)
            pyplot.show()


if sys.version_info[0] == 2:
    inttypes = int, long  # noqa

    def print_(*args, **kwargs):
        """Print function with flush support."""
        flush = kwargs.pop('flush', False)
        print(*args, **kwargs)
        if flush:
            sys.stdout.flush()

    def bytes2str(b, encoding=None):
        """Return string from bytes."""
        return b

    def str2bytes(s, encoding=None):
        """Return bytes from string."""
        return s

    def byte2int(b):
        """Return value of byte as int."""
        return ord(b)

    class FileNotFoundError(IOError):
        pass

    TiffFrame = TiffPage  # noqa
else:
    inttypes = int
    basestring = str, bytes
    unicode = str
    print_ = print

    def bytes2str(b, encoding='cp1252'):
        """Return unicode string from bytes."""
        return str(b, encoding)

    def str2bytes(s, encoding='cp1252'):
        """Return bytes from unicode string."""
        return s.encode(encoding)

    def byte2int(b):
        """Return value of byte as int."""
        return b

if __name__ == "__main__":
    sys.exit(main())