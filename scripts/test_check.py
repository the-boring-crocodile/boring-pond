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


RELEASE = """import argparse, json, os, sys
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--common-wheels', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--python-version')
p.add_argument('--target')
p.add_argument('--services-root', type=Path)
args = p.parse_args()
name = Path.cwd().name
assert (args.common_wheels / 'VERSION').read_text() == Path('expected').read_text()
bundle = None
if name == 'boring-pondnt':
    assert args.python_version is None and args.target is None
    bundle = (args.services_root / 'bundle').read_text()
    assert bundle == 'accepted bundle'
else:
    assert args.python_version == '%d.%d' % sys.version_info[:2]
    assert args.services_root is None
    assert args.target == ('linux' if name == 'boring-services' else None)
if name == 'boring-services':
    assert Path('bundle').read_text() == 'current, incompatible bundle'
with open(os.environ['FAMILY_TEST_AUDIT'], 'a') as f:
    f.write(json.dumps(['release', name, sys.executable, args.python_version, args.target, bundle]) + '\\n')
args.out.mkdir()
(args.out / 'artifact').write_text('built by the owner')
raise SystemExit(8 if os.environ.get('FAMILY_TEST_RELEASE_FAIL') == name else 0)
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
        write(self.common, 'packages/boring-registry/pyproject.toml', '[project]\nname = "boring-registry"\n')
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
            write(root, 'scripts/build.py', RELEASE)
            if name in ('crocodile', 'pirates'):
                write(root, 'tests/fixtures/admin-list.json', json.dumps({'ponds': ['pond', 'garden'], 'pirates': {'parrot': 1300}}))
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
        self.assertEqual([e[0] for e in self.events()], ['owner', 'owner', 'release', 'release'])
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

    def test_common_packages_come_from_the_selected_commit(self):
        root = self.family / 'boring-pirates'
        for name in ('boring-outcomes', 'boring-future-kit'):
            with self.subTest(name=name):
                manifest = f'packages/{name}/pyproject.toml'
                write(self.common, manifest, f'[project]\nname = "{name}"\n')
                selected = commit(self.common)
                write(root, '.common-ref', selected + '\n')
                # Neither HEAD nor the working tree declares this package now.
                (self.common / manifest).unlink()
                commit(self.common)
                write(root, 'requirements.lock', f'boring-registry==0.7.10\n{name}==0.7.8\n')
                self.assertIn('the locks pin 0.7.10, 0.7.8', refs.problems(root.name)[0])
                write(root, 'requirements.lock', f'boring-registry==0.7.10\n{name}==0.7.10\n')
                self.assertEqual(refs.problems(root.name), [])

    def test_names_check_is_skipped_without_private_records(self):
        result, output = self.run_check('--only', 'names')
        self.assertEqual(result, 0)
        self.assertIn('boring-records absent: skipped', output)

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

    def test_release_builds_run_once_on_first_python_and_use_checked_inputs(self):
        result, output = self.run_check('--only', *runner.CONSUMERS,
                                        '--python', sys.executable, sys.executable)
        self.assertEqual(result, 0)
        builds = [e for e in self.events() if e[0] == 'release']
        self.assertEqual([e[1] for e in builds], [runner.CHECKS[n][0] for n in runner.CONSUMERS])
        self.assertTrue(all(e[2] == sys.executable for e in builds))
        self.assertEqual(len([e for e in self.events() if e[0] == 'owner']), 8)
        for name in runner.CONSUMERS:
            self.assertIn(f'build-{name}', output)
        self.assert_untouched()

    def test_each_release_failure_fails_the_family_and_other_builds_still_run(self):
        for failed in runner.CONSUMERS:
            with self.subTest(failed=failed):
                self.audit.unlink(missing_ok=True)
                with patch.dict(os.environ, FAMILY_TEST_RELEASE_FAIL=runner.CHECKS[failed][0]):
                    result, output = self.run_check('--only', *runner.CONSUMERS)
                self.assertEqual(result, 1)
                self.assertIn('FAILED (8)', output)
                self.assertEqual(len([e for e in self.events() if e[0] == 'release']), 4)
                self.assert_untouched()

    def test_ci_pythons_without_uv_is_refused_before_effects(self):
        with patch.dict(os.environ, {'UV': '', 'PATH': ''}):
            result, output = self.run_check('--only', 'crocodile', '--ci-pythons')
        self.assertEqual(result, 1)
        self.assertIn('--ci-pythons needs uv', output)
        self.assertEqual(self.events(), [])


class AdminInventoryContractTests(unittest.TestCase):
    def test_mismatched_or_missing_consumer_example_stops_family_preflight(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "FAMILY", Path(tmp)):
            for repo in ("boring-crocodile", "boring-pirates"):
                write(Path(tmp) / repo, "tests/fixtures/admin-list.json", '{"ponds":["pond"],"pirates":{}}')
            runner.admin_inventory_contract()
            consumer = Path(tmp) / "boring-pirates/tests/fixtures/admin-list.json"
            consumer.write_text('{"ponds":["different"],"pirates":{}}')
            with self.assertRaisesRegex(ValueError, "examples differ"):
                runner.inputs(["pirates"], None)
            consumer.unlink()
            with self.assertRaisesRegex(ValueError, "missing or invalid"):
                runner.inputs(["pirates"], None)


class ReleasePlaceholderTests(unittest.TestCase):
    """Download recipes identify the published component and version."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'boring-pond'
        self.repo.mkdir()
        subprocess.run(['git', 'init', '-q'], cwd=self.repo, check=True)

    def hits(self, text, rel='README.md'):
        page = self.repo / rel
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(text)
        subprocess.run(['git', 'add', '--', rel], cwd=self.repo, check=True)
        return docs.release_pin_hits(self.repo)

    def test_placeholders_need_no_release_table(self):
        self.assertEqual(self.hits('    V=VERSION S=canvas\n    CROCODILE=VERSION PIRATES=VERSION CANVAS=VERSION\n'), [])

    def test_bash_release_pin_must_match_the_named_recipe(self):
        rel = 'docs/getting-started.md'
        self.assertEqual(self.hits('    V=0.5.0\n', rel), [])
        found = self.hits('    V=0.5.0rc21\n', rel)
        self.assertEqual(found, [f'boring-pond/{rel}:1: V=0.5.0rc21, the release set says 0.5.0'])

    def test_quoted_and_powershell_candidate_pins_are_named(self):
        for line in ('V="1.2.3"', "$v = '1.2.3rc1'", "$tag = 'v1.2.3-rc.1'",
                     'CROCODILE=v1.2.3-rc.1'):
            with self.subTest(line=line):
                self.assertEqual(len(self.hits(line)), 1)

    def test_service_recipe_is_checked_without_a_service_roster(self):
        self.assertEqual(len(self.hits('    V=1.2.3 S=some-new-service\n')), 1)

    def test_literal_release_download_url_is_named(self):
        for tag in ('v1.2.3', 'canvas-v1.2.3'):
            with self.subTest(tag=tag):
                self.assertEqual(len(self.hits('curl https://github.com/example/project/releases/download/' + tag + '/asset')), 1)

    def test_history_dependencies_and_host_versions_are_not_download_pins(self):
        self.assertEqual(self.hits('Historical Crocodile 0.4.21.\nCommon >=0.8,<0.9.\nglibc 2.39 and port 18520.\n'), [])

    def test_variable_download_url_is_allowed(self):
        self.assertEqual(self.hits('curl "$gh/releases/download/v$V/$f"\n'), [])

    def test_service_pins_follow_the_service_name(self):
        self.repo.rename(self.repo.with_name('boring-services'))
        self.repo = self.repo.with_name('boring-services')
        self.assertEqual(self.hits('    V=0.2.0 S=mcp-ferry\n    V=0.3.0 S=canvas\n'), [])
        self.assertEqual(len(self.hits('    V=0.3.0 S=mcp-ferry\n')), 1)

    def test_windows_tag_uses_the_release_prefix(self):
        self.repo.rename(self.repo.with_name('boring-pondnt'))
        self.repo = self.repo.with_name('boring-pondnt')
        rel = 'docs/INSTALL.md'
        self.assertEqual(self.hits("    $v = '0.3.0'; $tag = 'v0.3.0'\n", rel), [])
        self.assertEqual(len(self.hits("    $v = '0.3.0'; $tag = '0.3.0'\n", rel)), 1)


