#! /usr/bin/env python3

#import matplotlib.pyplot as plt
import sys
import argparse
import numpy as np
import glob
import os
import scipy.io
import logging
logger = logging.getLogger(__name__)

class MyInfo:
    # Give names of class members.
    def __repr__(self):
        return self.__class__.__name__ + '(' + str(list(self.__dict__.keys())) + ')'
    def __str__(self):
        return self.__class__.__name__ + '(' + str(list(self.__dict__.keys())) + ')'

def parse_line(line):
    if ':=' in line:
        try:
            name_raw, val_raw = line.split(':=')
        except ValueError:
            print("failed on line: '{}'".format(line))
            raise
    elif '=' in line:
        try:
            name_raw, val_raw = line.split('=')
        except ValueError:
            print("failed on line: '{}'".format(line))
            raise
    else:
        raise ValueError("no '=' or ':=' in line: '{}'".format(line))
    name = name_raw.strip() # remove whitespace
    val_str = val_raw.strip()
    val = float(val_str)
    return name, val

def parse_logfile(lines):
    names = ["f", "bstat", "amp", "alpha", "Ku1", "Aex", "Msat", "tstep", "save_step"]
    ops = ['=', ':=']
    p = {}
    for i, line in enumerate(lines):
        if any([line.startswith(name) for name in names]) and any([op in line for op in ops]):
            try:
                name, val = parse_line(line)
            except:
                sys.stderr.write("failed on line #{}\n".format(i))
                raise
            if name in p:
                raise ValueError("duplicate value for '{}': '{}', '{}'".format(name, val, p[name]))
            else:
                p[name] = val
    return p


def readable_directory(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            'not an existing directory: {}'.format(path))
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError(
            'not a readable directory: {}'.format(path))
    return path


def writable_directory(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            'not an existing directory: {}'.format(path))
    if not os.access(path, os.W_OK):
        raise argparse.ArgumentTypeError(
            'not a writable directory: {}'.format(path))
    return path

def process_mumax_out(read_dir, write_dir):
    logging.debug("read_dir = '{}'".format(read_dir))
    logging.debug("write_dir = '{}'".format(write_dir))
    read_dir_norm = os.path.normpath(read_dir)
    write_dir_norm = os.path.normpath(write_dir)
    parent_dir, read_filename = os.path.split(read_dir_norm)
    logging.debug("parent_dir = '{}'".format(parent_dir))
    logging.debug("read_filename = '{}'".format(read_filename))
    outfile_prefix, ext = os.path.splitext(read_filename)
    logging.debug("outfile_prefix = '{}'".format(outfile_prefix))
    logging.debug("ext = '{}'".format(ext))
    #assert ext == '.out'
    logpath = os.path.join(read_dir, 'log.txt')
    logging.debug("logpath = '{}'".format(logpath))
    with open(logpath) as fp:
        params = parse_logfile(fp.readlines())
    logging.debug("params = '{}'".format(params))
    if 'save_step' in params:
        # Need to do this to be compatible with both versions of the mumax3 input files.
        tstep = params['save_step']
    else:
        tstep = params['tstep']
    Msat = params['Msat']
    npy_files = glob.glob(os.path.join(read_dir, 'm_full*.npy'))
    logging.debug("len(npy_files) = '{}'".format(len(npy_files)))
    cells_list = MyInfo()
    cells_list.x = []
    cells_list.y = []
    cells_list.z = []
    for i, filepath in enumerate(npy_files):
        dat_raw = np.load(filepath)
        dat = np.squeeze(dat_raw)
        cells_list.x.append(dat[0])
        cells_list.y.append(dat[1])
        cells_list.z.append(dat[2])
        del dat_raw, dat
    del i, filepath
    cells = MyInfo()
    cells.x = np.stack(cells_list.x)
    cells.y = np.stack(cells_list.y)
    cells.z = np.stack(cells_list.z)
    del cells_list
    nt, nx, ny = cells.z.shape
    reshape = MyInfo()
    fft = MyInfo()
    fft_avg = MyInfo()

    # x
    reshape.x = np.zeros((nx, ny, nt))
    for i in range(nx):
        for j in range(ny):
            reshape.x[i][j] = cells.x[:, i, j]
    del cells.x
    fft.x = np.zeros((nx, ny, nt), dtype=np.complex128)
    for i in range(nx):
        for j in range(ny):
            fft.x[i][j] = np.fft.fft(reshape.x[i][j]/Msat)
    del reshape.x
    fft_avg.x = np.abs(fft.x).mean((0,1))
    del fft.x

    # y
    reshape.y = np.zeros((nx, ny, nt))
    for i in range(nx):
        for j in range(ny):
            reshape.y[i][j] = cells.y[:, i, j]
    del cells.y
    fft.y = np.zeros((nx, ny, nt), dtype=np.complex128)
    for i in range(nx):
        for j in range(ny):
            fft.y[i][j] = np.fft.fft(reshape.y[i][j]/Msat)
    del reshape.y
    fft_avg.y = np.abs(fft.y).mean((0,1))
    del fft.y

    # z
    reshape.z = np.zeros((nx, ny, nt))
    for i in range(nx):
        for j in range(ny):
            reshape.z[i][j] = cells.z[:, i, j]
    del cells.z
    del cells
    fft.z = np.zeros((nx, ny, nt), dtype=np.complex128)
    for i in range(nx):
        for j in range(ny):
            fft.z[i][j] = np.fft.fft(reshape.z[i][j]/Msat)
    del reshape.z
    fft_avg.z = np.abs(fft.z).mean((0,1))
    del fft.z

    del reshape
    del fft

    fft_freq_Hz = np.fft.fftfreq(nt)/tstep

    ns = 1e-9
    t_ns = np.linspace(0, tstep*nt, nt)/ns
    mat_dict_avg = {
        "fftx_avg": fft_avg.x,
        "ffty_avg": fft_avg.y,
        "fftz_avg": fft_avg.z,
        "folder": read_dir,
        'fft_freq_Hz': fft_freq_Hz,
        't_ns': t_ns,
    }
    mat_dict_avg.update(params)
    outpath_mat = os.path.join(write_dir_norm, outfile_prefix + "_fft_avg.mat")
    logging.debug("outpath_mat = '{}'".format(outpath_mat))
    scipy.io.savemat(
        outpath_mat,
        mat_dict_avg,
        long_field_names=True,
        do_compression=True,
    )

def main():
    parser = argparse.ArgumentParser(
        description='Average mumax3 output.',
        )
    parser.add_argument(
        'read_dir', type=readable_directory, help='Directory to read from.')
    parser.add_argument(
        'write_dir', type=writable_directory, help='Directory to write to.')
    # https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    parser.add_argument(
        '-v',
        '--verbose',
        help='More verbose logging',
        dest="loglevel",
        default=logging.WARNING,
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        '-d',
        '--debug',
        help='Enable debugging logs',
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logger.setLevel(args.loglevel)

    logging.debug("args.read_dir = '{}'".format(args.read_dir))
    logging.debug("args.write_dir = '{}'".format(args.write_dir))

    process_mumax_out(args.read_dir, args.write_dir)

if __name__ == '__main__':
    main()
