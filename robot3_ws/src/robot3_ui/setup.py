from setuptools import setup
import os
from glob import glob

package_name = 'robot3_ui'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    package_dir={'': '.'},

    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
        (os.path.join('share', package_name, 'ui_build'),
            glob('robot3_ui/ui_build/*.*')),
        (os.path.join('share', package_name, 'ui_build/assets'),
            glob('robot3_ui/ui_build/assets/*.*')),
    ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chandan',
    maintainer_email='chandan@example.com',
    description='UI Server and ROS2 Bridge',
    license='Apache-2.0',

    entry_points={
        'console_scripts': [
            'ui_server = robot3_ui.ui_server:main',
        ],
    },
)
