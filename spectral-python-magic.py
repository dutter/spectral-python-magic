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

# # # # # # # # # # # # # # # # # # # # # #
# Linear unmixing: this project works in "kit" format:
# takes raw images from 'input', processes via xls reference spectra in 'reference', outputs tif stacks into 'output'
#
# Options you might want to change are at the start of the final block (starts with "if __name__=='__main__':")
#
# Code originally written in MATLAB by Blair Rossetti, ported to Python 3.x.x by Daniel Utter & Steven Wilbert
# Last edited 2017.09.13
# # # # # # # # # # # # # # # # # # # # # #


def loadImage(cziFile):
    with cziutils(cziFile) as czi:
        meta = czi.metadata
        spectral = meta.find('.//SubType').text

        numBands = int(meta.find('.//SizeC').text)
        x = int(meta.find('.//SizeX').text)
        y = int(meta.find('.//SizeY').text)

        if "Spectral" not in spectral:
            sys.exit('This file is not spectral!')
        if 32 != numBands:
            sys.exit('There are only ' + str(numBands) + ' spectral bins, expected 32!')

        # should we hunt for excitation laser?

        rawImage = czi.asarray(max_workers=numCores)
        #        f, t, b, z, x, y, n = list(rawImage.shape)
        return rawImage, x, y, numBands


def processImage(rawImage, referenceMatrix, x, y, numBands):
    # get number of channels to unmix into
    numChannels = len(referenceMatrix.columns.values)

    # Remove extraneous dimensions to be bands x X x Y
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

    unmixed = unmixed.astype('uint32')
    return unmixed


def serUnmix(referenceMatrix, czi2d, x, y, N, numChannels):
    # make new dataframe for output to be in
    unmixed = np.zeros((numChannels, N), 'uint32')
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
    # ! # ! # END OF LIKELY CHANGES

    # get main kit location
    curDir = os.path.dirname(os.path.abspath(__file__))

    # set working dir paths
    inputDir = curDir + '/' + inputDirName + '/'
    referenceDir = curDir + '/' + referenceDirName + '/'
    outputDir = curDir + '/' + outputDirName + '/'

    # read in reference file
    referenceFile = [s for s in os.listdir(referenceDir) if 'xls' in s]
    if len(referenceFile) > 1:
        sys.exit('There are more than two files in ' + referenceDir + ' and it is confusing me!')

    referenceFile = referenceDir + referenceFile[0]
    referenceMatrix = pandas.read_excel(referenceFile)

    # get list of files to process
    imagesToProcess = os.listdir(inputDir)

    for image in imagesToProcess:
        print("Processing " + image)
        imPath = inputDir + image

        rawImage, x, y, numBands = loadImage(imPath)
        czi2d, N, numChannels = processImage(rawImage, referenceMatrix, x, y, numBands)

        # if only one core requested:
        if numCores is 1:
            unmixed = serUnmix(referenceMatrix, czi2d, x, y, numChannels)
        else:
            unmixed = parUnmix(referenceMatrix, czi2d, x, y, N, numChannels, numCores)

        # set output name and save
        newName = re.sub(".czi$", "-unmixed.tif", image)
        imPathOut = outputDir + newName
        tifffile.imsave(file=imPathOut, data=unmixed)

        print('Unmixed image stack saved as: ' + imPathOut)
        #saveUnmixed(unmixed, imPathOut)



