from setuptools import find_packages, setup

package_name = 'robot3_core'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        # Install launch file
        ('share/' + package_name + '/launch',
            ['launch/core.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chandan',
    maintainer_email='chandan@example.com',
    description='Central launch package for robot3 (battery + sensors + UI)',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)