# This script is developed for the JHU labor study.
# The script is mainly based on the ASTAR_LABOR project to compute the decompositions along the
# agri-food value chain
# This code is dveloped based on the EORA_Loop.py
# contact: jing.yi@wisc.edu

import os, os.path
import pandas as pd
import glob
import pyodbc
import subprocess
import requests, zipfile, io
import download
import wget

import requests
from selenium import webdriver
import time
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import subprocess

import sys
import nltk
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk import WordNetLemmatizer
from nltk import pos_tag
from nltk.stem import PorterStemmer
import matplotlib.pyplot as plt

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')

WorkingDir = r"D:\Dropbox\BoxOld\FEDSshare\MasterGithub\CornellGitHub\ASTAR_Labor\LaborAFVC\Code"
OutputDir = WorkingDir + "/Data"
dir = r"D:\Dropbox\BoxOld\FEDSshare\MasterGithub\CornellGitHub\ASTAR_Labor\LaborAFVC\Code\Data"
dir_test = r"D:\Dropbox\BoxOld\FEDSshare\MasterGithub\CornellGitHub\ASTAR_Labor\LaborAFVC\Code\Test"
sys.path.append(WorkingDir)
Dir_Manu = r"D:\Dropbox\BoxOld\FEDSshare\MasterGithub\CornellGitHub\ASTAR_Labor\LaborAFVC\TechnicalDocumentation"
DirVad = r"D:\Dropbox\BoxOld\FEDSshare\MasterGithub\CornellGitHub\ASTAR_Labor\LaborAFVC\Code\Validation"
jhuDir = r"D:\Dropbox\BoxOld\FEDSshare\MasterGithub\CornellGitHub\ASTAR_Labor\JHU\JhuJyGit\JHU\CodeData\Data"
dir_temp = r"D:\Dropbox\BoxOld\FEDSshare\MasterGithub\CornellGitHub\ASTAR_Labor\LaborAFVC\Code\Data"


import jy_eora
import importlib
importlib.reload(jy_eora)
import EORA_Config as config

FEDSsqlServerInstance = config.FEDSsqlServerInstance
dbname = config.dbname
FEDSconnectionStr = config.FEDSconnectionStr
FEDSconn = pyodbc.connect(FEDSconnectionStr)
FEDScursor = FEDSconn.cursor()

pd.set_option('display.max_columns', 15)
pd.set_option('display.max_row', 15)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.float_format',lambda x:'%.3f' % x)

def clean_tb(ls):
    for i in ls:
        sql_clean = "drop table " + i
        try:
            FEDScursor.execute(sql_clean)
            FEDScursor.commit()
        except Exception as e:
            continue
    return("removed the tables from the server")

def clean_view(ls):
    for i in ls:
        sql_clean = "drop view " + i
        try:
            FEDScursor.execute(sql_clean)
            FEDScursor.commit()
        except Exception as e:
            continue
    return("removed the views from the server")


def fn_get(fileName):
    df_i_header_file = OutputDir + fileName
    df_i_header = pd.read_csv(df_i_header_file, sep=r'\t', engine='python', header=None)
    return df_i_header


def fn_LAdd(df_temp):
    conditions = [(df_temp['Description',].str.contains('Compensation')),
                  (df_temp['Description',].str.contains('Taxes')),
                  (df_temp['Description',].str.contains('Subsidies')),
                  (df_temp['Description',].str.contains('Net operating')),
                  (df_temp['Description',].str.contains('Net mixed income')),
                  (df_temp['Description',].str.contains('Consumption'))]
    results = ["LH01" ,"LG01","LG02","LK01","LK02","LK03"]
    df_temp['Abb'] = np.select(conditions,results)
    return df_temp

def fn_IndAbb(df_temp,colName):
    conditions = [(df_temp[colName] =='Agriculture'),
                  (df_temp[colName] =='Fishing'),
                  (df_temp[colName] =='Mining and Quarrying'),
                  (df_temp[colName] =="Food & Beverages"),
                  (df_temp[colName] =='Textiles and Wearing Apparel'),
                  (df_temp[colName] =='Wood and Paper'),
                  (df_temp[colName] == "Petroleum, Chemical and Non-Metallic Mineral Products"),
                  (df_temp[colName] == 'Metal Products'),
                  (df_temp[colName] == 'Electrical and Machinery'),
                  (df_temp[colName] == 'Transport Equipment'),
                  (df_temp[colName] == 'Other Manufacturing'),
                  (df_temp[colName] == 'Recycling'),
                  (df_temp[colName] == 'Electricity, Gas and Water'),
                  (df_temp[colName] == 'Construction'),
                  (df_temp[colName] == 'Maintenance and Repair'),
                  (df_temp[colName] == 'Wholesale Trade'),
                  (df_temp[colName] == 'Retail Trade'),
                  (df_temp[colName] == 'Hotels and Restraurants'),
                  (df_temp[colName] == 'Transport'),
                  (df_temp[colName] == 'Post and Telecommunications'),
                  (df_temp[colName] == 'Finacial Intermediation and Business Activities'),
                  (df_temp[colName] == 'Public Administration'),
                  (df_temp[colName] == 'Education, Health and Other Services'),
                  (df_temp[colName] == 'Private Households'),
                  (df_temp[colName] == 'Others'),
                  (df_temp[colName] == "Re-export & Re-import"),
                  (df_temp[colName] == 'TOTAL')]
    results = ['A01',	'A02',	'A03',	'A04',	'A05',	'A06',	'A07',	'A08',	'A09',	'A10',	'A11',	'A12',
               'A13',	'A14',	'A15',	'A16',	'A17',	'A18',	'A19',	'A20',	'A21',	'A22',	'A23',	'A24',
               'A25',	'A26','LR1']
    colNew = colName+"Abb"
    df_temp[colNew] = np.select(conditions,results)
    return df_temp

