""" 
Normalization functions for the st analysis package
"""
import numpy as np
import pandas as pd
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri, r, globalenv
base = rpackages.importr("base")

def RimportLibrary(lib_name):
    if not rpackages.isinstalled(lib_name):
        base.source("http://www.bioconductor.org/biocLite.R")
        biocinstaller = rpackages.importr("BiocInstaller")
        biocinstaller.biocLite(lib_name)
    return rpackages.importr(lib_name)
     
def computeSizeFactors(counts):
    pandas2ri.activate()
    r_counts = pandas2ri.py2ri(counts)
    deseq = RimportLibrary("DESeq")
    dds = deseq.estimateSizeFactorsForMatrix(r_counts)
    pandas_sf = pandas2ri.ri2py(dds)
    pandas2ri.deactivate()
    return pandas_sf

def computeSizeFactorsLinear(counts):
    pandas2ri.activate()
    r_counts = pandas2ri.py2ri(counts)
    deseq2 = RimportLibrary("DESeq2")
    vec = rpackages.importr('S4Vectors')
    bio_generics = rpackages.importr("BiocGenerics")
    cond = vec.DataFrame(condition=base.factor(base.c(base.colnames(r_counts))))
    design = r('formula(~ condition)')
    dds = deseq2.DESeqDataSetFromMatrix(countData=r_counts, colData=cond, design=design)
    dds = bio_generics.estimateSizeFactors(dds, type="iterate")
    pandas_sf = pandas2ri.ri2py(bio_generics.sizeFactors(dds))
    pandas2ri.deactivate()
    return pandas_sf

def computeDESeq2LogTransform(counts):
    pandas2ri.activate()
    r_counts = pandas2ri.py2ri(counts)
    deseq2 = RimportLibrary("DESeq2")
    vec = rpackages.importr('S4Vectors')
    gr = rpackages.importr('GenomicRanges')
    cond = vec.DataFrame(condition=base.factor(base.c(base.colnames(r_counts))))
    design = r('formula(~ condition)')
    dds = deseq2.DESeqDataSetFromMatrix(countData=r_counts, colData=cond, design=design)
    logs = deseq2.rlog(dds, blind=True, fitType="mean")
    logs_count = gr.assay(logs)
    pandas_count = pd.DataFrame(np.matrix(logs_count), columns=logs_count.colnames, index=logs_count.rownames)
    pandas2ri.deactivate()
    return pandas_count
            
def computeEdgeRNormalization(counts):
    pandas2ri.activate()
    r_counts = pandas2ri.py2ri(counts)
    edger = RimportLibrary("edgeR")
    factors = base.factor(base.c(base.colnames(r_counts)))
    dge = edger.DGEList(counts=r_counts, group=factors)
    y = edger.calcNormFactors(dge)
    y = edger.estimateCommonDisp(y)
    mult = r.get('*')
    normalized = mult(y[0], y[1][2])
    pandas_count = pd.DataFrame(np.matrix(normalized), columns=normalized.colnames, index=normalized.rownames)
    pandas2ri.deactivate()
    # EdgeR transposes the matrix of counts
    return pandas_count.transpose()
