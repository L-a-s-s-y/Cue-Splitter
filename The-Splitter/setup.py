from setuptools import setup, find_packages

setup(
    name="ffcuesplitter-rest-api",
    version="1.0.0",
    author="Lassy",
    #author_email="tu_email@ejemplo.com",
    description="Aplicación para procesar archivos de audio y cue con Flask",
    long_description=open("README.md").read(),  # Asegúrate de tener un archivo README.md
    long_description_content_type="text/markdown",
    #url="https://github.com/L-a-s-s-y/Proyecto-CC",  # Cambia esto si tienes un repositorio
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=[
        "ffcuesplitter",
        "pytest",
        "Flask",
        "Werkzeug",
        "requests",
        "flask-cors",
        "psycopg2-binary"
    ],
    entry_points={
        "console_scripts": [
            "run-app=api:app.run",
        ],
    },
    #classifiers=[
    #    "Programming Language :: Python :: 3",
    #    "License :: OSI Approved :: MIT License",
    #    "Operating System :: OS Independent",
    #],
    python_requires=">=3.7",
)
