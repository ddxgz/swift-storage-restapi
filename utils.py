from datetime import datetime, timedelta
import logging
import six

from prettytable import PrettyTable


def yesterday_str(today_str, format='%Y-%m-%d'):
    return str(datetime.strptime(today_str, format) - timedelta(days=1))[:10]


def tomorrow_str(today_str, format='%Y-%m-%d'):
    return str(datetime.strptime(today_str, format) + timedelta(days=1))[:10]


def now_str(format='%Y-%m-%d'):
    return str(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))


def print_dict(d, wrap=0):
    """pretty table prints dictionaries.
    Wrap values to max_length wrap if wrap>0
    """
    pt = PrettyTable(['Property', 'Value'],
                                 caching=False, print_empty=False)
    pt.aligns = ['l', 'l']
    for (prop, value) in six.iteritems(d):
        if value is None:
            value = ''
        value = _word_wrap(value, max_length=wrap)
        pt.add_row([prop, value])
    # encoded = encodeutils.safe_encode(pt.get_string(sortby='Property'))
    # if six.PY3:
    #     encoded = encoded.decode()
    # print(encoded)
    # print(pt)
    return pt


def pretty_logging(d=None, notes='', level=logging.DEBUG):
    logging.basicConfig(format='%(levelname)s, %(message)s', 
    level=level)
    if d:
        pt = print_dict(d)
        if level is not logging.DEBUG:
            pass
        else:
            logging.debug(notes + '\n' + str(pt))



def _word_wrap(string, max_length=0):
    """wrap long strings to be no longer than max_length."""
    if max_length <= 0:
        return string
    return '\n'.join([string[i:i + max_length] for i in
                     range(0, len(string), max_length)])


def print_list(objs, fields, formatters={}, order_by=None):
    pt = PrettyTable([f for f in fields],
                                 caching=False, print_empty=False)
    pt.aligns = ['l' for f in fields]

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                field_name = field.lower().replace(' ', '_')
                data = getattr(o, field_name, '')
                if data is None:
                    data = ''
                row.append(data)
        pt.add_row(row)

    if order_by is None:
        order_by = fields[0]
    # encoded = encodeutils.safe_encode(pt.get_string(sortby=order_by))
    # if six.PY3:
    #     encoded = encoded.decode()
    # print(encoded)
    print(pt)


def list_with_key(dict_list, key):
    target_list = []
    logging.debug('in list_with_key:{}, key:{}'.format(dict_list, key))
    for adict in dict_list:
        pretty_logging(adict,'in list_with_key, adict.keys:%s'%adict.keys())
        if key in adict.keys():
            pretty_logging({'key':key})
            target_list.append(adict)
    return target_list