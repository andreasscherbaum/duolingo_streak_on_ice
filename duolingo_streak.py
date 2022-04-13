#!/usr/bin/env python3
#
# buy another "Streak on Ice" extension in Duolingo
#
# written by: Andreas Scherbaum <andreas@scherbaum.la>
#

# Note: this requires the "Duolingo" module in the current directory
# see:
# https://github.com/KartikTalwar/Duolingo
# http://tschuy.com/duolingo/api/endpoints.html

import re
import os
import stat
import sys
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')
import logging
import tempfile
import argparse
import yaml
import string
import datetime
import atexit
import smtplib
from email.mime.text import MIMEText
import pprint

sys.path.insert(0, 'Duolingo')
import duolingo

# start with 'info', can be overriden by '-q' later on
logging.basicConfig(level = logging.INFO,
		    format = '%(levelname)s: %(message)s')
# avoid info messages from the "Requests" module
logging.getLogger('requests').setLevel(logging.ERROR)
pp = pprint.PrettyPrinter(indent=4)




#######################################################################
# Config class

class Config:

    def __init__(self):
        self.__cmdline_read = 0
        self.__configfile_read = 0
        self.arguments = False
        self.argument_parser = False
        self.configfile = False
        self.config = False
        self.output_help = True

        if (os.environ.get('HOME') is None):
            logging.error("$HOME is not set!")
            sys.exit(1)
        if (os.path.isdir(os.environ.get('HOME')) is False):
            logging.error("$HOME does not point to a directory!")
            sys.exit(1)



    # config_help()
    #
    # flag if help shall be printed
    #
    # parameter:
    #  - self
    #  - True/False
    # return:
    #  none
    def config_help(self, config):
        if (config is False or config is True):
            self.output_help = config
        else:
            print("")
            print("invalid setting for config_help()")
            sys.exit(1)



    # print_help()
    #
    # print the help
    #
    # parameter:
    #  - self
    # return:
    #  none
    def print_help(self):
        if (self.output_help is True):
            self.argument_parser.print_help()



    # parse_parameters()
    #
    # parse commandline parameters, fill in array with arguments
    #
    # parameter:
    #  - self
    # return:
    #  none
    def parse_parameters(self):
        parser = argparse.ArgumentParser(description = 'buy another "Streak on Ice" in Duolingo',
                                         add_help = False)
        self.argument_parser = parser
        parser.add_argument('--help', default = False, dest = 'help', action = 'store_true', help = 'show this help')
        parser.add_argument('-c', '--config', default = '', dest = 'config', help = 'configuration file')
        # store_true: store "True" if specified, otherwise store "False"
        # store_false: store "False" if specified, otherwise store "True"
        parser.add_argument('-v', '--verbose', default = False, dest = 'verbose', action = 'store_true', help = 'be more verbose')
        parser.add_argument('-q', '--quiet', default = False, dest = 'quiet', action = 'store_true', help = 'run quietly')


        # parse parameters
        args = parser.parse_args()

        if (args.help is True):
            self.print_help()
            sys.exit(0)

        if (args.verbose is True and args.quiet is True):
            self.print_help()
            print("")
            print("Error: --verbose and --quiet can't be set at the same time")
            sys.exit(1)

        if not (args.config):
            self.print_help()
            print("")
            print("Error: configfile is required")
            sys.exit(1)

        if (args.verbose is True):
            logging.getLogger().setLevel(logging.DEBUG)

        if (args.quiet is True):
            logging.getLogger().setLevel(logging.ERROR)

        self.__cmdline_read = 1
        self.arguments = args

        return



    # load_config()
    #
    # load configuration file (YAML)
    #
    # parameter:
    #  - self
    # return:
    #  none
    def load_config(self):
        if not (self.arguments.config):
            return

        logging.debug("config file: " + self.arguments.config)

        if (self.arguments.config and os.path.isfile(self.arguments.config) is False):
            self.print_help()
            print("")
            print("Error: --config is not a file")
            sys.exit(1)

        # the config file holds sensitive information, make sure it's not group/world readable
        st = os.stat(self.arguments.config)
        if (st.st_mode & stat.S_IRGRP or st.st_mode & stat.S_IROTH):
            self.print_help()
            print("")
            print("Error: --config must not be group or world readable")
            sys.exit(1)


        try:
            with open(self.arguments.config, 'r') as ymlcfg:
                config_file = yaml.safe_load(ymlcfg)
        except:
            print("")
            print("Error loading config file")
            sys.exit(1)


        # verify account
        try:
            t = config_file['account']
        except KeyError:
            print("")
            print("Error: missing 'account' in config file")


        # verify username
        try:
            t = config_file['account']['username']
        except KeyError:
            print("")
            print("Error: missing 'account/username' in config file")


        # verify password
        try:
            t = config_file['account']['password']
        except KeyError:
            print("")
            print("Error: missing 'account/password' in config file")


        # verify sender address
        try:
            t = config_file['sender_address']
        except KeyError:
            print("")
            print("Error: missing 'sender_address' in config file")


        # verify status
        try:
            t = config_file['status']
        except KeyError:
            print("")
            print("Error: missing 'status' in config file")


        # verify send_status
        try:
            t = config_file['status']['send_status']
        except KeyError:
            print("")
            print("Error: missing 'status/send_status' in config file")


        # verify send_friends
        try:
            t = config_file['status']['send_friends']
        except KeyError:
            print("")
            print("Error: missing 'status/send_friends' in config file")


        # verify shop
        try:
            t = config_file['shop']
        except KeyError:
            print("")
            print("Error: missing 'shop' in config file")


        # verify buy_streak
        try:
            t = config_file['shop']['buy_streak']
        except KeyError:
            print("")
            print("Error: missing 'shop/buy_streak' in config file")


        self.configfile = config_file
        self.__configfile_read = 1

        return


