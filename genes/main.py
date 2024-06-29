import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import extracting_genes
#from .functions import genes_in_text

extracting_genes('extracted_genes.csv')

