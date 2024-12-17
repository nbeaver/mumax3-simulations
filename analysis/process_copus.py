#! /usr/bin/env python3

def parse_line(line_raw):
    """
    Parse a single line of mumax3 output file.
    """
    line_raw = line_raw.strip() # remove whitespace
    if '//' in line_raw:
        line, comment = line_raw.split('//', 1)
    else:
        line = line_raw
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
    names = ["f", "bstat", "amp", "alpha", "Ku1", "Aex", "Msat", "tstep", "save_step", "Nx", "Ny", "Nz", "c", "d"]
    ops = ['=', ':=']
    p = {}
    for i, line in enumerate(lines):
        if line.strip().startswith('for '):
            # Skip for loop lines
            continue
        if line.strip().startswith('// '):
            # Skip lines that are just comments.
            continue
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