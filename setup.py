from setuptools import find_packages, setup


def get_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="WinGrab",
    version="0.0.1a2",
    url="https://github.com/JezaChen/WinGrab",
    author="Jianzhang Chen",
    author_email="jezachen@163.com",
    license="MIT",
    description="WinGrab: A simple tool to get the PID of the window under the cursor.",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("*examples", "*examples.*")),
    python_requires=">=3.7, <4",
    keywords="win32api windows gui",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
    ],
    package_data={"wingrab": ["cursor.cur",]},
)
