# VERDE
Virtual Excited State Reference for the Discovery of Electronic Materials Database: An Open-Access Resource for Ground and Excited State Properties of Organic Molecules

*Please see the documentation for details. In brief,
1. Conda (base) has been set up on that node. If there is a need to redo it:
   1. Download miniconda from [here](https://docs.conda.io/en/latest/miniconda.html)
   2. Get the repo: `git clone https://github.com/lopez-lab/VERDE.git`
   3. Install the needed packages: `pip install -r requirement.txt`
   4. Generate the 2D molecule images: `python util/GenerateImages.py`
2. Keep the app running on the node.
   1. Use "nohup" (ignore the HUP signal): `nohup python app.py > log.txt &`
   2. Make sure the website [VERDE DB](http://verdedb.org/) is working 
