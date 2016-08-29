from setuptools import setup, find_packages

version = '0.5'

setup(
    name='Products.PleiadesEntity',
    version=version,
    description="",
    long_description="""\
""",
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='',
    author='Institute for the Study of the Ancient World',
    author_email='isaw@nyu.edu',
    url='https://github.com/isawnyu/PleiadesEntity',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'collective.geo.geographer',
        'isaw.bibitems',
    ],
    extras_require={
        'test': ['Products.PloneTestCase'],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
