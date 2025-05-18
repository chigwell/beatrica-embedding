from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='beatrica-embedding',
    version='2025.5.180922',
    author='Eugene Evstafev',
    author_email='chigwel@gmail.com',
    description='A Python package for embedding and analyzing code changes in git repositories.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/beatrica-embedding',
    packages=find_packages(),
    install_requires=[
        'gitignore-parser>=0.0.8',
        'langchain>=0.1',
        'GitPython>=3.1,<4'
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'flake8>=3.8',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
