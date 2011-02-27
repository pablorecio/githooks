# Copyright (C) 2011  Alejandro Blanco Escudero <alejandro.b.e@gmail.com>
#
# This file is part of githooks
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import re
import shutil
import tempfile

version = "0.1.1dev"

re_options = re.IGNORECASE | re.MULTILINE | re.DOTALL
skip_pattern = re.compile('# githooks: (.*)', re_options)


class MercurialUI(object):

    def debug(self, text):
        # TODO print only in debug mode
        print text

    def warn(self, text):
        # TODO print in the error output
        print text

    def config(self, arg1, arg2, arg3=None):
        # TODO access config
        return ''


class GitCommands(object):

    def getDescription(self, revision):
        # TODO
        return ""

    def getFileNames(self, revision):
        # TODO
        return []

    def getFileData(self, revision, filename):
        # TODO
        return ""


class CheckerManager(object):

    def __init__(self, ui, revisions, skip_text=None):
        self.ui = ui
        self.revisions = revisions
        self.skip_text = skip_text
        self.gitcmd = GitCommands()

    def skip_file(self, filename, filedata):
        if not filename.endswith('.py'):
            return True

        for match in skip_pattern.findall(filedata):
            if self.skip_text in match:
                return True

        return False

    def check(self, checker):
        warnings = 0
        for current_rev in self.revisions:
            rev_warnings = 0
            directory = tempfile.mkdtemp(suffix='-r%d' % current_rev,
                                         prefix='githooks')

            self.ui.debug("Checking revision %d\n" % current_rev)

            description = self.gitcmd.getDescription(current_rev)
            if self.skip_text and self.skip_text in description:
                continue

            files_to_check = {}
            revision_files = self.gitcmd.getFileNames(current_rev)
            for filename in revision_files:

                # TODO check if the file was removed in this changeset

                filedata = self.gitcmd.getFileData(current_rev, filename)

                if self.skip_text and self.skip_file(filename, filedata):
                    continue

                full_path = os.path.join(directory, filename)
                files_to_check[full_path] = filedata

            if files_to_check:
                rev_warnings += checker(files_to_check, description)

            if rev_warnings:
                self.ui.warn('%d warnings found in revision %d\n' %
                             (rev_warnings, current_rev - 1))
            else:
                self.ui.debug('No warnings in revision %d. Good job!\n' %
                              (current_rev - 1))
            warnings += rev_warnings
            shutil.rmtree(directory)

        if warnings:
            return True   # failure
        else:
            return False  # sucess