#!/usr/bin/env python
import argparse
import json
import os.path
import sys

import configparser

from helpers.functions import get_url_from_name, get_ip_blocks_from_nirsoft, count_ip_address, \
    generate_masscan_settings, write_massscan_config_files
from labels import *
from helpers.masscan.parsers.json import parse as masscan_parser
from helpers.masscan.parsers.json import transform as masscan_translator

CONFIG_FILE = 'settings.ini'
MASSCAN_SETTINGS_PATH = 'scans'
MASSCAN_SETTINGS_RESULTS = 'results'

NirSoft_DOMAIN = 'www.nirsoft.net'


def should_continue(blocks, total):
    return total != 0


def validate_settings(config):
    return os.path.exists(config.get('default', 'masscan')) and \
           config.get('default', 'rate') > 0 and \
           len(config.get('default', 'ports').split(',')) > 0


if __name__ == '__main__':
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    test = "{}/{}/0.json".format(current_path, MASSCAN_SETTINGS_RESULTS)

    with open(test) as data_file:
        data = json.loads(data_file.read())

    results = masscan_translator(masscan_parser(data))
    """
    config = configparser.ConfigParser()
    config.read('settings.ini')

    if not validate_settings(config):
        print "Settings are not valid."
        sys.exit(-1)

    masscan = config.get('default', 'masscan')

    parser = argparse.ArgumentParser(description='Mass scanning a whole country.')
    parser.add_argument('--country', help='Country')

    args = parser.parse_args()

    total = 0
    blocks = []

    if args.country:
        country_url = get_url_from_name(NirSoft_DOMAIN, args.country)
        blocks = get_ip_blocks_from_nirsoft(country_url)

    total = count_ip_address(blocks)

    if not should_continue(blocks, total):
        print NO_IP_WAS_FOUND
        sys.exit(-1)

    print TOTAL_IP_COUNTS.format(total)

    current_path = os.path.dirname(os.path.realpath(__file__))

    masscan_settings = generate_masscan_settings(blocks,
                                                 config.getfloat('default', 'rate'),
                                                 config.get('default', 'ports'),
                                                 "{}/{}".format(current_path, MASSCAN_SETTINGS_RESULTS),
                                                 config.getboolean('default', 'banners'))

    scan_created = write_massscan_config_files(masscan_settings, "{}/{}".format(current_path, MASSCAN_SETTINGS_PATH))
