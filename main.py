import sys
import os
import itertools
import visualisedictionary as vd

ifdefs = []
ifndefs = []
endifs = []
elifs = []
elseifs = []
ifs = []


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


def count_and_capture_ifs(line, file, line_number):
    if line.strip().startswith('#if '):
        ifs.append((line, file, line_number))


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
            line = line.split(sep='//')[0].strip()
            count_and_capture_ifdefs(line, file, line_number)
            count_and_capture_ifndefs(line, file, line_number)
            count_and_capture_endifs(line, file, line_number)
            count_and_capture_ifs(line, file, line_number)
            count_and_capture_elifs(line, file, line_number)
            count_and_capture_elseifs(line, file, line_number)
            line = fh.readline()
            line_number += 1
    return


def add_to_dict(full_list,current_dict):
    # print('full list', full_list)
    # print('current_dict', current_dict)
    if len(full_list) == 1:
        if full_list[0] not in current_dict:
            current_dict[full_list[0]] = dict()
    else:
        current_dict[full_list[0]] = add_to_dict(full_list[1:],current_dict[full_list[0]])
    return current_dict


if __name__ == "__main__":
    root = sys.argv[1]
    full_dict = dict()

    for file in get_all_cpp_beneath(root):
        current_list = []
        test_dict = dict()

        print('\n'+file)
        get_all_directives_in_file(file)

        filtered_ifdefs = get_x_from_file_y(ifdefs, file)
        filtered_ifndefs = get_x_from_file_y(ifndefs, file)
        filtered_endifs = get_x_from_file_y(endifs, file)
        filtered_elifs = get_x_from_file_y(elifs, file)
        filtered_elseifs = get_x_from_file_y(elseifs, file)
        filtered_ifs = get_x_from_file_y(ifs, file)

        filtered_ifdefs = [x for x in filtered_ifdefs if not x[0] == '#ifdef OLD_DYNAMICS']
        filtered_ifndefs = [x for x in filtered_ifndefs if not x[0] == '#ifndef OLD_DYNAMICS']
        indent = 0
        for tup in combine((filtered_ifdefs,
                            filtered_ifndefs,
                            filtered_endifs,
                            filtered_elifs,
                            filtered_elseifs,
                            filtered_ifs)):

            if tup[0].startswith('#endif'):
                indent -= 1
                try:
                    current_list.pop()
                except:
                    print('error in ', tup[0], tup[1], tup[2])
            # print(str(indent) + indent*4*' ' + tup[0])
            if tup[0].startswith(('#ifdef', '#if ', '#ifndef')):
                indent += 1
                current_list.append(tup[0])
                add_to_dict(current_list,test_dict)
                add_to_dict(current_list,full_dict)
            if tup[0].startswith(('#elif', '#elseif')):
                current_list.pop()
                current_list.append(tup[0])
                add_to_dict(current_list, test_dict)
                add_to_dict(current_list, full_dict)
        print(current_list)
        print(test_dict)
        vd.pprint(test_dict)
        G = vd.KeysGraph(test_dict)
        G.draw(file + 'test.png')
        for tup in combine((filtered_ifdefs,
                            filtered_ifndefs,
                            filtered_endifs,
                            filtered_elifs,
                            filtered_elseifs,
                            filtered_ifs)):

            if tup[0].startswith('#endif'):
                try:
                    current_list.pop()
                except:
                    print('error in ', tup[0], tup[1], tup[2])
            # print(str(indent) + indent*4*' ' + tup[0])
            if tup[0].startswith(('#ifdef', '#if ', '#ifndef')):
                current_list.append(tup[0])
                add_to_dict(current_list,test_dict)
                add_to_dict(current_list,full_dict)
            if tup[0].startswith(('#elif', '#elseif')):
                current_list.pop()
                current_list.append(tup[0])
                add_to_dict(current_list, test_dict)
                add_to_dict(current_list, full_dict)

        assert len(current_list) == 0, AssertionError('current_list is not empty at end of file processing')
    vd.pprint(full_dict)
    G = vd.KeysGraph(full_dict)
    G.graph_attr.update(size="100,100")
    # G.graph_attr.update(ratio="fill")
    G.draw('./fulltest.png')

    # TODO: handle else clauses
