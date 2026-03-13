from setuptools import setup

package_name = "scout_voice"

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
    description="Voice interface for Home Scout",
    license="MIT",
    entry_points={
        "console_scripts": [
            "wake_word_node = scout_voice.wake_word_node:main",
            "asr_node = scout_voice.asr_node:main",
            "tts_node = scout_voice.tts_node:main",
            "conversation_node = scout_voice.conversation_node:main",
        ],
    },
)
