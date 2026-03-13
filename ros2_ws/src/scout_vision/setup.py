from setuptools import setup

package_name = "scout_vision"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Home Scout Contributors",
    maintainer_email="you@example.com",
    description="Computer vision for Home Scout",
    license="MIT",
    entry_points={
        "console_scripts": [
            "camera_node = scout_vision.camera_node:main",
            "detector_node = scout_vision.detector_node:main",
            "tracker_node = scout_vision.tracker_node:main",
        ],
    },
)
