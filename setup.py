from setuptools import setup, find_packages

setup(
    name='extract_cp',
    version='2.1.0',
    description='Fetal brain MRI CP surface extraction using CIVET marching-cubes',
    author='Jennings Zhang',
    author_email='Jennings.Zhang@childrens.harvard.edu',
    url='https://github.com/FNNDSC/pl-fetal-surface-extract',
    packages=find_packages(exclude=['tests']),
    install_requires=['chris_plugin', 'loguru', 'pycivet', 'pybicpl', 'numpy'],
    license='MIT',
    entry_points={
        'console_scripts': [
            'extract_cp = extract_cp.__main__:main'
        ]
    },
    scripts=['scripts/chamfer.sh'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    extras_require={
        'none': [],
        'dev': [
            'pytest~=7.1'
        ]
    }
)
