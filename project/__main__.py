import time
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from scipy.sparse import lil_matrix, csr_matrix, csc_matrix
from scipy.stats import tstd
from project.finite_automata import *
from project.boolean_matrix_automata import *
import project.graph_module as gm
from tabulate import tabulate

print("exec sources directory")
