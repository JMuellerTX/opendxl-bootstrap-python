import os
import shutil
import sys
import tempfile
import textwrap
import unittest

from dxlbootstrap._resources import package_files


class ApplicationConfigFilesTest(unittest.TestCase):
    """
    Regression tests for the creation of the application configuration
    files from the ``_config/app`` directory of the application package
    (previously implemented with the deprecated ``pkg_resources`` API).
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="dxlbootstrap_app_")
        package_dir = os.path.join(self.temp_dir, "dxlbootstraptestapp")
        os.makedirs(os.path.join(package_dir, "_config", "app", "subdir"))
        with open(os.path.join(package_dir, "__init__.py"), "w") as handle:
            handle.write("")
        with open(os.path.join(package_dir, "app.py"), "w") as handle:
            handle.write(textwrap.dedent("""
                from dxlbootstrap.app import Application

                class TestApplication(Application):
                    def __init__(self, config_dir):
                        super(TestApplication, self).__init__(config_dir, "test.config")
                """))
        app_config_dir = os.path.join(package_dir, "_config", "app")
        for name in ("test.config", "logging.config", "dxlclient.config",
                     "ignored.py", "ignored.pyc"):
            with open(os.path.join(app_config_dir, name), "w") as handle:
                handle.write("[Section]\nname=" + name + "\n")
        sys.path.insert(0, self.temp_dir)

    def tearDown(self):
        sys.path.remove(self.temp_dir)
        sys.modules.pop("dxlbootstraptestapp", None)
        sys.modules.pop("dxlbootstraptestapp.app", None)
        shutil.rmtree(self.temp_dir)

    def test_package_files_resolves_module_to_package_dir(self):
        from dxlbootstraptestapp import app # pylint: disable=import-error
        self.assertTrue(
            package_files(app.__name__).joinpath("_config/app").is_dir())
        self.assertTrue(
            package_files("dxlbootstraptestapp").joinpath("_config").is_dir())

    def test_config_files_created_from_package(self):
        from dxlbootstraptestapp.app import TestApplication # pylint: disable=import-error
        config_dir = os.path.join(self.temp_dir, "config")
        app = TestApplication(config_dir)
        app._validate_config_files() # pylint: disable=protected-access
        created = sorted(os.listdir(config_dir))
        self.assertEqual(
            ["dxlclient.config", "logging.config", "test.config"], created)
        with open(os.path.join(config_dir, "test.config")) as handle:
            self.assertEqual("[Section]\nname=test.config\n", handle.read())

    def test_logging_config_not_created_in_existing_config_dir(self):
        from dxlbootstraptestapp.app import TestApplication # pylint: disable=import-error
        config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(config_dir)
        with open(os.path.join(config_dir, "existing.config"), "w") as handle:
            handle.write("")
        app = TestApplication(config_dir)
        app._validate_config_files() # pylint: disable=protected-access
        self.assertFalse(
            os.path.exists(os.path.join(config_dir, "logging.config")))
        self.assertTrue(os.path.exists(os.path.join(config_dir, "test.config")))
