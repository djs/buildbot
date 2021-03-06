import os

from twisted.trial import unittest
from twisted.python import runtime

from buildslave.test.fake.runprocess import Expect
from buildslave.test.util.sourcecommand import SourceCommandTestMixin
from buildslave.commands import git

class TestGit(SourceCommandTestMixin, unittest.TestCase):

    def setUp(self):
        self.setUpCommand()

    def tearDown(self):
        self.tearDownCommand()

    def test_simple(self):
        self.patch_getCommand('git', 'path/to/git')
        self.clean_environ()
        self.make_command(git.Git, dict(
            workdir='workdir',
            mode='copy',
            revision=None,
            repourl='git://github.com/djmitche/buildbot.git',
        ))

        exp_environ = dict(PWD='.', LC_MESSAGES='C')
        expects = [
            Expect([ 'clobber', 'workdir' ],
                self.basedir)
                + 0,
            Expect([ 'clobber', 'source' ],
                self.basedir)
                + 0,
            # TODO: capture makedirs invocation here
            Expect([ 'path/to/git', 'init'],
                os.path.join(self.basedir, 'source'),
                sendRC=False, timeout=120, usePTY=False)
                + 0,
            Expect([ 'path/to/git', 'clean', '-f', '-d', '-x'],
                os.path.join(self.basedir, 'source'),
                sendRC=False, timeout=120, usePTY=False)
                + 0,
            Expect([ 'path/to/git', 'fetch', '-t',
                     'git://github.com/djmitche/buildbot.git', '+master' ],
                os.path.join(self.basedir, 'source'),
                sendRC=False, timeout=120, usePTY=False)
                + 0,
            Expect(['path/to/git', 'reset', '--hard', 'FETCH_HEAD'],
                os.path.join(self.basedir, 'source'),
                sendRC=False, timeout=120, usePTY=False)
                + 0,
            Expect(['path/to/git', 'branch', '-M', 'master'],
                os.path.join(self.basedir, 'source'),
                sendRC=False, timeout=120, usePTY=False)
                + 0,
            Expect([ 'path/to/git', 'rev-parse', 'HEAD' ],
                os.path.join(self.basedir, 'source'),
                sendRC=False, timeout=120, usePTY=False, keepStdout=True)
                + { 'stdout' : '4026d33b0532b11f36b0875f63699adfa8ee8662\n' }
                + 0,
            Expect([ 'copy', 'source', 'workdir'],
                self.basedir)
                + 0,
        ]
        self.patch_runprocess(*expects)

        d = self.run_command()
        d.addCallback(self.check_sourcedata, "git://github.com/djmitche/buildbot.git master\n")
        return d