def fn_lut(fileName,preName):
    df_i_header_file = OutputDir+fileName
    df_i_header = pd.read_csv(df_i_header_file, sep=r'\t', engine='python',header=None)
    if preName == "L":
        print("Leakage")
        df_i_header.columns = [['Category', 'Description']]
        df_i_header = fn_LAdd(df_i_header)
        df_i_header = df_i_header.iloc[:,[0,2,1]]
    elif preName == "X":
        print("Final demand")
        df_i_header.columns = [['Abb','Abb2','Category','Description']]
        df_i_header = fn_FdAbb(df_i_header,'Description')
        df_i_header['ctry_col_abb'] = df_i_header['Abb',].astype(str) +"_"+df_i_header['DescriptionAbb',]
        df_i_header.columns =['Abb','Abb2','Category','Description','DescriptionAbb','Ctry_Col_Abb']
        # df_i_header = df_i_header.iloc[:, [0, 2, 1]]
    else:
        df_i_header.columns = [['Abb','Abb2','Category','Description']]
        df_i_header = df_i_header.drop('Abb2',axis=1)
        df_i_header = df_i_header.iloc[:,[1,0,2]]
        df_i_header = fn_IndAbb(df_i_header,'Description')
        df_i_header['Row'] = df_i_header['Abb',] + "_" +df_i_header['DescriptionAbb',]
    return df_i_header


def fn_FdAbb(df_temp,colName):
    conditions = [(df_temp[colName] =='Household final consumption P.3h'),
                  (df_temp[colName] == 'Non-profit institutions serving households P.3n'),
                  (df_temp[colName] == 'Government final consumption P.3g'),
                  (df_temp[colName] == 'Gross fixed capital formation P.51'),
                  (df_temp[colName] == 'Changes in inventories P.52'),
                  (df_temp[colName] == 'Acquisitions less disposals of valuables P.53')]
    results = ["XH","XNPISH","XG","XK01","XK02","XK03"]
    colNew = colName+"Abb"
    df_temp[colNew] = np.select(conditions,results)
    return df_temp
# ------------------------------------------------------------------#
# functions for estimations:
# ------------------------------------------------------------------#
def get_fs_margin(df_margin):
    df_margin_A01 = df_margin.mul(df_ag_food['Agriculture'],axis=0)
    df_margin_A01 = df_margin_A01.groupby(df_margin_A01.index.get_level_values(0).str[:3]).sum()
    df_margin_A01.rename(index=lambda x:x+'_A01',inplace=True)

    df_margin_A02 = df_margin.mul(df_ag_food['Fishing'],axis=0)
    df_margin_A02 = df_margin_A02.groupby(df_margin_A02.index.get_level_values(0).str[:3]).sum()
    df_margin_A02.rename(index=lambda x:x+'_A02',inplace=True)

    df_margin_A04 = df_margin.mul(df_ag_food['Food & Beverages'],axis=0)
    df_margin_A04 = df_margin_A04.groupby(df_margin_A04.index.get_level_values(0).str[:3]).sum()
    df_margin_A04.rename(index=lambda x:x+'_A04',inplace=True)
    return df_margin_A01, df_margin_A02, df_margin_A04

def sum_col(df_i, df_fs_cord):
    df_fs_row = df_fs_cord.T
    result = pd.DataFrame()
    for col_i in df_i.columns:
        if col_i in df_fs_row.columns:
            result[col_i] = df_i[col_i] * df_fs_row[col_i].values[0]

    group_key = [col[:3] for col in result.columns.get_level_values(0)]
    df_i_sum = result.groupby(group_key, axis=1).sum()
    df_i_sum = df_i_sum.add_suffix("_A18")
    return df_i_sum

def get_comm_rows_cols(df_1_ori,df_2_ori):
    df_1 = df_1_ori.copy()
    df_2 = df_2_ori.copy()
    df_1.columns = df_1.columns.str[:3]
    df_2.columns = df_2.columns.str[:3]

    df_1.index = df_1.index.str[:3]
    df_2.index = df_2.index.str[:3]

    common_columns = df_1.columns.intersection(df_2.columns)
    df_1 = df_1[common_columns]
    df_2 = df_2[common_columns]
    common_index = df_1.index.intersection(df_2.index)
    df_1 = df_1.loc[common_index]
    df_2 = df_2.loc[common_index]
    return df_1,df_2

