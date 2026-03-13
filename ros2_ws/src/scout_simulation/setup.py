import os
from glob import glob

from setuptools import setup

package_name = "scout_simulation"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Home Scout Contributors",
    maintainer_email="you@example.com",
    description="Gazebo simulation for Home Scout",
    license="MIT",
)
