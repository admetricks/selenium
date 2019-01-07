import copy
import json
import os
import shutil
import tempfile

import selenium.webdriver.firefox.firefox_profile as firefox_profile
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


class FirefoxProfileInPlace(FirefoxProfile):
    """
    Patched version of class FirefoxProfile that has the option to use the i
    provided profile in place, rather than making a copy of it.

    The default is to copy the profile, per the parent class.

    Obvious risks include change of state (whether desired or not) and
    the possibility of running multiple instances of this profile concurrently.
    """
    def __init__(self, profile_directory=None, in_place=False):
        """
        Initialises a new instance of a Firefox Profile

        :args:
         - profile_directory: Directory of profile that you want to use.
           This defaults to None and will create a new
           directory when object is created.
        """
        if not FirefoxProfile.DEFAULT_PREFERENCES:
            with open(os.path.join(os.path.dirname(firefox_profile.__file__),
                                   firefox_profile.WEBDRIVER_PREFERENCES)) as default_prefs:
                FirefoxProfile.DEFAULT_PREFERENCES = json.load(default_prefs)

        self.default_preferences = copy.deepcopy(
            FirefoxProfile.DEFAULT_PREFERENCES['mutable'])
        self.native_events_enabled = True
        self.profile_dir = profile_directory
        self.tempfolder = None
        if self.profile_dir is None:
            self.profile_dir = self._create_tempfolder()
        else:
            if not in_place:
                self.tempfolder = tempfile.mkdtemp()
                newprof = os.path.join(self.tempfolder, "webdriver-py-profilecopy")
                shutil.copytree(self.profile_dir, newprof,
                                ignore=shutil.ignore_patterns("parent.lock", "lock", ".parentlock"))
                self.profile_dir = newprof
            else:
                self.profile_dir = profile_directory
            self._read_existing_userjs(os.path.join(self.profile_dir, "user.js"))
        self.extensionsDir = os.path.join(self.profile_dir, "extensions")
        self.userPrefs = os.path.join(self.profile_dir, "user.js")