def get_comm_ctry(df_1_ori, df_2_ori):
    df_1 = df_1_ori.copy()
    df_2 = df_2_ori.copy()

    df_1.index = df_1.index.str[:3]
    df_2.index = df_2.index.str[:3]
    common_index = df_1.index.intersection(df_2.index)
    df_1 = df_1.loc[common_index]
    df_2 = df_2.loc[common_index]

    return df_1, df_2

def get_margin_new(df_x,sec,df_ratio):
    df_x_sec = df_x[df_x.index.str[4:7] == str(sec)]
    df_x_sec, df_ratio = get_comm_rows_cols(df_x_sec, df_ratio)
    df_margin = df_x_sec.multiply(df_ratio)
    df_margin.index = df_margin.index + '_'+ str(sec)
    return df_margin

def A01T02(df):
    # df = L_
    df = df.rename(columns = lambda x: x.replace('_A01','_A01T02').replace('_A02','_A01T02'))
    df = df.rename(index=lambda x: x.replace('A01', 'A01T02').replace('A02', 'A01T02'))
    df_a0102 = df.groupby(df.columns,axis=1).sum()
    df_a0102.sort_index(axis=1,inplace=True)
    df_a0102 = df_a0102.groupby(df_a0102.index).sum()
    return df_a0102

def sum_by_tb(df_i):
    df_i['Group'] = np.where(df_i.index.get_level_values(1).str.contains('tobacco', case=False), 'Tb', 'NoTb')
    df_i['Ctry'] = df_i.index.get_level_values(1).str[:3]
    df_i_tb = df_i.groupby(['Group', 'Ctry']).sum()
    df_i_tb.reset_index(inplace=True)
    df_i_tb.sort_values(by=['Ctry', 'Group'], inplace=True)
    return df_i_tb

def get_fs_margin(df_margin):
    df_margin_A01 = df_margin.mul(df_ag_food['Agriculture'],axis=0)
    df_margin_A01 = df_margin_A01.groupby(df_margin_A01.index.get_level_values(0).str[:3]).sum()
    df_margin_A01.rename(index=lambda x:x+'_A01',inplace=True)

    df_margin_A02 = df_margin.mul(df_ag_food['Fishing'],axis=0)
    df_margin_A02 = df_margin_A02.groupby(df_margin_A02.index.get_level_values(0).str[:3]).sum()
    df_margin_A02.rename(index=lambda x:x+'_A02',inplace=True)

    df_margin_A04 = df_margin.mul(df_ag_food['Food & Beverages'],axis=0)
    df_margin_A04 = df_margin_A04.groupby(df_margin_A04.index.get_level_values(0).str[:3]).sum()
    df_margin_A04.rename(index=lambda x:x+'_A04',inplace=True)
    return df_margin_A01, df_margin_A02, df_margin_A04


def sum_col(df_i, df_fs_cord):
    df_fs_row = df_fs_cord.T
    result = pd.DataFrame()
    for col_i in df_i.columns:
        if col_i in df_fs_row.columns:
            result[col_i] = df_i[col_i] * df_fs_row[col_i].values[0]

    group_key = [col[:3] for col in result.columns.get_level_values(0)]
    df_i_sum = result.groupby(group_key, axis=1).sum()
    df_i_sum = df_i_sum.add_suffix("_A18")
    return df_i_sum

# Function to extract nouns
def extract_nouns(text):
    text = text.lower()  # Convert text to lower case
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    nouns = [word for word, pos in tagged if (pos in ['NN', 'NNS', 'NNP', 'NNPS']) and stemmer.stem(word) not in ignored_words]
    return nouns


def A01T02(df):
    # df = L_
    df = df.rename(columns = lambda x: x.replace('_A01','_A01T02').replace('_A02','_A01T02'))
    df = df.rename(index=lambda x: x.replace('A01', 'A01T02').replace('A02', 'A01T02'))
    df_a0102 = df.groupby(df.columns,axis=1).sum()
    df_a0102.sort_index(axis=1,inplace=True)
    df_a0102 = df_a0102.groupby(df_a0102.index).sum()
    return df_a0102


def sum_by_tb(df_i):
    df_i['Group'] = np.where(df_i.index.get_level_values(1).str.contains('tobacco', case=False), 'Tb', 'NoTb')
    df_i['Ctry'] = df_i.index.get_level_values(1).str[:3]
    df_i_tb = df_i.groupby(['Group', 'Ctry']).sum()
    df_i_tb.reset_index(inplace=True)
    df_i_tb.sort_values(by=['Ctry', 'Group'], inplace=True)
    return df_i_tb


def sum_col(df_i, df_fs_cord):
    df_fs_row = df_fs_cord.T
    result = pd.DataFrame()
    for col_i in df_i.columns:
        if col_i in df_fs_row.columns:
            result[col_i] = df_i[col_i] * df_fs_row[col_i].values[0]

    group_key = [col[:3] for col in result.columns.get_level_values(0)]
    df_i_sum = result.groupby(group_key, axis=1).sum()
    df_i_sum = df_i_sum.add_suffix("_A18")
    return df_i_sum


