import os
import sys
import struct
import scipy
import scipy.misc
import scipy.cluster
from PIL import Image

# original code from:
# http://stackoverflow.com/questions/3241929/python-find-dominant-most-common-color-in-an-image/3244061#3244061

NUM_CLUSTERS = 5

def colorAsHex(color):
    return ''.join(chr(c) for c in color).encode('hex')

def findDominantColor(imgpath, cluster_count=NUM_CLUSTERS):
    # load image
    im = Image.open(imgpath)
    im = im.resize((150, 150))      # optional, to reduce time

    # remove tmp file
    os.remove(imgpath)

    # convert image to RGB
    if im.mode == 'P':
        im.putalpha(0)
    if im.mode == 'RGBA':
        om = im
        im = Image.new("RGB", om.size, (255, 255, 255))
        im.paste(om, mask=om.split()[3])

    # get color data array
    ar = scipy.misc.fromimage(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2])
    ar = ar.astype(float)

    # run clusters
    codes, dist = scipy.cluster.vq.kmeans(ar, cluster_count)
    vecs, dist = scipy.cluster.vq.vq(ar, codes)
    counts, bins = scipy.histogram(vecs, len(codes))

    # find most saturated color (least grey)
    maxgap = 0
    peak = None
    for i, code in enumerate(codes):
        truncCode = code.astype(int)
        gap = max(abs(truncCode[1]-truncCode[0]),
                  abs(truncCode[2]-truncCode[1]),
                  abs(truncCode[2]-truncCode[0]))
        if gap > maxgap:
            maxgap = gap
            peak = colorAsHex(truncCode)

    # collect alternatives
    alternatives = []
    for i, code in enumerate(codes):
        colorCode = colorAsHex(code.astype(int))
        if colorCode != peak:
            alternatives.append(colorCode)

    # return colors
    return {'color': peak,
            'alternatives': alternatives}

def main():
    if not os.path.isfile(sys.argv[1]):
        print 'path is not a file: '+sys.argv[1]
        exit(1)

    color = findDominantColor(sys.argv[1], cluster_count=5)
    print 'dominant color is #%s' % color

if __name__ == '__main__':
    main()