class UnicodeEscapeTests(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: subprocess.run(['rm', '-rf', str(self.repo)], check=True))
        subprocess.run(['git', 'init', '-q'], cwd=self.repo, check=True)

    def hits(self, text):
        page = self.repo / 'README.md'
        page.write_text(text, encoding='utf-8')
        subprocess.run(['git', 'add', '--', 'README.md'], cwd=self.repo, check=True)
        return docs.unicode_hits(self.repo)

    def test_accidental_escape_is_named_with_its_line(self):
        found = self.hits('Title\n' + r'release\u2019s notes' + '\n')
        self.assertEqual(len(found), 1)
        self.assertIn('README.md:2: literal Unicode escape in Markdown', found[0])

    def test_code_blocks_are_checked_too(self):
        found = self.hits('~~~json\n' + r'{"text":"\u2019"}' + '\n~~~\n')
        self.assertEqual(len(found), 1)

    def test_real_unicode_character_is_accepted(self):
        self.assertEqual(self.hits('The release’s notes.\n'), [])

    def test_extra_markdown_page_uses_the_same_guard(self):
        page = self.repo / 'extra.md'
        page.write_text(r'wrong \u0027', encoding='utf-8')
        self.assertEqual(len(docs.markdown_escape_hits(page, 'extra.md')), 1)


