from setuptools import setup

package_name = "scout_faces"

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
    description="Face recognition for Home Scout",
    license="MIT",
    entry_points={
        "console_scripts": [
            "enrollment_node = scout_faces.enrollment_node:main",
            "recognition_node = scout_faces.recognition_node:main",
            "greeting_node = scout_faces.greeting_node:main",
        ],
    },
)
