from setuptools import setup

package_name = "scout_nav"

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
    description="Navigation for Home Scout",
    license="MIT",
    entry_points={
        "console_scripts": [
            "base_driver_node = scout_nav.base_driver_node:main",
            "odometry_node = scout_nav.odometry_node:main",
            "patrol_node = scout_nav.patrol_node:main",
            "slam_node = scout_nav.slam_node:main",
        ],
    },
)
