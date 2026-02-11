from setuptools import setup

package_name = 'robot3_detection_bridge'

setup(
    name=package_name,
    version='0.0.2',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        # Launch folder (if you add one later)
        ('share/' + package_name + '/launch',
            ['launch/detection_bridge.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chandan',
    maintainer_email='chandan.m.reddy21@gmail.com',
    description='Forward Robot2 detection to UI & UI detection mode to Robot2',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            # Existing bridge
            'detection_bridge_node = robot3_detection_bridge.detection_bridge_node:main',

            # ⭐ NEW bridge for plant/bird mode
            'detection_mode_bridge = robot3_detection_bridge.detection_mode_bridge:main',
        ],
    },
)
