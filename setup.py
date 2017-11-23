from setuptools import find_packages, setup

version = '0.0.1'

setup(
    name='tinyauth',
    version=version,
    license='Apache Software License',
    classifiers=[
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask>=0.12",
        "Flask-Cors>=3.0.2",
        "Flask-Migrate>=2.0.3",
        "Flask-RESTful>=0.3.5",
        "Flask-SQLAlchemy>=2.2",
        "psycopg2>=2.6.1",
        "PyJWT>=1.5.3",
    ],
    extras_require = {
        'test': [
            'flake8',
            'flake8-isort',
            'pytest',
            'pytest-cov',
            'codecov',
        ],
    },
    entry_points='''
        [console_scripts]
        tinyauth = tinyauth.app:cli
    ''',
)
