import platform
from urllib.request import urlretrieve
import os
import subprocess as sp
import fnmatch
import shutil

from .common import run


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    os.environ.update(
        {
            "CIBW_BUILD": "cp36-macosx_x86_64 cp37-macosx_x86_64 cp38-macosx_x86_64 cp36-manylinux_x86_64 cp37-manylinux_x86_64 cp38-manylinux_x86_64 cp36-win_amd64 cp37-win_amd64 cp38-win_amd64",
            "CIBW_BEFORE_BUILD": "pip install -r procgen-build/requirements.txt && pip install -e procgen-build && python -u -m procgen_build.build_qt --output-dir /tmp/qt5",
            "CIBW_TEST_EXTRAS": "test",
            "CIBW_BEFORE_TEST": "pip install -r procgen-build/requirements.txt",
            # the --pyargs option causes pytest to use the installed procgen wheel
            "CIBW_TEST_COMMAND": "pytest --verbose --benchmark-disable --durations=16 --pyargs procgen",
            # this is where build-qt.py will put the files
            "CIBW_ENVIRONMENT": "PROCGEN_CMAKE_PREFIX_PATH=/tmp/qt5/qt/build/qtbase/lib/cmake/Qt5",
            # this is a bit too verbose normally
            # "CIBW_BUILD_VERBOSITY": "3",
        }
    )
    if platform.system() == "Linux":
        if "TRAVIS_TAG" in os.environ:
            # pass TRAVIS_TAG to the container so that it can build wheels with the correct version number
            os.environ["CIBW_ENVIRONMENT"] = (
                os.environ["CIBW_ENVIRONMENT"]
                + " TRAVIS_TAG=" + os.environ["TRAVIS_TAG"]
            )
        os.environ["CIBW_ENVIRONMENT"] = (
            os.environ["CIBW_ENVIRONMENT"]
            + f" CACHE_DIR=/host{os.getcwd()}/cache"
        )

    run("pip install cibuildwheel==1.4.1")
    run("cibuildwheel --output-dir wheelhouse")

    if platform.system() == "Linux":
        # copy the wheels outside of the docker container
        input_dir = "wheelhouse"
        output_dir = os.path.join("/host" + os.getcwd(), "wheelhouse")
        os.makedirs(output_dir, exist_ok=True)
        
        for filename in os.listdir(input_dir):
            src = os.path.join(input_dir, filename)
            dst = os.path.join(output_dir, filename)
            print(src, "=>", dst)
            shutil.copyfile(src, dst)


if __name__ == "__main__":
    main()