def get_margin_value(df_x,sec,df_ratio):
    # df_x = y_fah
    # sec='A01'
    # df_ratio = A01_trans_ratio
    df_x_sec = df_x[df_x.index.str[4:7] == str(sec)]
    df_x_sec, df_ratio = get_comm_rows_cols(df_x_sec, df_ratio)
    df_margin = df_x_sec.multiply(df_ratio)
    df_margin.index = df_margin.index + '_'+ str(sec)
    # df_margin.index = df_margin.index + '_A19'
    return df_margin

def wideToLong(trans_margin_i):

    df_trans_long = pd.DataFrame()
    for col in trans_margin_i.columns:
        df_i = trans_margin_i[[col]]
        df_i['Ctry'] = col[:3]
        # df_i['COL'] = col
        df_i = df_i.rename(columns={col:'Trans'})
        df_i['ROW'] = df_i.index
        df_trans_long = pd.concat([df_trans_long,df_i])
    return df_trans_long

# ---------------------------------------------------------------------------------------------
# --------------------------------------Create balanced tables:---------------------------------
# ---------------------------------------------------------------------------------------------
fileName = "/labels_FD.txt"
preName = "X"
df_FD_header = fn_lut(fileName,preName)
df_FD_header.loc[df_FD_header['Ctry_Col_Abb'].str[:3]=='ROW','Ctry_Col_Abb'] = 'ZZZ' + df_FD_header['Ctry_Col_Abb'].str[3:]

fileName = "/labels_T.txt"
preName = "A"
df_T_header = fn_lut(fileName,"A")
df_T_header.shape
df_T_header.columns = ["Category","Abb","Description","Descriptionabb","ROW"]
df_T_header.loc[df_T_header['ROW'] == 'ROW_LR1', 'ROW'] = 'LR1'

fileName = "/labels_VA.txt"
preName = "L"
df_L_header = fn_lut(fileName,preName)

year_i = 2021

# removed COU74_ in the following view:
sql_1 = """
CREATE VIEW [JHU_EORA].[LUT"""  + """]
AS
SELECT	 [COU]
FROM	 [ASTAR_Labor].[EORA].[COU_LUT]
where COUNTRY !='RestOfWorld'
"""
FEDScursor.execute(sql_1)
FEDScursor.commit()

# was named [EORA].[EORA74x26_TRowCol_LUT +str(year_i):
sql_view = """ CREATE VIEW [JHU_EORA].[TRowCol_LUT"""+"""]
    AS
    SELECT	 [ROW_BAL] [ROW]
    FROM	 [ASTAR_Labor].[EORA].[T2COU_ccd]
    WHERE	 [COU]
    IN		 (SELECT * FROM [JHU_EORA].[LUT]"""
FEDScursor.execute(sql_view)
FEDScursor.commit()

sql_view2 = """ CREATE VIEW [JHU_EORA].[XCol_LUT""" +  """]
   AS
   SELECT	 [COL_BAL] [COL]
   FROM	 [ASTAR_Labor].[EORA].[X2COU_ccd]
   WHERE	 [COU]
   IN		 (SELECT * FROM [JHU_EORA].[LUT"""   + "])"
FEDScursor.execute(sql_view2)
FEDScursor.commit()

sql_x = """ CREATE TABLE [JHU_EORA].[xBAL""" + str(year_i) + """](
    [ROW] [nchar](5) NOT NULL,
    [COL] [nchar](5) NOT NULL,
    [VALUE] [decimal](14, 3) NOT NULL)"""
FEDScursor.execute(sql_x)
FEDScursor.commit()

sql_x1 = """INSERT INTO [JHU_EORA].[xBAL""" + str(year_i) + """]
      --TMATRIX
      SELECT [ROW]
              ,[COL]
              ,[VALUE]
      FROM	 [EORA].[EORA26_BAL""" + str(
    year_i) + """] WHERE	 [ROW] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT""" + """]) AND		
     [COL] IN (SELECT * 
      FROM [JHU_EORA].[TRowCol_LUT"""   + """]) UNION
      --XMATRIX
      SELECT	 [ROW]
              ,[COL]
              ,[VALUE]
      FROM	 [EORA].[EORA26_BAL""" + str(
    year_i) + """] WHERE	 [ROW] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""  + """])  AND		
     [COL] IN (SELECT * 
      FROM [JHU_EORA].[XCol_LUT"""  + """]) UNION
      --LMATRIX
      SELECT	 [ROW]
              ,[COL]
              ,[VALUE]
      FROM	 [EORA].[EORA26_BAL""" + str(year_i) + """] WHERE	 LEFT([ROW],1) = 'L'
      AND		 [COL] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT""" + """])
      UNION
      --XRVECTOR
      SELECT	 [ROW]
              ,'XR001' [COL]
              ,SUM([VALUE]) [VALUE]
      FROM	 [EORA].[EORA26_BAL""" + str(year_i) + """]
      WHERE	 [ROW] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""  + """])
      AND		 [COL] NOT IN ( SELECT * FROM [JHU_EORA].[TRowCol_LUT"""  + """] UNION
                              SELECT * FROM [JHU_EORA].[XCol_LUT""" + """])
      GROUP BY [ROW]
      UNION
      --LRVECTOR
      SELECT	 'LR001' [ROW]
              ,[COL]
              ,SUM([VALUE]) [VALUE]
      FROM	 [EORA].[EORA26_BAL""" + str(year_i) + """]
      WHERE	 [COL] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""  + """])
      AND		 [ROW] NOT IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""  + """]) AND	
      	 LEFT([ROW], 1) != 'L'
      GROUP BY [COL]
      """
