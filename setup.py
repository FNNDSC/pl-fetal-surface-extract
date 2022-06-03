from setuptools import setup

setup(
    name='extract_cp',
    version='1.0.0',
    description='Fetal brain MRI CP surface extraction using CIVET marching-cubes',
    author='Jennings Zhang',
    author_email='Jennings.Zhang@childrens.harvard.edu',
    url='https://github.com/FNNDSC/pl-fetal-cp-surface-extract',
    packages=['extract_cp'],
    install_requires=['chris_plugin'],
    license='MIT',
    python_requires='>=3.10.4',
    entry_points={
        'console_scripts': [
            'extract_cp = extract_cp.__main__:main'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
