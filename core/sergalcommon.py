import calendar
from datetime import datetime
from enum import Enum
from json import JSONDecodeError
import json
import logging
import os
import configparser
import mysql.connector
import xml
import xml.etree.ElementTree as ET
import pprint
from core import databasemodule
from core.databaseversions import databaseVersions

def checkSettings():
    if not os.path.isfile("settings.conf"):
            print("settings -> Config file not present!")
            settings = configparser.ConfigParser()
            settings['connections'] = {
                'mysql-host': '127.0.0.1',
                'mysql-username': 'sergal',
                'mysql-password': 'somepassword',
                'log-to-db': False,
            }
            settings['discord'] = {
                'bot-name': 'SergalBot',
                'api-key': 'CHANGE_KEY_IN_SETTINGS',
                'hikari-loglevel': logging.DEBUG
            }
            settings['application'] = {
                'loglevel': logging.INFO,
                'startup-update': True,
                'loglevels-available': f'{logging.DEBUG}, {logging.INFO}, {logging.WARNING}, {logging.ERROR}, {logging.CRITICAL}, {logging.FATAL}',
                'logname': 'SergalBot # .log will be appended',
                'testing': False
            }
            with open("settings.conf", 'w') as configfile:
                settings.write(configfile)
            
            print("Complete setup in settings.conf !")
            exit()
    else:
        settings = configparser.ConfigParser()
        settings.read("settings.conf")
        return settings
            
