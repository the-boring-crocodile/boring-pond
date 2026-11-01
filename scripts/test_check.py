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
import check_docs as docs


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
    f.write(json.dumps(['owner', name, version, args.python]) + '\\n')
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

    def test_products_run_once_per_python_family_checks_once(self):
        result, output = self.run_check('--only', 'crocodile', 'pondnt', '--python', sys.executable, sys.executable)
        self.assertEqual(result, 0)
        owners = [e for e in self.events() if e[0] == 'owner']
        self.assertEqual([(e[1], e[3]) for e in owners],
                         [('boring-crocodile', sys.executable)] * 2 + [('boring-pondnt', sys.executable)] * 2)
        self.assertEqual([e for e in self.events() if e[0] == 'build'], [['build', '0.7.10']])
        version = '%d.%d' % sys.version_info[:2]
        self.assertIn(f'crocodile@{version}', output)
        self.assert_untouched()

    def test_ci_pythons_without_uv_is_refused_before_effects(self):
        with patch.dict(os.environ, {'UV': '', 'PATH': ''}):
            result, output = self.run_check('--only', 'crocodile', '--ci-pythons')
        self.assertEqual(result, 1)
        self.assertIn('--ci-pythons needs uv', output)
        self.assertEqual(self.events(), [])


class ReleaseSetTests(unittest.TestCase):
    """check_docs: versions pinned in copy-paste blocks follow updating.md's release set table."""

    def setUp(self):
        self.repo = Path(tempfile.mkdtemp()) / 'boring-pond'
        (self.repo / 'docs').mkdir(parents=True)
        self.addCleanup(lambda: subprocess.run(['rm', '-rf', str(self.repo.parent)], check=True))
        (self.repo / 'docs' / 'updating.md').write_text(
            '| Crocodile | x | `v1.2.3` | y |\n| Pirates | x | `v0.9.0` | y |\n| Services | x | e.g. `canvas-v0.2.1` | y |\n'
            '\n    CROCODILE=1.2.3 PIRATES=0.9.0 CANVAS=0.2.1\n')
        subprocess.run(['git', 'init', '-q'], cwd=self.repo, check=True)

    def hits(self, page):
        (self.repo / 'docs' / 'start.md').write_text(page)
        subprocess.run(['git', 'add', '-A'], cwd=self.repo, check=True)
        return docs.release_set_hits(self.repo)

    def test_matching_pins_pass(self):
        self.assertEqual(self.hits('```bash\nV=1.2.3\n```\n'), [])

    def test_a_stale_pin_is_named(self):
        found = self.hits('```bash\nV=1.2.2\n```\n')
        self.assertEqual(len(found), 1)
        self.assertIn('docs/start.md:2: V=1.2.2, the release set says 1.2.3', found[0])

    def test_other_repositories_are_not_checked(self):
        other = self.repo.parent / 'boring-crocodile'
        other.mkdir()
        self.assertEqual(docs.release_set_hits(other), [])


class ServicesSetTests(unittest.TestCase):
    """check_docs: boring-services' V=X S=NAME blocks follow the release set sentence in boring-pond."""

    def setUp(self):
        self.family = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: subprocess.run(['rm', '-rf', str(self.family)], check=True))
        (self.family / 'boring-pond' / 'docs').mkdir(parents=True)
        (self.family / 'boring-pond' / 'docs' / 'updating.md').write_text(
            'The current release set: Crocodile 1.0.0,\nPirates 0.1.0, Canvas 0.2.19, Knowledge 0.2.15, Fishmarket\n0.1.14 and Ferry 0.1.3.\n')
        self.repo = self.family / 'boring-services'
        self.repo.mkdir()
        subprocess.run(['git', 'init', '-q'], cwd=self.repo, check=True)
        old, docs.FAMILY = docs.FAMILY, self.family
        self.addCleanup(lambda: setattr(docs, 'FAMILY', old))

    def hits(self, page):
        (self.repo / 'README.md').write_text(page)
        subprocess.run(['git', 'add', '-A'], cwd=self.repo, check=True)
        return docs.services_set_hits(self.repo)

    def test_matching_and_line_broken_versions_pass(self):
        self.assertEqual(self.hits('    V=0.2.19 S=canvas D=x\n    V=0.1.14 S=fishmarket\n'), [])

    def test_a_stale_service_pin_is_named(self):
        found = self.hits('    V=0.2.18 S=canvas\n')
        self.assertEqual(found, ['boring-services/README.md:1: canvas 0.2.18, the release set says 0.2.19'])

    def test_a_service_missing_from_the_set_is_named(self):
        self.assertIn('no sourcecache-d365 version', self.hits('    V=0.1.18 S=sourcecache-d365\n')[0])


class DocAnchorTests(unittest.TestCase):
    """check_docs: a link's #anchor must name a heading of the page it points at."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: subprocess.run(['rm', '-rf', str(self.tmp)], check=True))
        docs.anchors.cache_clear()
        self.other = self.tmp / 'boring-mailstack'
        self.other.mkdir()
        (self.other / 'README.md').write_text(
            '# boring-mailstack\n\n## Try it with fictional mail\n\n## Notes\n\n## Notes\n'
            '\n## [Using](docs/USING.md) `it`\n\n<a id="kept"></a>\n\n```\n## not a heading\n```\n')
        self.page = self.tmp / 'page.md'

    def hits(self, text):
        self.page.write_text(text)
        return docs.doc_link_hits(self.page, self.tmp, 'page.md', {'boring-mailstack': self.other})

    def test_repository_anchor_must_name_a_readme_heading(self):
        base = 'https://github.com/the-boring-crocodile/boring-mailstack'
        self.assertEqual(self.hits(f'[a]({base}#try-it-with-fictional-mail)'), [])
        self.assertIn('names no heading #try-it', self.hits(f'[a]({base}#try-it)')[0])

    def test_repeats_links_in_headings_explicit_ids_and_fences(self):
        base = 'https://github.com/the-boring-crocodile/boring-mailstack/blob/main/README.md'
        for good in ('notes', 'notes-1', 'using-it', 'kept'):
            self.assertEqual(self.hits(f'[a]({base}#{good})'), [], good)
        for bad in ('notes-2', 'not-a-heading'):
            self.assertEqual(len(self.hits(f'[a]({base}#{bad})')), 1, bad)

    def test_same_page_and_relative_anchors(self):
        (self.tmp / 'other.md').write_text('# Other\n\n## Step two\n')
        self.assertEqual(self.hits('# Here\n\n[a](#here) [b](other.md#step-two)'), [])
        self.assertEqual(len(self.hits('# Here\n\n[a](#gone) [b](other.md#step-three)')), 2)

    def test_repository_without_checkout_is_not_judged(self):
        self.assertEqual(self.hits('[a](https://github.com/the-boring-crocodile/unknown#x)'), [])


if __name__ == '__main__':
    unittest.main()
