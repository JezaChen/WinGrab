from setuptools import find_packages, setup

setup(
    name="WinGrab",
    version="0.1",
    url="https://github.com/JezaChen/WinGrab",
    author="Chen Jianzhang",
    author_email="jezachen@163.com",
    description="WinGrab: A simple tool to get the PID of the window under the cursor.",
    packages=find_packages(exclude=("*examples", "*examples.*")),
    python_requires=">=3.7, <4",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
    ]
)
