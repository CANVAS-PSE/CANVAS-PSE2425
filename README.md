![banner](https://github.com/user-attachments/assets/a3be1582-ffdc-4a34-94df-08d07bcda11e)

# CANVAS - 3D editor for the AI-enhanced differentiable Ray Tracer ARTIST

[![](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Installation
We heavily recommend to install `CANVAS` package in a dedicated `Python3.8+` virtual environment ([click here for the documentation](https://docs.python.org/3/library/venv.html)).

After setting up and activating the virtual environment *(or deciding against against it)*, execute the following instructions, to set up the code base
```bash
# for Mac users: replace python with python3
# clone the repo
git clone https://github.com/CANVAS-PSE/CANVAS-PSE2425.git

# install requirements
cd CANVAS-PSE2425/
pip install -r requirements.txt

# add the .env file to the root of the canvas_project folder 
# containing debug variable, client_id + secret_key for OpenID, email-host password, etc.

# configure the database
cd canvas_project/
python manage.py migrate

# start the server
python manage.py runserver

# access the website under the in the command line specified url
```

## How to contribute

Check out our [contribution guidelines](CONTRIBUTING.md) if you are interested in contributing to the `CANVAS` project :fire:.
Please also carefully check our [code of conduct](CODE_OF_CONDUCT.md) :blue_heart:.

## License

Liberally licensed under MIT.

---

<div align="center">
  <a href="https://www.dlr.de/EN/Home/home_node.html"><img src="./logos/logo_dlr.svg" height="50px" hspace="3%" vspace="25px"></a>
  <a href="http://www.kit.edu/english/index.php"><img src="./logos/logo_kit.svg" height="50px" hspace="3%" vspace="25px"></a>
  <a href="https://www.helmholtz.ai/"><img src="./logos/logo_hai.svg" height="25px" hspace="3%" vspace="25px"></a>
</div>