class SergalBot():

    class databaseUpdater:

        def commitUpdate(self):
            for i in range(len(self.updates_pending)):
                logging.info(f'Applying update {i+1}/{len(self.updates_pending)}')
                try:
                    self.updates_pending[i]() # TODO: add database module exceptions
                except mysql.connector.errors.ProgrammingError as e:
                    if e.errno == 1060:
                        logging.warning("Duplicate column in update step...Skipping...")
                        self.db.currentQuery = ""
                    else:
                        self.problem = True
                        logging.exception("Updater encountered an error!", exc_info=True)
                        return
                except Exception as e:
                    self.problem = True
                    logging.exception("Updater encountered an error!", exc_info=True)
                    return
            logging.info("All updates complete")

        def update_gather(self):
            steps = []

            proposed_version = self.db_version
            for attr_name in dir(databaseVersions):
                attr = getattr(databaseVersions, attr_name)
                if callable(attr) and not attr_name.startswith('__'):
                    updates = attr(self.db, proposed_version)
                    if len(updates) > 0:
                        proposed_version+=1
                    for update in updates:
                        steps.append(update)
            
            
            logging.info(f'{len(steps)} database record updates available')
            if proposed_version > self.db_version:
                logging.info(f'Updater wants to update database from v{self.db_version} to v{proposed_version}')

            return steps

        def get_db_ver(self):
            if "settings" in self.db.tables:
                logging.info("Settings table found.")
                try:
                    results = self.db.select("settings", where=["setting"], where_val=["db_ver"])
                    database_version = results[0][1]
                    self.db_version = database_version
                except Exception as e:
                    logging.exception(f'Updater had exception while checking database version! {results=}', exc_info=True)
                    self.db_version = '?'
                    self.problem = True

        def __init__(self, db:databasemodule.databaseHandler, runNow=False, simulate=False, checkVersion=True) -> None:
            self.db = db
            self.runNow = runNow
            self.simulate = simulate
            self.checkVersion = checkVersion
            self.isUpdateRequired = False
            self.problem = False
            self.updates_pending = []
            self.db_version = None

            logging.debug(f'Update -> ENTRY db: v{self.db_version}')
            self.db.refreshTables()

            if len(self.db.tables) == 0:
                self.db_version = 0
                logging.info("No tables present in database, Hello!")
            
            self.get_db_ver()

            if self.problem is False:
                self.updates_pending = self.update_gather()
                if runNow:
                    self.commitUpdate()
                    self.get_db_ver()                 

    def __init__(self, settings: configparser.ConfigParser, testing=False, skip_updater=False, update_only=False) -> None:
        self.db_version = None
        self.dbHost = settings.get("connections", "mysql-host")
        self.dbuser = settings.get("connections", "mysql-username")
        self.dbpassword = settings.get("connections", "mysql-password")

        logging.debug("Connecting to MySQL...")
        if not testing:
            self.db = databasemodule.databaseHandler(dbHost, dbuser, dbpassword, "Sergal-prod")
        else:
            self.db = databasemodule.databaseHandler(dbHost, dbuser, dbpassword, "Sergal-dev")

        if not skip_updater:
            updater = self.databaseUpdater(self.db, runNow=True)
            if updater.problem:
                logging.critical("SergalBot -> Updater reported a problem! Exiting Immediately!")
                exit()
            else:
                self.db_version = updater.db_version
                logging.info(f'Database v{self.db_version}')

    def getRightNowTime():
        dt = datetime.today()
        seconds = calendar.timegm(dt.timetuple())
        return seconds

    def secConverter(self, seconds:int) -> str:
        minutes = int(seconds/60)
        return f'{minutes} Minutes'
    
    def reportError(self, type, info):
        self.db.currentQuery = ""
        self.db.insert("errors",
                      ["type", "info"],
                      [type, info]
        )
        logging.info("Error reported")

    def getChannelSetting(self, guildID, channelID):
        results = self.db.select("channel_settings", where=["guild_id"], where_val=[guildID])
        return results

    def setChannelSetting(self, guildID, channelID, setting):
        self.db.insert("channel_settings", columns=["guild_id", "channel_id", "setting"], data=[guildID, channelID, setting])

    def getSetting(self, settingName):
        results = self.db.select("settings", where=["setting"], where_val=[settingName])
        if len(results) == 0:
            logging.warning(f'Settings -> Asked for {settingName=} but it was not set in the database.')
            return None
        elif len(results) == 1:
            setting_val = results[0][1]
            setting_text = results[0][2]
            if setting_val is not None:
                setting = setting_val
            elif setting_text is not None:
                setting = setting_text
            elif setting_val is None and setting_text is None:
                logging.warning(f'Settings -> no data set for setting {settingName=} -> we return none')
                return None
            
            if setting_val is not None and setting_text is not None:
                logging.warning(f'Settings -> Both setting values for {settingName=} had data. -> We return the results list')
                return results
            logging.debug(f'Settings -> Got {settingName=} -> {setting}')
            return setting
        elif len(results) > 1:
            logging.warning(f'Settings -> Multiple entries for {settingName=} - This might be intentional. Or a bug. Returning {len(results)} setting entries...')
            return results
        
    def setSetting(self, settingName, value):
        logging.debug("Settings -> Testing entry before changing database...")
        test = self.db.select("settings", where=["setting"], where_val=[settingName])

        if len(test) == 0:
            logging.info(f'Settings -> Creating new settings entry "{settingName}" -> {value}')
            if isinstance(value, int):
                self.db.insert("settings",
                               ["setting", "setting_val"],
                               [settingName, value])
            elif isinstance(value, str):
                self.db.insert("settings",
                               ["setting", "setting_text"],
                               [settingName, value])
            else:
                logging.warning(f'Settings -> {settingName=} is being set with data that is not a string or an integer. This may be a bug. \n{value=}')
                self.db.insert("settings",
                               ["setting", "setting_text"],
                               [settingName, value])
        if len(test) == 1:
            logging.info(f'Settings -> Updating {settingName=} to {value=}')
            if isinstance(value, int):
                self.db.update("settings",
                               ["setting_val"],
                               [value],
                               where="setting",
                               wherevalue=settingName)
            elif isinstance(value, str):
                self.db.update("settings",
                               ["setting_text"],
                               [value],
                               where="setting",
                               wherevalue=settingName)
            else:
                logging.warning(f'Settings -> {settingName=} is being updated with data that is not a string or an integer. This may be a bug. \n{value=}')
                self.db.update("settings",
                               ["setting_text"],
                               [value],
                               where="setting",
                               wherevalue=settingName)
    
    def getStat(self, statName):
        results = self.db.select("stat", where=["stat"], where_val=[statName])
        if len(results) == 0:
            logging.warning(f'Stats -> Asked for {statName=} but it was not set in the database.')
            return None
        elif len(results) == 1:
            stat_text = results[0][1]
            stat_val = results[0][2]
            if stat_val is not None:
                stat = stat_val
            elif stat_text is not None:
                stat = stat_text
            elif stat_val is None and stat_text is None:
                logging.warning(f'Stat -> no data set for stat {statName=} -> we return none')
                return None
            
            if stat_val is not None and stat_text is not None:
                logging.warning(f'Stat -> Both stat values for {statName=} had data. -> We return the results list')
                return results
            logging.debug(f'Stat -> Got {statName=} -> {stat}')
            return stat
        elif len(results) > 1:
            logging.warning(f'Stat -> Multiple entries for {statName=} - This might be intentional. Or a bug. Returning {len(results)} setting entries...')
            return results
        
    def setStat(self, statName, value):
        logging.debug("Stat -> Testing entry before changing database...")
        test = self.db.select("stat", where=["stat"], where_val=[statName])

        if len(test) == 0:
            logging.info(f'Stat -> Creating new stat entry "{statName}" -> {value}')
            if isinstance(value, int):
                self.db.insert("stat",
                               ["stat", "val"],
                               [statName, value])
            elif isinstance(value, str):
                self.db.insert("stat",
                               ["stat", "textval"],
                               [statName, value])
            else:
                logging.warning(f'Stat -> {statName=} is being set with data that is not a string or an integer. This may be a bug. \n{value=}')
                self.db.insert("stat",
                               ["stat", "textval"],
                               [statName, value])
        if len(test) == 1:
            logging.debug(f'Stat -> Updating {statName=} to {value=}')
            if isinstance(value, int):
                self.db.update("stat",
                               ["val"],
                               [value],
                               where="stat",
                               wherevalue=statName)
            elif isinstance(value, str):
                self.db.update("stat",
                               ["textval"],
                               [value],
                               where="stat",
                               wherevalue=statName)
            else:
                logging.warning(f'Stat -> {statName=} is being updated with data that is not a string or an integer. This may be a bug. \n{value=}')
                self.db.update("stat",
                               ["textval"],
                               [value],
                               where="stat",
                               wherevalue=statName)