from setuptools import setup, find_packages
import os

package_name = 'robot3_seeds'

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
            ['launch/seeds.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='chandan',
    maintainer_email='chandan@example.com',
    description='Seed dispenser control package for Robot 3',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'seed_node = robot3_seeds.seed_node:main',
        ],
    },
)
