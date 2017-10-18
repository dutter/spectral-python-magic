import os
import sys
import re
import numpy as np
import pandas
from scipy import signal
from scipy import optimize
from functools import partial
import multiprocessing
from czifile import CziFile as cziutils
import tifffile


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Linear unmixing: this project works in "kit" format:
# takes raw images from 'input', processes via xls reference spectra in 'reference', outputs tif stacks into 'output'
#
# The code should detect which laser(s) used from the czi metadata and choose the appropriate reference set
#
# If using single lasers, channel-selects based on in-code 'channelSelector' dict - EDIT THIS BY HAND!
#
# Physical pixel size should be embedded in metadata for use in ImageJ 
#
# Options you might want to change are at the start of the final block (starts with "if __name__=='__main__':")
#
# Code originally written in MATLAB by Blair Rossetti, ported to Python 3.x.x by Daniel Utter & Steven Wilbert
# Last edited 2017.10.17
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def loadImage(cziFile):
    with cziutils(cziFile) as czi:
        meta = czi.metadata
        spectral = meta.find('.//SubType').text

        # CZI metadata has lasers used as value of <Wavelength> under block(s) <LightSourceSettings>
        lightsourcesettings = [source for source in meta.findall('.//LightSourceSettings')]
        lasers = sorted(list(set([round(float(source.find('.//Wavelength').text)) for source in lightsourcesettings])))

        print("  Excitation laser(s) identified from czi metadata: " + ', '.join([str(l) for l in lasers]))

        # ET.dump(meta)  # this prints out ALL metadata xml as raw text

        numBands = int(meta.find('.//SizeC').text)
        scaleX = float(meta.find('.//ScalingX').text)
        scaleY = float(meta.find('.//ScalingY').text)
        x = int(meta.find('.//SizeX').text)
        y = int(meta.find('.//SizeY').text)

        # check for z stack - if Z doesn't exist, assume 1
        try:
            z = int(meta.find('.//SizeZ').text)
        except AttributeError:
            z = 1

        if "Spectral" not in spectral:
            sys.exit('This file is not spectral!')

        # warn user of how many spectral bins found
        print("  " + str(numBands) + " lambda bins found")


        rawImage = czi.asarray(max_workers=numCores)
        #        f, t, b, z, x, y, n = list(rawImage.shape)
        return rawImage, x, y, z, numBands, lasers, scaleX, scaleY


def processImage(rawImage, referenceMatrix, x, y, zplane, numBands):
    # get number of channels to unmix into
    numChannels = len(referenceMatrix.columns.values)

    # slice appropriate z
    if len(rawImage.shape) == 8:
        rawImage = rawImage[:, :, :, :, zplane, :, :, :]
    else:
        rawImage = rawImage[:, :, :, zplane, :, :, :]
    # Remove extraneous dimensions to be Bands x X x Y
    czi3d = np.reshape(rawImage, (numBands, x, y))

    # median filter
    if medianFilter:
        czi3d = signal.medfilt(volume=czi3d, kernel_size=[1, 3, 3])

    # collapse xy wide
    N = x * y
    czi2d = np.reshape(czi3d, (numBands, N))
    return czi2d, N, numChannels


# do the unmixing - parallel style
def parUnmix(referenceMatrix, czi2d, x, y, N, numChannels, numCores):  # twice as fast using 7 processors!
    pool = multiprocessing.Pool(processes=numCores)
    solution = pool.map(partial(optimize.nnls, referenceMatrix), [czi2d[:, pix] for pix in range(N)])
    pool.close()
    pool.join()

    # parse it out - simple concatenation
    unmixed = np.reshape(np.array(solution), (N, 2))[:, 0]
    unmixed = np.stack(unmixed, axis=1)

    # convert to 3d - order='A' needed in reshape to recreate original pixel order
    unmixed = np.reshape(unmixed, (numChannels, x, y), order='A')

    unmixed = unmixed.astype('uint16')
    return unmixed


def serUnmix(referenceMatrix, czi2d, x, y, N, numChannels):
    # make new dataframe for output to be in
    unmixed = np.zeros((numChannels, N), 'uint16')
    for pix in range(N):
        unmixed[:, pix] = optimize.nnls(referenceMatrix, czi2d[:, pix])[0]

    unmixed = np.reshape(unmixed, (numChannels, x, y))

    return unmixed


