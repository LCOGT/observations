# -*- coding: utf-8 -*-
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

def parse_frames_list(frames):
    '''
    Parse frames from Archive API, filtering ones which have groups of 3 colours
    Returns a list of block IDs with appropriate frames, filters and URLs
    '''
    colour_set = []
    blks = set([r['BLKUID'] for r in frames])
    blks_set = { bid: [] for bid in blks}
    for frame in frames:
        params = {'filter':frame['FILTER'], 'url' : frame['url']}
        blks_set[frame['BLKUID']].append(params)
    for k, v in blks_set:
        if len(v) == 3:
            colour_set.append({'block' : k, 'frames' : v})
    return colour_set