FEDScursor.execute(sql_x1)
FEDScursor.commit()

sql_75x26_bal = """ 
 CREATE TABLE [JHU_EORA].[BAL""" + str(year_i) + """] ([ROW] [nchar](5) NOT NULL,
 	[COL] [nchar](5) NOT NULL,
 	[VALUE] [decimal](14, 3) NOT NULL )"""
FEDScursor.execute(sql_75x26_bal)
FEDScursor.commit()

sql_A = """ SELECT	 [ROW]
    ,[COL]
    ,[VALUE]
INTO	 #JHU_A""" + str(year_i) + """ FROM
(
SELECT	 [ROW]
        ,[COL]
        ,[VALUE]
FROM	 [EORA].[EORA26_BAL""" + str(year_i)+ \
        """] WHERE	 [ROW] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT""" +\
        """]) AND [COL] IN (
        SELECT * FROM [JHU_EORA].[TRowCol_LUT""" + """]) UNION
--T74x75th
SELECT	 A.[ROW]
        ,'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4)) [COL]
        ,SUM(A.[VALUE]) [VALUE]
FROM	 [EORA].[EORA26_BAL""" + str(year_i)+"""] A
        ,[EORA].[T2CouAct_ccd] B WHERE	 A.[COL] = B.[ROW_BAL]
AND		 A.[ROW] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""  +\
        """]) AND		 A.[COL] NOT IN (
SELECT * FROM [JHU_EORA].[TRowCol_LUT"""   +"""]) GROUP BY A.[ROW]
        ,'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4))
UNION SELECT	 'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4)) [ROW]
        ,A.[COL]
        ,SUM(A.[VALUE]) [VALUE]
FROM	 [EORA].[EORA26_BAL""" + str(year_i)+"""] A
        ,[EORA].[T2CouAct_ccd] B
WHERE	 A.[ROW] = B.[ROW_BAL]
AND		 A.[ROW] NOT IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""  +"""]) AND	
     A.[COL] IN (
SELECT * FROM [JHU_EORA].[TRowCol_LUT""" +\
        """]) GROUP BY 'A'+CAST(4915+CAST(RIGHT(B.[Act],
2) AS INT) AS CHAR(4))
        ,A.[COL] UNION
SELECT	 'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4)) [ROW]
        ,'A'+CAST(4915+CAST(RIGHT(C.[Act],2) AS INT) AS CHAR(4)) [COL]
        ,SUM(A.[VALUE]) [VALUE]
FROM	 [EORA].[EORA26_BAL""" + str(year_i)+"""] A
        ,[EORA].[T2CouAct_ccd] B
        ,[EORA].[T2CouAct_ccd] C
WHERE	 A.[ROW] = B.[ROW_BAL]
AND		 A.[COL] = C.[ROW_BAL]
AND		 A.[ROW] NOT IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT""" +"""]) AND		
 A.[COL] NOT IN (
SELECT * FROM [JHU_EORA].[TRowCol_LUT""" +"""]) GROUP BY 'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4))
        ,'A'+CAST(4915+CAST(RIGHT(C.[Act],2) AS INT) AS CHAR(4)) UNION
SELECT	 [ROW]
        ,[COL]
        ,[VALUE]
FROM	 [EORA].[EORA26_BAL""" + str(year_i)+"""] WHERE	 [ROW] IN
 (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""+ """]) AND	
     [COL] IN (SELECT * FROM [JHU_EORA].[XCol_LUT"""+"""]) UNION
--X74x75th
SELECT	 [ROW]
        ,[COL]=CASE
         WHEN [COL]='XG' THEN 'X1135'
         WHEN [COL]='XH' THEN 'X1136'
         WHEN [COL]='XK01' THEN 'X1137'
         WHEN [COL]='XK02' THEN 'X1138'
         WHEN [COL]='XK03' THEN 'X1139'
         WHEN [COL]='XNPISH' THEN 'X1140'
         WHEN [COL]='XR1' THEN 'X1141'
         END
        ,[VALUE]
FROM	 (SELECT A.[ROW]
                ,B.[Inst] [COL]
                ,SUM(A.[VALUE]) [VALUE]
          FROM	 [EORA].[EORA26_BAL""" + str(year_i)+"""]  A
                ,[EORA].[X2CouInst_ccd] B WHERE	 A.[COL] = B.[COL_BAL]
          AND	 A.[ROW] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT""" +\
"""]) AND	 A.[COL] NOT IN (SELECT * FROM [JHU_EORA].[XCol_LUT"""+"""]) GROUP BY A.[ROW]
                ,B.[Inst]) X
UNION
--X75thx74
SELECT	 'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4)) [ROW]
        ,A.[COL]
        ,SUM(A.[VALUE]) [VALUE]
