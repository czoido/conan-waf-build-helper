import os
import shutil
from conans import ConanFile, tools
from conans.client.tools.oss import args_to_string
from conans.util.files import normalize, save
from conans.client.build.compiler_flags import libcxx_flag
from conans.client.build.cppstd_flags import cppstd_flag
from conans.errors import ConanException


class WafBuildEnvironment(object):

    def __init__(self, conanfile):
        self._conanfile = conanfile
        self._settings = conanfile.settings
        self._os_build = self._ss("os_build")
        self._arch_build = self._ss("arch_build")
        self._os = self._ss("os")
        self._os_subsystem = self._ss("os.subsystem")
        self._arch = self._ss("arch")
        self._compiler = self._ss("compiler")
        self._compiler_version = self._ss("compiler.version")
        self._compiler_threads = self._ss("compiler.threads")
        self._compiler_libcxx = self._ss("compiler.libcxx")
        self._compiler_cppstd = self._ss("compiler.cppstd")
        self._build_type = self._ss("build_type")
        # shared
        self._shared = self._so("shared")
        # fpic
        if self._os and "Windows" not in self._os:
            self._fpic = self._so("fPIC")
        # gcc
        self._compiler_threads = self._ss("compiler.threads")
        self._compiler_exception = self._ss("compiler.exception")
        # vs
        self._compiler_toolset = self._ss("compiler.toolset")
        self._compiler_runtime = self._ss("compiler.runtime")
        self._arch_conan2waf = {
            'x86': 'x86',
            'x86_64': 'x64'
        }

    def _gcc_ver_conan2waf(self, conan_version):
        version = [v for v in conan_version.split('.', 3)]
        while len(version) < 3:
            version.append('0')
        return "('{}', '{}', '{}')".format(version[0], version[1], version[2])

    def _toolchain_content(self):
        sections = []
        sections.append("def configure(conf):")
        if "Visual Studio" in self._compiler:
            # first we set the options for the compiler, then load
            sections.append("    conf.env.MSVC_VERSION = '{}'".format(
                self._compiler_version))
            try:
                sections.append("    conf.env.MSVC_TARGETS = '{}'".format(
                    self._arch_conan2waf[self._arch_build]))
            except KeyError:
                raise ConanException(
                    "Architecture  '%s' not supported" % self._arch_build)

            sections.append(
                "    conf.env.CXXFLAGS.append('/{}')".format(self._compiler_runtime))
            sections.append("    conf.load('msvc')")
        else:
            if "gcc" in self._compiler:
                sections.append("    conf.load('gcc')")
            elif "clang" in self._compiler:
                sections.append("    conf.load('clangxx')")
            else:
                sections.append("    conf.load('compiler_cxx')")

            sections.append("    conf.env.CC_VERSION = {}".format(
                self._gcc_ver_conan2waf(self._compiler_version)))

            cxxf = libcxx_flag(compiler=self._compiler,
                               libcxx=self._compiler_libcxx)
            sections.append("    conf.env.CXXFLAGS.append('{}')".format(cxxf))

            cppstdf = cppstd_flag(
                self._compiler, self._compiler_version, self._compiler_cppstd)
            sections.append(
                "    conf.env.CXXFLAGS.append('{}')".format(cppstdf))

        return "\n".join(sections)

    def _save_toolchain_file(self):
        filename = "waf_conan_toolchain.py"
        content = self._toolchain_content()
        output_path = self._conanfile.build_folder
        content = normalize(content)
        self._conanfile.output.info(
            "Waf Toolchain File created: %s" % (filename))
        save(os.path.join(output_path, filename),
             content, only_if_modified=True)

    # add all kinds of arguments that can be passed to waf via command line
    def configure(self):
        self._save_toolchain_file()
        self._run("waf configure")

    def build(self):
        self._run("waf build")

    def _run(self, command):
        self._conanfile.run(command)

    def _ss(self, setname):
        """safe setting"""
        return self._conanfile.settings.get_safe(setname)

    def _so(self, setname):
        """safe option"""
        return self._conanfile.options.get_safe(setname)
