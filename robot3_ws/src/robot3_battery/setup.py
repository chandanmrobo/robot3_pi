from setuptools import setup, find_packages

package_name = 'robot3_battery'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        ('share/' + package_name + '/launch',
            ['launch/battery.launch.py']),

        ('share/' + package_name + '/resource',
            ['resource/' + package_name]),
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='chandan',
    maintainer_email='chandan@example.com',
    description='Battery monitor for robot3',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'battery_node = robot3_battery.battery_node:main',
        ],
    },
)
