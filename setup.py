import setuptools

version = '2.0.1'

setuptools.setup(
    name='mysql_tracer',
    version=version,
    author='Adrien Horgnies',
    author_email='adrien.pierre.horgnies@gmail.com',
    description='A MySQL client to run queries, write execution reports and export results',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AdrienHorgnies/py-mysql-tracer',
    download_url='https://github.com/AdrienHorgnies/py-mysql-tracer/archive/{version}.tar.gz'.format(version=version),
    packages=setuptools.find_packages(),
    install_requires=['mysql-connector-python==8.0.17', 'keyring==19.0.2'],
    extras_require={
        'dev': ['pytest==5.0.1', 'mock==3.0.5']
    },
    entry_points={
        'console_scripts': ['mst=mysql_tracer.__main__:main']
    },
    license='MIT License',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
    keywords=['mysql', 'client', 'report', 'export']
)
