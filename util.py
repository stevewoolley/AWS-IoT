import logging


def set_logger(name='iot', level=logging.INFO):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filename="/var/log/%s.log" % (name),
                        filemode='a')
    return logging.getLogger()


def search_list(l, search_string, idx):
    if idx > len(l) - 1:
        return None
    for sublist in l:
        if sublist[idx] == search_string:
            return sublist
    return None
