import os
import shutil
from conans import ConanFile, tools
from waf_environment import WafBuildEnvironment


class PythonRequires(ConanFile):
    name = "waf-build-helper"
    version = "0.1"
    exports = "waf_environment.py"


def get_conanfile():
    class BaseConanFile(ConanFile):

        def build_requirements(self):
            self.build_requires("waf_installer/2.0.17@czoido/testing")

        def package_info(self):
            self.cpp_info.libs = [self.name]

    return BaseConanFile
