"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from mongorunner import TestCase
from mbox_processor.models import Mbox
import mbox_processor
import os


class MboxImportTest(TestCase):
    data_folder = os.path.abspath(mbox_processor.__path__[0]) + "/../data/"
    def testShouldParseAndImportMboxFiles(self):
        Mbox(self.data_folder + "201208.mbox").parse_and_save()
        Mbox(self.data_folder + "201209.mbox").parse_and_save()
        Mbox(self.data_folder + "201210.mbox").parse_and_save()
        Mbox(self.data_folder + "201211.mbox").parse_and_save()
        Mbox(self.data_folder + "201212.mbox").parse_and_save()
        Mbox(self.data_folder + "201301.mbox").parse_and_save()
        Mbox(self.data_folder + "201302.mbox").parse_and_save()
        Mbox(self.data_folder + "201303.mbox").parse_and_save()