# end Config class
#######################################################################


#######################################################################
# main program

config = Config()
config.parse_parameters()
config.load_config()


lingo = duolingo.Duolingo(config.configfile['account']['username'], password = config.configfile['account']['password'])
# workaround
num_streak_on_ice = lingo.__dict__['user_data'].__dict__['tracking_properties']['num_item_streak_freeze']


user_info = lingo.get_user_info()
user_settings = lingo.get_settings()
# getting friends is currently broken
# https://github.com/KartikTalwar/Duolingo/issues/112
# the variable $user_friends is currently not in use
#user_friends = lingo.get_friends()
user_streak_info = lingo.get_streak_info()
#pp.pprint(user_streak_info)
# the field "streak_extended_today" is only telling us if the user extended the streak today
# it's not telling us if the user is equipped with a streak on ice
user_xp_progress = lingo.get_daily_xp_progress()
#pp.pprint(user_xp_progress)



if (config.configfile['shop']['buy_streak'] is True and num_streak_on_ice < 2):
    logging.debug("going to buy 'Streak on Ice' extension ...")
    try:
        if (lingo.buy_streak_freeze() is True):
            logging.info("bought streak extension for: " + str(user_info['username']))
    except duolingo.AlreadyHaveStoreItemException:
        # not possible to buy item (already equipped)
        pass
    except Exception:
        logging.error("Unknown exception!")
        sys.exit(1)

    try:
        if (lingo.buy_item('streak_freeze', 'en') is True):
            logging.info("bought streak extension for: " + str(user_info['username']))
    except duolingo.AlreadyHaveStoreItemException:
        # not possible to buy item (already equipped)
        pass
    except Exception:
        logging.error("Unknown exception!")
        sys.exit(1)


if (config.configfile['status']['send_status'] is True):
    # re-read streak status
    user_streak_info = lingo.get_streak_info()
    user_xp_progress = lingo.get_daily_xp_progress()
    logging.debug("going to send streak status information ...")
    if (user_streak_info['streak_extended_today'] == True):
        logging.info("Streak extended today: yes")
    else:
        logging.info("Streak extended today: no")
    logging.info("Streak days: %s" % (str(user_streak_info['site_streak'])))
    logging.info("XP today: %s (goal: %s)" % (str(user_xp_progress['xp_today']), str(user_xp_progress['xp_goal'])))
    logging.info("Number streaks on ice: %s" % (str(num_streak_on_ice)))
