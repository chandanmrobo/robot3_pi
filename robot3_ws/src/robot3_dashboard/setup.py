from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot3_dashboard'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        # Package index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # Package manifest
        ('share/' + package_name, ['package.xml']),

        # Install launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),

        # Install storage directory (empty JSON logs)
        (os.path.join('share', package_name, 'storage'), glob('robot3_dashboard/storage/*.json')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chandan',
    maintainer_email='chandan.m.reddy21@gmail.com',
    description='Robot3 Dashboard backend for logging and analytics.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # ROS2 Executable: dashboard_node
            'dashboard_node = robot3_dashboard.dashboard_node:main',
        ],
    },
)
