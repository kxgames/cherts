#!/usr/bin/env python3

import os

file_pairs = {
        'Chess_bdt45.svg': 'piece_bdt45.png',
        'Chess_blt45.svg': 'piece_blt45.png',
        'Chess_kdt45.svg': 'piece_kdt45.png',
        'Chess_klt45.svg': 'piece_klt45.png',
        'Chess_ndt45.svg': 'piece_ndt45.png',
        'Chess_nlt45.svg': 'piece_nlt45.png',
        'Chess_pdt45.svg': 'piece_pdt45.png',
        'Chess_plt45.svg': 'piece_plt45.png',
        'Chess_qdt45.svg': 'piece_qdt45.png',
        'Chess_qlt45.svg': 'piece_qlt45.png',
        'Chess_rdt45.svg': 'piece_rdt45.png',
        'Chess_rlt45.svg': 'piece_rlt45.png',
}

for infile, outfile in file_pairs.items():
    cmd = f"inkscape --export-png=../{outfile} --export-area-page {infile}"
    os.system(cmd)

