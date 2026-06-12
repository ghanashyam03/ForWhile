from setuptools import setup, find_packages

setup(
    name="forwhile",
    version="1.0.0",
    description="A children's programming language teaching OOP concepts through plain-English syntax",
    author="ForWhile Team",
    packages=find_packages(),
    install_requires=[
        "ply>=3.11",
    ],
    entry_points={
        "console_scripts": [
            "forwhile=forwhile.interpreter:main",
        ],
    },
    python_requires=">=3.6",
)
