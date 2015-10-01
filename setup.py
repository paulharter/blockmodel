from setuptools import setup, find_packages

setup(name='blockmodel',
    version='1.0.1',
    description='Converts Minecraft models to 3D models',
    url='https://github.com/paulharter/blockmodel',
    author='Paul Harter',
    author_email='paul@glowinthedark.co.uk',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License'
    ],
    keywords='minecraft 3D printing',
    install_requires=['nbt', 'jinja2'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False)