if __name__=='__main__':

    # ! # ! # DEFAULTS YOU MIGHT WANT TO CHANGE (or at least check)
    numCores = os.cpu_count() - 1
    inputDirName = 'input'
    outputDirName = 'output'
    referenceDirName = 'reference'
    medianFilter = True  # this does the 3-pixel median BEFORE unmixing, 'False' does no filtering

    channelSelector = {
        "405": ["AF", "PacBlue", "At425"],
        "488": ["Dy490", "Lx514"],
        "514": ["At532"],
        "561": ["At550", "RRX"],
        "594": ["TRX", "At594"],
        "633": ["At620", "At647", "At655"]
    }


    # ! # ! # END OF LIKELY CHANGES

    # get main kit location
    curDir = os.path.dirname(os.path.abspath(__file__))

    # set working dir paths
    inputDir = curDir + '/' + inputDirName + '/'
    referenceDir = curDir + '/' + referenceDirName + '/'
    outputDir = curDir + '/' + outputDirName + '/'

    # read in reference file
    singleShot = False
    referenceFiles = [s for s in os.listdir(referenceDir) if 'xls' in s]
    if len(referenceFiles) > 1:
        print('Found multiple reference spectra so processing all input as multiple single-laser shots!')
        singleShot = True


    # get list of files to process
    imagesToProcess = os.listdir(inputDir)
    if imagesToProcess[0].startswith(".DS_Store"):  # sometimes python gets confused and reads DS_Store file
        del imagesToProcess[0]

    for image in imagesToProcess:
        print("Processing " + image)
        imPath = inputDir + image

        rawImage, x, y, z, numBands, lasers, scaleX, scaleY = loadImage(imPath)
        # set scale - scaleX from czi is size per pixel in cm, tifffile/imageJ wants num pixels per micron
        physicalWidth = int(1/(100*scaleX))
        physicalHeight = int(1/(100*scaleY))

        # determine which reference file to use
        if singleShot:
            referenceFile = referenceDir + [ref for ref in referenceFiles if str(lasers[0]) in ref][0]
            # parse the filename to get just the core part, for the output filename
            image = '_'.join([part for part in image.split('_') if str(lasers[0]) not in part])
        else:
            referenceFile = referenceDir + referenceFiles[0]

        # read in reference matrix
        referenceMatrix = pandas.read_excel(referenceFile)

        # iterate through z stack
        for zed in range(z):
            print("  On plane " + str(zed + 1) + " of " + str(z))
            czi2d, N, numChannels = processImage(rawImage, referenceMatrix, x, y, zed, numBands)

            # if only one core requested:
            if numCores is 1:
                unmixed = serUnmix(referenceMatrix, czi2d, x, y, numChannels)
            else:
                unmixed = parUnmix(referenceMatrix, czi2d, x, y, N, numChannels, numCores)

            newName = re.sub(".czi$", "-unmixed.tif", image)
            imPathOut = outputDir + newName

            # if single, need to figure out which channels, and then concatenate ome's
            if singleShot:

                selectChannels = [i for i, v in enumerate(referenceMatrix.columns.values)
                                  if any(m in v for m in channelSelector[str(lasers[0])])]
                channelsCurrent = len(channelSelector[str(lasers[0])])

                print("  Keeping channels " + ', '.join(channelSelector[str(lasers[0])]) +
                      " from laser " + str(lasers[0]))

                # Select channels appropriate for this laser
                unmixed = unmixed[selectChannels, :, :]

                # append all shots into one tiff (need minisblack in case first laser has 3 ch and it thinks RGB)
                tifffile.imsave(file=imPathOut, data=unmixed, append=True, photometric='minisblack',
                                resolution=(physicalWidth, physicalHeight, 'cm'))
            else:
                # Just save
                tifffile.imsave(file=imPathOut, data=unmixed, append=True, photometric='minisblack',
                                resolution=(physicalWidth, physicalHeight, 'cm'))

            print('  Done! Unmixed image: ' + imPathOut)



