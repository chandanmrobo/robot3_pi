from setuptools import find_packages, setup

package_name = 'robot3_sensors'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        # Install launch file
        ('share/' + package_name + '/launch',
            ['launch/sensors.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='chandan',
    maintainer_email='chandan@example.com',
    description='Sensor monitoring package for robot3 (DHT11 + Soil Moisture)',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'sensor_node = robot3_sensors.sensor_node:main',
        ],
    },
)
