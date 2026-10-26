import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('links', Path(__file__).resolve().parents[1] / 'scripts/validate_local_links.py')
links = importlib.util.module_from_spec(spec)
spec.loader.exec_module(links)


class LocalLinkChecks(unittest.TestCase):
    def check_links(self, markdown, files=None, tracked=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text(markdown)
            for name in files or []:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text('example')
            return links.validate_links(root, tracked or ['README.md'] + (files or []))

    def test_nested_chinese_encoded_paths_and_titles(self):
        count, errors = self.check_links('[指南](docs/%E6%8C%87%E5%8D%97.md#步骤 "说明")\n[空格](<docs/a b.md>)\n[目录](docs/)', ['docs/指南.md', 'docs/a b.md'])
        self.assertEqual(count, 3)
        self.assertEqual(errors, [])

    def test_local_untracked_file_does_not_hide_broken_github_link(self):
        _, errors = self.check_links('[网站](sites/app/README.md)', ['sites/app/README.md'], ['README.md'])
        self.assertEqual(len(errors), 1)
        self.assertIn('untracked', errors[0])

    def test_deleted_target_fails(self):
        _, errors = self.check_links('[坏链接](missing.md)')
        self.assertEqual(len(errors), 1)

    def test_external_anchors_and_code_examples_are_skipped(self):
        count, errors = self.check_links('[外部](https://example.com/a) [页内](#标题)\n```md\n[示例](missing.md)\n```\n`[示例](absent.md)`')
        self.assertEqual((count, errors), (0, []))

    def test_reference_links_and_images(self):
        count, errors = self.check_links('[指南][a]\n![图](docs/chart.svg)\n[a]: docs/guide.md "标题"', ['docs/chart.svg', 'docs/guide.md'])
        self.assertEqual((count, errors), (2, []))

    def test_reference_typo_fails(self):
        _, errors = self.check_links('[指南][absent]')
        self.assertEqual(len(errors), 1)

    def test_outside_repository_path_fails(self):
        _, errors = self.check_links('[外部文件](../outside.md)')
        self.assertEqual(len(errors), 1)
        self.assertIn('outside-repository', errors[0])

    def test_relative_to_document_and_root_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'docs').mkdir()
            (root / 'README.md').write_text('index')
            (root / 'docs/guide.md').write_text('[返回](../README.md) [根目录](/README.md)')
            self.assertEqual(links.validate_links(root, ['README.md', 'docs/guide.md']), (2, []))


if __name__ == '__main__':
    unittest.main()