class DiagramCaptionTests(unittest.TestCase):
    """Both rendered themes have versionless captions; dated maps keep their evidence label."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'boring-pond'
        (self.repo / 'docs').mkdir(parents=True)
        subprocess.run(['git', 'init', '-q'], cwd=self.repo, check=True)

    def write_svg(self, stem, subtitle, note=''):
        (self.repo / 'docs' / (stem + '.svg')).write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><text>Title</text>'
            f'<text>{subtitle}</text><text>{note}</text></svg>')
        subprocess.run(['git', 'add', '--', 'docs/' + stem + '.svg'], cwd=self.repo, check=True)

    def pair(self, subtitle, note=''):
        for stem in ('example', 'example-dark'):
            self.write_svg(stem, subtitle, note)

    def test_versionless_pair_needs_no_manifest_or_release_table(self):
        self.pair('Container view · source architecture')
        self.assertEqual(docs.diagram_version_hits(self.repo), [])

    def test_only_versioned_dark_caption_is_named(self):
        self.pair('Container view · Crocodile')
        self.write_svg('example-dark', 'Container view · Crocodile 1.2.3')
        self.assertEqual(docs.diagram_version_hits(self.repo),
                         ['boring-pond/docs/example-dark.svg: release number in diagram caption'])

    def test_split_graphviz_caption_and_candidates_are_checked(self):
        self.pair('Dynamic view', 'Crocodile 1.2.3rc1')
        self.assertEqual(len(docs.diagram_version_hits(self.repo)), 2)

    def test_malformed_tracked_svg_is_reported(self):
        self.write_svg('broken', 'view')
        (self.repo / 'docs' / 'broken.svg').write_text('<svg>')
        self.assertIn('cannot read diagram', docs.diagram_version_hits(self.repo)[0])

    def test_our_site_has_no_special_caption_rule(self):
        self.write_svg('our-site', 'Topology')
        self.assertEqual(docs.diagram_version_hits(self.repo), [])
        self.write_svg('our-site', 'Topology 1.2.3')
        self.assertEqual(docs.diagram_version_hits(self.repo),
                         ['boring-pond/docs/our-site.svg: release number in diagram caption'])


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


class UpgradeCommandTest(unittest.TestCase):
    def test_published_blocks_stop_at_download_unpack_preflight_and_deploy_failures(self):
        page = Path(__file__).resolve().parents[1] / 'docs/updating.md'
        blocks, current = [], []
        for line in [*page.read_text().splitlines(), '']:
            if line.startswith('    '):
                current.append(line[4:])
            elif current:
                blocks.append('\n'.join(current))
                current = []
        download, = [b for b in blocks if 'get()' in b]
        preflight, = [b for b in blocks if '/deploy --check' in b and 'set -eu' not in b]
        deploy, = [b for b in blocks if 'boring-pirates-$PIRATES/deploy --check' in b and 'set -eu' in b]
        prefix = r'''
record() { printf '%s|\n' "$*" >> "$AUDIT"; case "$*|" in *"$FAIL"*) return 7;; esac; }
curl() { record "curl $*"; }
sha256sum() { record "sha256sum $*"; }
sudo() { record "sudo $*"; }
mkdir() { :; }
cd() { :; }
CROCODILE=0.5.0 PIRATES=0.4.0 CANVAS=0.3.0
'''
        cases = [(download, 'curl -fLO https://github.com/the-boring-crocodile/boring-crocodile/',
                  'sudo tar', 'download'),
                 (download, 'sudo tar xzf boring-crocodile-', 'sudo tar xzf boring-pirates-', 'first unpack'),
                 (download, 'sudo tar xzf boring-pirates-', 'sudo tar xzf boring-canvas-', 'second unpack'),
                 (preflight, 'boring-crocodile-0.5.0/deploy --check', 'boring-pirates-0.4.0', 'preflight'),
                 (deploy, 'boring-crocodile-0.5.0/deploy|', 'boring-pirates-0.4.0', 'first deploy'),
                 (deploy, 'boring-pirates-0.4.0/deploy --check', 'boring-pirates-0.4.0/deploy|', 'Pirates check'),
                 (deploy, 'boring-pirates-0.4.0/deploy|', 'boring-canvas-0.3.0/deploy', 'second deploy')]
        with tempfile.TemporaryDirectory() as tmp:
            audit = Path(tmp) / 'calls'
            for block, fail, later, label in cases:
                with self.subTest(stage=label):
                    audit.write_text('')
                    run = subprocess.run(['bash'], input=prefix + block, text=True,
                                         capture_output=True, env=dict(os.environ, AUDIT=str(audit), FAIL=fail))
                    self.assertEqual(run.returncode, 7, run.stderr)
                    self.assertIn(fail, audit.read_text())
                    self.assertNotIn(later, audit.read_text())


if __name__ == '__main__':
    unittest.main()
