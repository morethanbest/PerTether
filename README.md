# PerTether
## Introduction
PerTether is a tool that can automatically initialize a private Ethereum blockchain and execute performance tests on it. PerTether is designed based on the performance concerns of the private Ethereum blockchain. PerTether can fully test the private Ethereum blockchain in different scenarios with a single start operation. There is no need to build test chain and simulate the scenarios manually. Researchers only need to deﬁne a simple conﬁguration, PerTether will do the rest steps, which provides convenience for the researchers. 
## Installation
If you run our tools you need to install the following software environment.
### Software Environment Configuration
Python 3.6
To install the package to your computer, simply run the following command in the base directory:
* pip install Django
* pip install json
* pip install urllib
* pip install shutil
* pip install zipfile
* pip install os
* pip install zipstream
* pip install pandas as pd
* pip install time
* pip install subprocess
* pip install execjs
## How do I run this project?
* Step 1:Enter the directory of this project and execute the following command to start the Django project.
  * python manage.py runserver 127.0.0.1:8000
* Step 2:Enter the URL http://127.0.0.1:8000/experiment/ in the browser to enter the Ethereum configuration page.
## Example
![](https://github.com/morethanbest/PerTether/blob/master/gui/static/images/config.png)
![](https://github.com/morethanbest/PerTether/blob/master/gui/static/images/testconfig.png)


