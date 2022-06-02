from setuptools import setup

setup(
    name='chris-plugin-template',
    version='1.0.0',
    description='A ChRIS DS plugin template',
    author='FNNDSC',
    author_email='dev@babyMRI.org',
    url='https://github.com/FNNDSC/python-chrisapp-template',
    py_modules=['app'],
    install_requires=['chris_plugin'],
    license='MIT',
    python_requires='>=3.8.2',
    entry_points={
        'console_scripts': [
            'commandname = app:main'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
