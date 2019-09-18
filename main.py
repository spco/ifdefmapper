import sys
import os
import itertools

ifdefs = []
ifndefs = []
endifs = []
elifs = []
elseifs = []
ifdefineds = []


def combine(args):
    whole_list = list(itertools.chain([b for a in args for b in a]))
    return sorted(whole_list, key=lambda tup: tup[2])


def get_x_from_file_y(x, y):
    """
    Extract all tuples in x that have y as their filename in the second element
    :param x: list of tuples
    :param y: filename
    :return: list of tuples
    """
    l = []
    for line in x:
        if line[1] == y:
            l.append(line)
    return l


def count_and_capture_ifdefs(line, file, line_number):
    if line.strip().startswith('#ifdef'):
        ifdefs.append((line, file, line_number))


def count_and_capture_ifndefs(line, file, line_number):
    if line.strip().startswith('#ifndef'):
        ifndefs.append((line, file, line_number))


def count_and_capture_endifs(line, file, line_number):
    if line.strip().startswith('#endif'):
        endifs.append((line, file, line_number))


def count_and_capture_elifs(line, file, line_number):
    if line.strip().startswith('#elif'):
        elifs.append((line, file, line_number))


def count_and_capture_elseifs(line, file, line_number):
    if line.strip().startswith('#elseif'):
        elseifs.append((line, file, line_number))


def count_and_capture_ifdefineds(line, file, line_number):
    if line.strip().startswith('#if defined'):
        ifdefineds.append((line, file, line_number))


def get_all_cpp_beneath(root):
    file_list = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith('.cpp'):
                file_list.append(os.path.join(path, name))
    return file_list


def get_all_directives_in_file(file):
    with open(file, 'r') as fh:
        line = fh.readline()
        line_number = 0
        while line:
            line = line.strip('\n')
            count_and_capture_ifdefs(line, file, line_number)
            count_and_capture_ifndefs(line, file, line_number)
            count_and_capture_endifs(line, file, line_number)
            count_and_capture_ifdefineds(line, file, line_number)
            count_and_capture_elifs(line, file, line_number)
            count_and_capture_elseifs(line, file, line_number)
            line = fh.readline()
            line_number += 1
    return


if __name__ == "__main__":
    root = sys.argv[1]

    for file in get_all_cpp_beneath(root):
        print(file)
        get_all_directives_in_file(file)

        filtered_ifdefs = get_x_from_file_y(ifdefs, file)
        filtered_ifndefs = get_x_from_file_y(ifndefs, file)
        filtered_endifs = get_x_from_file_y(endifs, file)
        filtered_elifs = get_x_from_file_y(elifs, file)
        filtered_elseifs = get_x_from_file_y(elseifs, file)
        filtered_ifdefineds = get_x_from_file_y(ifdefineds, file)

        indent = 0
        for tup in combine((filtered_ifdefs,
                            filtered_ifndefs,
                            filtered_endifs,
                            filtered_elifs,
                            filtered_elseifs,
                            filtered_ifdefineds)):

            if tup[0].startswith('#endif'):
                indent -= 1
            print(str(indent) + indent*4*' ' + tup[0])
            if tup[0].startswith(('#ifdef', '#ifndef', '#if defined')):
                indent += 1
