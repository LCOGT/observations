'''
Observations: Open access archive app for Las Cumbres Observatory Global Telescope Network
Copyright (C) 2014-2015 LCOGT

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

from astropy.io import fits
from astroscrappy import detect_cosmics
import PIL.Image as pli
from PIL import ImageFont, ImageDraw
import numpy as np
import alipy
import glob
import logging
import sys, os
import argparse
import tempfile
import shutil
import subprocess
import requests
import logging

from django.conf import settings

logger = logging.getLogger('imager')


def parse_frames_list(frames):
    '''
    Parse frames from Archive API, filtering ones which have groups of 3 colours
    Returns a list of block IDs with appropriate frames files, filters and URLs
    '''
    colour_set = []
    blks = set([r['BLKUID'] for r in frames])
    blks_set = { bid: [] for bid in blks}
    for frame in frames:
        params = {'filter':frame['FILTER'], 'url' : frame['url'], 'filename' : frame['filename']}
        blks_set[frame['BLKUID']].append(params)
    for k, v in blks_set.items():
        if len(v) == 3:
            colour_set.append({'block' : k, 'frames' : v})
    return colour_set

def remove_cr(data):
    '''
    Removes high value pixels which are presumed to be cosmic ray hits.
    '''
    m, imdata = detect_cosmics(data, readnoise=20., gain=1.4, sigclip=5., sigfrac=.5, objlim=6.)
    return imdata

def clean_data(data):
    '''
    - Remove bogus (i.e. negative) pixels
    - Remove Cosmic Rays
    - Find the 99.5% percentile and remove everything above that
    - Subtract the median sky value
    - Scale the images in the range for JPEG
    '''
    # Level out the colour balance in the frames
    logging.warning('--- Begin CR removal ---')
    median = np.median(data)
    data[data<0.]=median
    # Run astroScrappy to remove pesky cosmic rays
    data = remove_cr(data)
    logging.warning('Median=%s' % median)
    logging.warning('Max after median=%s' % data.max())
    return data


def scale_data(data, i):
    # Recalculate the median
    logging.warning('--- Begin Scaling ---')
    data[data<0.]=0.
    median = np.median(data)
    data-= median
    data[data<0.]=0.
    sc_data= data #np.arcsinh(data)
    max_val = np.percentile(sc_data,99.5)
    logging.warning('99.5 =%s' % max_val)
    scaled = sc_data*255./(max_val)
    scaled[scaled>255.]=255.
    logging.warning('Median of scaled=%s' % np.median(scaled))
    logging.warning('Min scaled=%s' % scaled.min())
    return scaled

def select_images(frames):
    ref_image = frames[0]
    hdr = fits.getheader(ref_image, 1)
    objectname = hdr['OBJECT'].strip().replace(' ','_')
    filename = '%s-%s.jpg' % (objectname, hdr['REQNUM'])
    return ref_image, frames, filename

def read_aligned(filelist):
    # Scale the images
    rgb_list =[]
    for i, file_in in enumerate(filelist):
        data, hdrs = fits.getdata(file_in, header=True)
        data = clean_data(data)
        data = scale_data(data, i)
        logging.warning('Shape of %s %s' % (file_in, str(data.shape)))
        rgb_list.append(data)
    return rgb_list

def read_write_data(filelist):
    '''
    Overwrite FITS files with cleaned and scaled data
    - Data is read into uncompressed FITS file to remove dependency on FPack
    '''
    img_list =[]
    for i, file_in in enumerate(filelist):
        data, hdrs = fits.getdata(file_in, header=True)
        data = clean_data(data)
        # data = scale_data(data, i)
        logging.warning('Shape of %s %s' % (file_in, str(data.shape)))
        new_filename = file_in.split('.')[0] + "_c.fits"
        hdu = fits.PrimaryHDU(data, header=hdrs)
        hdu.writeto(new_filename)
        img_list.append(str(new_filename))

    return img_list


def create_colour_stiff(img_list, filename='test.jpg'):
    resp = subprocess.call(['stiff']+img_list)
    if resp == 0:
        resp = subprocess.call(['convert', '-quality','70%', '-resize','1500', 'stiff.tif', filename])

    return True


def reproject_files(ref_image, images_to_align, tmpdir='temp/'):
    identifications = alipy.ident.run(ref_image, images_to_align[1:3], visu=False)
    outputshape = alipy.align.shape(ref_image)

    for id in identifications:
        if id.ok:
            alipy.align.affineremap(id.ukn.filepath, id.trans, shape=outputshape, makepng=True, outdir=tmpdir)

    aligned_images = sorted(glob.glob(tmpdir+"/*_affineremap.fits"))

    img_list = [ref_image]+aligned_images

    return img_list

def download_frames(frames, tmpdir, feedback=False):
    file_list = []
    for frame in frames['frames']:
        file_name = os.path.join(tmpdir,frame['filename'])
        with open(file_name, "wb") as f:
            logger.info("Downloading %s" % file_name)
            response = requests.get(frame['url'], stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None: # no content length header
                f.write(response.content)
            elif not feedback:
                # We don't want any console feedback on progress
                for data in response.iter_content():
                    f.write(data)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content():
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                    sys.stdout.flush()
        file_list.append(file_name)

    return file_list

def run_colour_imager(frames, args):
    tmpdir = tempfile.mkdtemp()
    frame_files = download_frames(frames=frames, tmpdir=tmpdir, feedback=args.feedback)

    ref_image, images_to_align, filename = select_images(frames=frame_files)

    img_list = read_write_data(images_to_align)
    img_list = reproject_files(img_list[0], img_list, tmpdir)
    resp = create_colour_stiff(img_list, filename)

    # Remove the temporary files
    shutil.rmtree(tmpdir)
    if resp:
        return filename
    else:
        return resp