FROM	 [EORA].[EORA26_BAL""" + str(year_i) + """]  A
        ,[EORA].[T2CouAct_ccd] B
WHERE	 A.[ROW] = B.[ROW_BAL]
AND	 A.[ROW] NOT IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT""" +   """]) AND	 A.[COL] 
IN (SELECT * FROM [JHU_EORA].[XCol_LUT"""  +"""]) GROUP BY 'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4))
        ,A.[COL]
UNION
--X75thx75th
SELECT	 [ROW]
        ,[COL]=CASE
         WHEN [COL]='XG' THEN 'X1135'
         WHEN [COL]='XH' THEN 'X1136'
         WHEN [COL]='XK01' THEN 'X1137'
         WHEN [COL]='XK02' THEN 'X1138'
         WHEN [COL]='XK03' THEN 'X1139'
         WHEN [COL]='XNPISH' THEN 'X1140'
         WHEN [COL]='XR1' THEN 'X1141'
         END
        ,[VALUE]
FROM	 (SELECT 'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4)) [ROW]
                ,C.[Inst] [COL]
                ,SUM(A.[VALUE]) [VALUE] FROM	 [EORA].[EORA26_BAL""" + str(year_i) + """] A
                ,[EORA].[T2CouAct_ccd] B
                ,[EORA].[X2CouInst_ccd] C
          WHERE	 A.[ROW] = B.[ROW_BAL]
          AND	 A.[COL] = C.[COL_BAL]
          AND	 A.[ROW] NOT IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""   +"""])   AND	
           A.[COL] NOT IN (SELECT * FROM [JHU_EORA].[XCol_LUT"""  + """])  
            GROUP BY 'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4))
                ,C.[Inst]) X
UNION
--LMATRIX
--L7xT74
SELECT	 [ROW]
        ,[COL]
        ,[VALUE]
FROM	 [EORA].[EORA26_BAL""" + str(year_i) + """] WHERE	 LEFT([ROW],1) = 'L'
AND		 [COL] IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""  + """]) UNION
--L7xT75th
SELECT	 A.[ROW]
        ,'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4)) [COL]
        ,SUM(A.[VALUE]) [VALUE]
FROM	 [EORA].[EORA26_BAL"""+ str(year_i) + """]  A
        ,[EORA].[T2CouAct_ccd] B
WHERE	 A.[COL] = B.[ROW_BAL]
AND		 LEFT(A.[ROW],1) = 'L'
AND		 A.[COL] NOT IN (SELECT * FROM [JHU_EORA].[TRowCol_LUT"""   + """]) GROUP BY A.[ROW]
        ,'A'+CAST(4915+CAST(RIGHT(B.[Act],2) AS INT) AS CHAR(4))
UNION
--L7xX74
SELECT	 [ROW]
        ,[COL]
        ,[VALUE]
FROM	 [EORA].[EORA26_BAL""" + str(year_i) + """] WHERE	 LEFT([ROW],1) = 'L'
AND		 [COL] IN (SELECT * FROM [JHU_EORA].[XCol_LUT"""  + """]) UNION
--L7xX75
SELECT	 [ROW]
        ,[COL]=CASE
         WHEN [COL]='XG' THEN 'X1135'
         WHEN [COL]='XH' THEN 'X1136'
         WHEN [COL]='XK01' THEN 'X1137'
         WHEN [COL]='XK02' THEN 'X1138'
         WHEN [COL]='XK03' THEN 'X1139'
         WHEN [COL]='XNPISH' THEN 'X1140'
         WHEN [COL]='XR1' THEN 'X1141'
         END
        ,[VALUE]
FROM	 (SELECT A.[ROW]
                ,B.[Inst] [COL]
                ,SUM(A.[VALUE]) [VALUE]
          FROM	 [EORA].[EORA26_BAL""" + str(year_i) + """] A
                ,[EORA].[X2CouInst_ccd] B
          WHERE	 A.[COL] = B.[COL_BAL]
          AND	 LEFT(A.[ROW],1) = 'L'
          AND	 A.[COL] NOT IN (SELECT * FROM [JHU_EORA].[XCol_LUT"""  + """])  GROUP BY [ROW]
                ,B.[Inst]) X
) ZZ ;""" + """ SELECT	 Y.[ID]
        ,X.[DIFF]
        ,-X.[DIFF]*Y.[X1142] [X1142]
        ,X.[DIFF]*Y.[L0008] [L0008]
