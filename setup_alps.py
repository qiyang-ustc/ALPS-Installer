import os
import subprocess
import sys

import colorama
import platform
from setuptools import setup, find_packages
from setuptools.command.install import install
from packaging import version

from colorama import Fore, Style, init
init() # init colorama

install_path = "./ALPSLib"

class ALPSInstall(install):
    def run(self):
        try:
            os.makedirs(install_path, exist_ok=True)
            print(Fore.GREEN+f"Directory {install_path} is ready.")
        except OSError as e:
            print(Fore.RED+f"Error creating directory {install_path}: {e}")
            raise

        print(f"Set up ALPS into {os.path.abspath(install_path)}")
        os.chdir(os.path.dirname(__file__)+"/ALPSLib")

        self.install_dependencies()
        self.download_boost()
        self.build_alps()
        install.run(self)

    def install_dependencies(self):
        print(Fore.BLUE +"Installing Python dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy", "scipy"])

    def download_boost(self):
        print(Fore.BLUE +"Downloading and unpacking Boost...")

        boost_version = "1.81.0"
        boost_filename = f"boost_{boost_version.replace('.', '_')}.tar.gz"
        boost_url = f"https://archives.boost.io/release/{boost_version}/source/{boost_filename}"

        try:
            if not os.path.exists(boost_filename):
                subprocess.check_call(["wget", boost_url])
            else:
                print(Fore.GREEN +f"{boost_filename} already exists, skipping download.")

            if not os.path.exists(f"boost_{boost_version.replace('.', '_')}"):
                subprocess.check_call(["tar", "-xzf", boost_filename])
            else:
                print(Fore.GREEN +f"Boost directory already exists, skipping extraction.")

            self.boost_dir = os.path.abspath(f"boost_{boost_version.replace('.', '_')}")
            print(f"Load Boost DIR {self.boost_dir}")

        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

    def build_alps(self):
        print("Cloning ALPS repository...")
        repo_path = "alps-src"

        try:
            if os.path.exists(repo_path):
                print(Fore.GREEN +"ALPS repository already exists. Attempting to update...")
                os.chdir(repo_path)
                subprocess.check_call(["git", "pull"])
                os.chdir("..")  # 返回到原始目录
                print(Fore.GREEN +"ALPS repository updated successfully.")
            else:
                print(Fore.GREEN +"Cloning ALPS repository...")
                subprocess.check_call(["git", "clone", "https://github.com/alpsim/ALPS", repo_path])
                print(Fore.GREEN +"ALPS repository cloned successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during git operations: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

        print("Configuring ALPS build...")
        self.setup_environment()
        install_dir = os.path.join(self.install_lib, "alps")
        build_dir = "alps-build"
        os.makedirs(build_dir, exist_ok=True)

        LD_LIBRARY_PATH = os.environ.get("LD_LIBRARY_PATH")
        if LD_LIBRARY_PATH is None:
            LD_LIBRARY_PATH = os.path.abspath(".")

        cmake_args = [
            "cmake",
            "-S", "alps-src",
            "-B", build_dir,
            f"-DCMAKE_INSTALL_PREFIX={install_dir}",
            f"-DBoost_ROOT_DIR={self.boost_dir}",
            "-DCMAKE_CXX_STANDARD=11",
            "-DCMAKE_CXX_FLAGS=-std=c++11 -stdlib=libc++ -DBOOST_NO_AUTO_PTR -DBOOST_FILESYSTEM_NO_CXX20_ATOMIC_REF",
            f"-DCMAKE_LIBRARY_PATH={self.boost_dir}"+f"/stage/lib:{LD_LIBRARY_PATH}"
                ]
        subprocess.check_call(cmake_args)

        if not input(f"Confirm Building Configurations? (y/n): ").lower().strip() == 'y':
            print("Exiting due to unexpected Configuration.")
            sys.exit(1)

        print("Building ALPS...")
        subprocess.check_call(["cmake", "--build", build_dir, "-j", str(os.cpu_count())])

        print("Running ALPS tests...")
        subprocess.check_call(["cmake", "--build", build_dir, "-t", "test"])

        print("Installing ALPS...")
        subprocess.check_call(["cmake", "--install", build_dir])

    def setup_environment(self):
        if platform.system() == "Darwin":  # 检查是否为 macOS
            print("Detected macOS. Setting up environment...")

            os.environ["CC"] = "clang"
            os.environ["CXX"] = "clang++"

            # 检查 MacOSX14.sdk 是否存在
            sdk_path = "/Library/Developer/CommandLineTools/SDKs/MacOSX14.sdk"
            if os.path.exists(sdk_path):
                os.environ["SDKROOT"] = sdk_path
                print(f"Set SDKROOT to {sdk_path}")
            else:
                print("MacOSX14.sdk not found. Trying to find the latest SDK...")

                # 尝试找到最新的 SDK
                sdk_base_path = "/Library/Developer/CommandLineTools/SDKs"
                if os.path.exists(sdk_base_path):
                    sdks = [d for d in os.listdir(sdk_base_path) if d.startswith("MacOSX") and d.endswith(".sdk")]
                    if sdks:
                        latest_sdk = max(sdks)
                        os.environ["SDKROOT"] = os.path.join(sdk_base_path, latest_sdk)
                        print(f"Set SDKROOT to {os.environ['SDKROOT']}")
                    else:
                        print("No MacOSX SDK found. Please check your Xcode installation.")
                else:
                    print("SDK directory not found. Please check your Xcode installation.")

            # 打印当前的 SDKROOT 值以确认
            print(f"Current SDKROOT: {os.environ.get('SDKROOT', 'Not set')}")


setup(
    name="alps",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
    ],
    cmdclass={
        'install': ALPSInstall,
    },
)
