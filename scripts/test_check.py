#!/usr/bin/env python3
"""Exercise the family runner against disposable Git repositories and owner checks."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import check as runner
import check_common_ref as refs


BUILD = """import argparse, json, os
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--out', type=Path)
args = p.parse_args()
version = Path('VERSION').read_text().strip()
with open(os.environ['FAMILY_TEST_AUDIT'], 'a') as f:
    f.write(json.dumps(['build', version]) + '\\n')
if os.environ.get('FAMILY_TEST_BUILD_FAIL') == version:
    raise SystemExit(9)
args.out.mkdir()
(args.out / 'VERSION').write_text(version)
"""
OWNER = """import argparse, json, os
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--python')
p.add_argument('--common-wheels', type=Path)
p.add_argument('--services-root', type=Path)
args = p.parse_args()
name = Path.cwd().name
version = (args.common_wheels / 'VERSION').read_text().strip()
assert version == Path('expected').read_text().strip(), (name, version)
if name == 'boring-pondnt':
    assert (args.services_root / 'bundle').read_text() == 'accepted bundle'
with open(os.environ['FAMILY_TEST_AUDIT'], 'a') as f:
    f.write(json.dumps(['owner', name, version]) + '\\n')
raise SystemExit(7 if os.environ.get('FAMILY_TEST_OWNER_FAIL') == name else 0)
"""


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def commit(root):
    git(root, 'add', '.')
    git(root, 'commit', '-qm', 'fixture')
    return git(root, 'rev-parse', 'HEAD')


class FamilyCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='family-runner-test-')
        self.addCleanup(self.tmp.cleanup)
        self.family = Path(self.tmp.name)
        self.audit = self.family / 'audit.jsonl'
        for repo in ('boring-pond-common', *refs.CONSUMERS):
            root = self.family / repo
            root.mkdir()
            git(root, 'init', '-q')
            git(root, 'config', 'user.name', 'Fixture')
            git(root, 'config', 'user.email', 'fixture@example.test')
        self.common = self.family / 'boring-pond-common'
        write(self.common, 'scripts/build.py', BUILD)
        self.commits = {}
        for version in ('0.7.8', '0.7.10'):
            write(self.common, 'VERSION', version)
            self.commits[version] = commit(self.common)
        self.services = self.family / 'boring-services'
        write(self.services, 'bundle', 'accepted bundle')
        self.services_ref = commit(self.services)
        write(self.services, 'bundle', 'current, incompatible bundle')
        for name in runner.CONSUMERS:
            root = self.family / runner.CHECKS[name][0]
            version = '0.7.10'
            write(root, '.common-ref', self.commits[version] + '\n')
            write(root, 'requirements.lock', 'boring-registry==' + version + '\n')
            write(root, 'expected', version)
            write(root, 'scripts/check.py', OWNER)
            if name == 'pondnt':
                write(root, '.services-ref', self.services_ref + '\n')
            commit(root)
        self.before = {repo: (git(self.family / repo, 'rev-parse', 'HEAD'),
                              git(self.family / repo, 'status', '--porcelain'),
                              git(self.family / repo, 'worktree', 'list', '--porcelain'))
                       for repo in ('boring-pond-common', *refs.CONSUMERS)}
        for obj, name, value in ((runner, 'FAMILY', self.family), (refs, 'FAMILY', self.family),
                                 (refs, 'COMMON', self.common)):
            context = patch.object(obj, name, value)
            context.start()
            self.addCleanup(context.stop)
        context = patch.dict(os.environ, FAMILY_TEST_AUDIT=str(self.audit))
        context.start()
        self.addCleanup(context.stop)

    def run_check(self, *args):
        out = io.StringIO()
        with patch.object(sys, 'argv', ['check.py', *args]), redirect_stdout(out), redirect_stderr(out):
            result = runner.main()
        return result, out.getvalue()

    def events(self):
        return [json.loads(line) for line in self.audit.read_text().splitlines()] if self.audit.exists() else []

    def assert_untouched(self):
        for repo, before in self.before.items():
            root = self.family / repo
            self.assertEqual(before, (git(root, 'rev-parse', 'HEAD'), git(root, 'status', '--porcelain'),
                                      git(root, 'worktree', 'list', '--porcelain')), repo)

    def mix(self):
        """Pirates relocked onto another Common: refs and locks agree, but differ from the family."""
        root = self.family / 'boring-pirates'
        write(root, '.common-ref', self.commits['0.7.8'] + '\n')
        write(root, 'requirements.lock', 'boring-registry==0.7.8\n')

    def test_one_common_is_built_once_with_the_frozen_bundle(self):
        result, _ = self.run_check('--only', *runner.CONSUMERS)
        self.assertEqual(result, 0)
        self.assertEqual([e for e in self.events() if e[0] == 'build'], [['build', '0.7.10']])
        self.assertEqual(len([e for e in self.events() if e[0] == 'owner']), 4)
        self.assert_untouched()

    def test_differing_common_refs_are_refused_before_effects(self):
        self.mix()
        for extra in ((), ('--common-wheels', str(self.family))):
            with self.subTest(extra=extra):
                result, output = self.run_check(*extra, '--only', 'crocodile', 'pirates')
                self.assertEqual(result, 1)
                self.assertIn('Common refs differ', output)
                self.assertEqual(self.events(), [])

    def test_explicit_dist_is_used_instead_of_a_build(self):
        dist = self.family / 'dist'
        dist.mkdir()
        write(dist, 'VERSION', '0.7.10')
        result, _ = self.run_check('--common-wheels', str(dist), '--only', 'crocodile', 'services')
        self.assertEqual(result, 0)
        self.assertEqual(len(self.events()), 2)
        self.assertTrue(all(e[0] == 'owner' for e in self.events()))
        self.assert_untouched()

    def test_missing_moving_and_lock_mismatched_refs_fail_before_builds(self):
        root = self.family / 'boring-pirates'
        for ref in ('main', 'f' * 40, self.commits['0.7.8']):
            with self.subTest(ref=ref):
                write(root, '.common-ref', ref)
                result, _ = self.run_check('--only', 'pirates')
                self.assertEqual(result, 1)
                self.assertEqual(self.events(), [])
        write(root, '.common-ref', self.commits['0.7.10'] + '\n')
        (self.family / 'boring-pondnt' / '.services-ref').unlink()
        result, _ = self.run_check('--only', 'pondnt')
        self.assertEqual(result, 1)
        self.assertEqual(self.events(), [])

    def test_names_check_is_skipped_without_private_records(self):
        result, output = self.run_check('--only', 'names')
        self.assertEqual(result, 0)
        self.assertIn('pond/checks absent: skipped', output)

    def test_build_failure_cleans_worktree_and_does_not_run_owner(self):
        with patch.dict(os.environ, FAMILY_TEST_BUILD_FAIL='0.7.10'):
            result, _ = self.run_check('--only', 'pirates')
        self.assertEqual(result, 1)
        self.assertEqual(self.events(), [['build', '0.7.10']])
        self.assert_untouched()

    def test_owner_failure_still_checks_next_owner_and_cleans_worktrees(self):
        with patch.dict(os.environ, FAMILY_TEST_OWNER_FAIL='boring-crocodile'):
            result, output = self.run_check('--only', 'crocodile', 'pondnt')
        self.assertEqual(result, 1)
        self.assertIn('FAILED (7)', output)
        self.assertEqual(len([e for e in self.events() if e[0] == 'owner']), 2)
        self.assert_untouched()


if __name__ == '__main__':
    unittest.main()