INTO	 #JHU_STP1_""" +str(year_i) + """ FROM
(
SELECT	 U.[ROW]
        ,U.[USE]-ISNULL(M.[MAKE],0) [DIFF]
FROM	 (SELECT [ROW]
                ,SUM([VALUE]) [USE]
          FROM	 #JHU_A"""+ str(year_i) + """  WHERE	 LEFT([ROW],1) = 'A'
          GROUP BY [ROW]) U
LEFT OUTER JOIN
         (SELECT [COL]
                ,SUM([VALUE]) [MAKE]
          FROM	 #JHU_A"""+ str(year_i)  + """ WHERE	 LEFT([COL],1) = 'A'
          GROUP BY [COL]) M
ON		 U.[ROW] = M.[COL]
) X,
(
SELECT	 ISNULL(A.[ROW],B.[COL]) [ID]
        ,[X1142]=CASE
         WHEN ISNULL(B.[L0007],0)=0 THEN 0.999
         ELSE CAST(ISNULL(A.[X1141],0) AS FLOAT)/(ISNULL(A.[X1141],0)+ISNULL(B.[L0007],0)) 
         END
        ,[L0008]=CASE
         WHEN ISNULL(B.[L0007],0)=0 THEN 0.001
         ELSE ISNULL(CAST(B.[L0007] AS FLOAT),0)/(ISNULL(A.[X1141],0)+ISNULL(B.[L0007],0))
         END
FROM	 (SELECT [ROW]
                ,[VALUE] [X1141]
          FROM	 #JHU_A"""+ str(year_i) + """ WHERE	 [COL] = 'X1141'
          AND	 LEFT([ROW],1) = 'A') A
FULL OUTER JOIN
         (SELECT [COL]
                ,[VALUE] [L0007]
          FROM	 [JHU_EORA].[xBAL"""+str(year_i)+"""]   WHERE	 [ROW] = 'L0007'
      AND	 LEFT([COL],1) = 'A') B
ON		 A.[ROW] = B.[COL]
) Y
WHERE	 X.[ROW] = Y.[ID]""" + """ 
SELECT	 [ROW]
        ,[COL]
        ,[VALUE]
INTO	 #JHU_STP2_""" + str(year_i) + """ FROM	 (SELECT 'L0008' [ROW]
                ,[ID] [COL]
                ,[L0008] [VALUE]
          FROM	 #JHU_STP1_""" + str(year_i) + """ UNION
          SELECT [ID] [ROW]
                ,'X1142' [COL]
                ,[X1142] [VALUE]
          FROM	 #JHU_STP1_""" + str(year_i) + """  UNION
          SELECT [ROW]
                ,[COL]
                ,[VALUE]
          FROM	 #JHU_A""" + str(year_i)+""") Z""" + """ 
          INSERT INTO [JHU_EORA].[BAL""" + str(year_i)+"""] SELECT * FROM #JHU_STP2_""" + str(
    year_i)

FEDScursor.execute(sql_A)
FEDScursor.commit()

sql_last = """ SELECT	 A.[ROW]
    ,[RCOU]=CASE
     WHEN (LEFT(A.[ROW],1)='L' AND A.[COL] NOT IN ('X1141','X1142')) THEN C.[COU]
     WHEN (LEFT(A.[ROW],1)='L' AND A.[COL] IN ('X1141','X1142')) THEN 0 
     ELSE ISNULL(B.[COU],0) 
     END
    ,[RActOrInst]=CASE
     WHEN LEFT(A.[ROW],1)='A' THEN RIGHT(B.[ROW],3)
     WHEN LEFT(A.[ROW],3) in ('L00') THEN A.[ROW]
     ELSE RIGHT(A.[ROW],3)
     END
    ,A.[COL]
    ,[CCOU]=CASE
     WHEN A.[COL] IN ('X1141','X1142') THEN 0
     ELSE ISNULL(C.[COU],0)
     END
    ,[CActOrInst]=CASE
     WHEN LEFT(A.[COL],1)='A' THEN RIGHT(C.[ROW],3)
     WHEN A.[COL]='X1141' THEN 'XR1'
     WHEN A.[COL]='X1142' THEN 'XR2'
     ELSE SUBSTRING(C.[ROW],5,LEN(C.[ROW]))
     END
    ,[VALUE]
into """ + """ [JHU_EORA].[wCouIDs_xNULLS""" + str(year_i)+ \
"""]  FROM	 (SELECT Y.[ROW]
            ,Y.[COL]
            ,ISNULL(Z.[VALUE],0) [VALUE]
      FROM	 (SELECT W.[ROW]
                    ,X.[COL]
              FROM	 (SELECT DISTINCT
                             [ROW]
                      FROM	 [JHU_EORA].[BAL"""+str(year_i)+"""]) W
                    ,(SELECT DISTINCT
                             [COL]
                      FROM	 [JHU_EORA].[BAL""" +str(year_i)+"""]) X) Y 
      LEFT OUTER JOIN
             [JHU_EORA].[BAL""" + str(year_i)+"""] Z
      ON	 Y.[ROW] = Z.[ROW]
      AND	 Y.[COL] = Z.[COL]) A
LEFT OUTER JOIN
     [EORA].[T2COU_ccd] B
ON		 A.[ROW] = B.[ROW_BAL]	
LEFT OUTER JOIN
     (SELECT [ROW]
            ,[ROW_BAL] [COL]
            ,[COU]
      FROM	 [EORA].[T2COU_ccd] UNION
      SELECT [COL] [ROW]
            ,[COL_BAL] [COL]
            ,[COU]
     FROM [EORA].[X2COU_ccd]) C
ON		 A.[COL] = C.[COL]"""

FEDScursor.execute(sql_last)
FEDScursor.commit()

