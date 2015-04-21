from setuptools import setup, find_packages

setup(name='blockmodel',
    version='1.0.0',
    description='Converts Minecraft models to 3D models',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7.6',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: MIT License'
    ],
    author='Paul Harter',
    author_email='username: paul, domain: glowinthedark.co.uk',
    install_requires=['nbt', 'jinja2'],
    packages=find_packages('src'),
    package_data={'': ['*.csv', '*.mtl', '*.obj', '*.x3d', '*.png', '*.xml']},
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False)