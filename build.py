import os
from cpt.packager import ConanMultiPackager


if __name__ == "__main__":
    os.environ["CONAN_REMOTES"]="https://api.bintray.com/conan/czoido/conan-packages@True@czoido-bintray"
    builder = ConanMultiPackager(build_policy="missing")
    builder.add_common_builds()
    builder.run()