# ---------------------------------------------------------------------------------------------
# --------------------------------------Use balanced tables:---------------------------------
# ---------------------------------------------------------------------------------------------
sql_qry_yr = """select *  from [JHU_EORA].[wCouIDs_xNULLS""" + str(year_i) +"]"
df_bal_yr = pd.read_sql(sql_qry_yr, FEDSconn)
df_bal_yr = df_bal_yr[['ROW', 'COL', 'VALUE']]
# df_bal_yr.to_csv(DirVad + '/jhu_bal' + str(year_i) + ".csv", sep='|')
df_bal_yr = df_bal_yr.sort_values(by=['ROW', 'COL'])
# df_bal_yr.to_csv(dir+'/balanced2010.csv',sep='|',index=False)
df_bal_yr3 = df_bal_yr.pivot(index='ROW', columns='COL', values='VALUE')
df_cor = pd.read_csv(OutputDir +'/ccd.csv',sep='|')
df_cor_dic = dict(zip(df_cor.ROW_BAL, df_cor.ROW))
df_corX = pd.read_csv(OutputDir +'/X2COU_ccd.csv',sep='|')
df_corX_dic = dict(zip(df_corX.COL_BAL, df_corX.COL))

df_bal_yr3.rename(index=df_cor_dic, inplace=True)
df_bal_yr3.rename(columns=df_cor_dic, inplace=True)
df_bal_yr3.rename(columns=df_corX_dic, inplace=True)
df_bal_yr3.rename(columns={'LR1': 'ZZZ_ZLR1', 'X1142': 'ZZZ_ZX1142'}, inplace=True)
df_bal_yr3.rename(index={'LR1': 'ZZZ_ZLR1', 'L0008': 'ZZZ_ZL0008'}, inplace=True)
df_bal_yr3.to_csv(DirVad + '/jhu_bal' + str(year_i) + ".csv", sep='|')

RowTot = df_bal_yr3.sum(axis=1)
dfRowTot = pd.DataFrame(RowTot,columns=['GrossOutput'])
dfRowTot.to_csv(jhuDir+'/GrossOutput'+str(year_i)+'.csv',sep='|')
test2 = df_bal_yr3.sum(axis=0)

# collapse imports:
df_output = pd.DataFrame()
# col = 'ABW_A01'
for col in df_bal_yr3.columns:
    # print(col)
    prefix = col.split('_')[0]
    df_i = df_bal_yr3[[col]].copy()
    # df_i.rename(columns={col:'Value'},inplace=True)
    df_i['Dest'] = col.split('_')[0]
    df_i['Origin'] = df_i.apply(lambda row: row.name[:3] if "_" in str(row.name) else prefix, axis=1)

    df_i['Origin_Sec'] = df_i.apply(lambda row: row.name[4:] if "_" in str(row.name) else  str(row.name), axis=1)


    df_dom = df_i[(df_i['Dest'] == df_i['Origin']) | df_i.index.astype(str).isin(['LH01', 'LG01', 'LG02', 'LK01',
                                                                                 'LK02',
                                                                        'LK03'])]

    df_imp = df_i[(df_i['Dest'] != df_i['Origin']) & ~df_i.index.astype(str).isin(['LH01', 'LG01', 'LG02', 'LK01',
                                                                                 'LK02',
                                                                        'LK03'])]
    df_impTot = df_imp.groupby('Origin_Sec')[col].sum().reset_index()

    df_dom['ROW'] = df_dom['Origin'].astype(str) + "_" + df_dom['Origin_Sec'].astype(str)
    df_dom['Value'] = df_dom[col]
    df_dom['COL'] = col
    df_impTot['ROW'] = "Imp_"+df_impTot['Origin_Sec'].astype(str)
    df_impTot['Value'] = df_impTot[col]
    df_impTot['COL'] = col
    df_i_proc = pd.concat([df_dom[['ROW','COL','Value']], df_impTot[['ROW','COL','Value']]])
    df_i_proc.reset_index(drop=True, inplace=True)

    df_output = df_output.append(df_i_proc)

df_output.to_csv(jhuDir+'/T_'+str(year_i)+'.csv',sep='|')
#  Test balance: 
# df_i_proc_test = df_output[df_i_proc['ROW'] == 'ABW_A01']
# df_i_proc.sum()
df_TransOutput = pd.merge(df_output,dfRowTot, on='ROW' )
df_TransOutput['Coef'] = df_TransOutput['Value']/df_TransOutput['GrossOutput']
df_TransOutput.to_csv(jhuDir+'/Coeff_'+str(year_i)+'.csv',sep='|')
df_TransOutput_test = df_TransOutput[df_TransOutput['COL']=='ABW_A01']
df_TransOutput_test.to_csv(jhuDir+'/TEST_Coeff_'+str(year_i)+'.csv',sep='|')

df_TransOutput_col = pd.merge(df_output,dfRowTot, left_on='COL',right_on='ROW' )
df_TransOutput_col['Coef'] = df_TransOutput_col['Value']/df_TransOutput_col['GrossOutput']
df_TransOutput_col.to_csv(jhuDir+'/Coeff_Col_'+str(year_i)+'.csv',sep='|')