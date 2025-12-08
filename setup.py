from setuptools import setup, find_packages

setup(
    name="math_slm",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "torch",
        "transformers",
        "sympy",
        "numpy"
    ],
)