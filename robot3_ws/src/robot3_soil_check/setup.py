from setuptools import find_packages, setup
import os

package_name = 'robot3_soil_check'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        # Register package with ament index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # Install package.xml
        ('share/' + package_name, ['package.xml']),

        # Install launch file
        (os.path.join('share', package_name, 'launch'),
            ['launch/soil_check.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chandan',
    maintainer_email='chandan@example.com',
    description='Publishes soil moisture check request to ESP32',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'soil_check_node = robot3_soil_check.soil_check_node:main',
        ],
    },
)
