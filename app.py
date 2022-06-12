import random
import pandas as pd
import numpy as np
import os
import json
import glob
import requests
import re
from flask import Flask, jsonify, request, abort, render_template, Response, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length
from forms.SmileForm import AddSmileForm, SearchSmileForm, AdminLoginForm, AddSmileToDBForm
from forms.Table import Results
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import rdkit
from rdkit import Chem
from rdkit.Chem import Draw
from datetime import datetime

app = Flask(__name__)
# Z. Hu, updated csv
#df = pd.read_csv(os.getcwd() + '/data/verde_properties.csv')
df = pd.read_csv(os.getcwd() + '/data/verde_properties_07232020.csv')
#df = pd.read_csv(os.getcwd() + '/data/Parsed_data_for_verde-db_2022-05-15.csv')
colDict = {'inchi_key':'inchiKey','smiles':'smiles','homo (eV)':'homo','lumo (eV)':'lumo',
'vertical_excitation_energy (eV)':'verticalExcitationEnergy','redox_potential_S0 (eV)':'redoxPotentialS0',
'redox_potential_S1 (eV)':'redoxPotentialS1','redox_potential_T1 (eV)':'redoxPotentialT1',
'dipole_moment_S0 (D)':'dipoleMomentS0','dipole_moment_S1 (D)':'dipoleMomentS1','dipole_moment_T1 (D)':'dipoleMomentT1',
'0-0_S1 (eV)':'zero0s1','0-0_T1 (eV)':'zero0t1','ionization_potential (eV)':'ionizationPotential'}
df.rename(columns=colDict, inplace=True)
# Z. Hu, updated csv for images 
#smileToImage = pd.read_csv(os.getcwd()+'/data/smileImageMapping.csv')
smileToImage = pd.read_csv(os.getcwd()+'/data/smileImageMapping_12272020.csv')
#smileToImage = pd.read_csv(os.getcwd()+'/data/smileImageMapping_05172022.csv')

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    # Z. Hu, updated csv 
    #df = pd.read_csv(os.getcwd() + '/data/verde_properties.csv')
    df = pd.read_csv(os.getcwd() + '/data/verde_properties_07232020.csv')
    #df = pd.read_csv(os.getcwd() + '/data/Parsed_data_for_verde-db_2022-05-15.csv')
    # Z. Hu, two decimal points for all numbers from database
    df = df.round(decimals=2)
    df.rename(columns=colDict, inplace=True)
    # Z. Hu, updated csv for images 
    #smileToImage = pd.read_csv(os.getcwd()+'/data/smileImageMapping.csv')
    smileToImage = pd.read_csv(os.getcwd()+'/data/smileImageMapping_12272020.csv')
    #smileToImage = pd.read_csv(os.getcwd()+'/data/smileImageMapping_05172022.csv')
    search = SearchSmileForm(request.form)
    table = Results(df.to_dict(orient='records'), table_id='dtHorizontalVertical')
    table.border = True
    if request.method == 'POST':
        ##############################################################
        # Z. Hu, save the queried results to a csv file 
        #table = search_results(search, df)
        table, table_df = search_results(search, df)
        timestamp = str(datetime.now()).replace(" ","-")
        filename = f"VERDE_queried_results_{timestamp}"
        table_df.to_csv(f"query/{filename}.csv", index=False)
        ##############################################################

    return render_template('Index.html', form=search, table=table)

@app.route('/<inchiKey>', methods=['POST'])
def openPopup(inchiKey):
    row = smileToImage[smileToImage['inchiKey'] == inchiKey]
    imgname = row['imageName'].iloc[0]
    smile = row['smiles'].iloc[0]
    inchikey = row['inchiKey'].iloc[0]
    ###############################################
    #Z. Hu, Test
    row1 = df[df['inchiKey'] == inchiKey]
    print (row1)
    #import sys; sys.exit()
    homo = row1['homo'].iloc[0]
    lumo = row1['lumo'].iloc[0]
    vee = row1['verticalExcitationEnergy'].iloc[0]
    rps0 = row1['redoxPotentialS0'].iloc[0]
    rps1 = row1['redoxPotentialS1'].iloc[0]
    rpt1 = row1['redoxPotentialT1'].iloc[0]
    dms0 = row1['dipoleMomentS0'].iloc[0]
    dms1 = row1['dipoleMomentS1'].iloc[0]
    dmt1 = row1['dipoleMomentT1'].iloc[0]
    ip = row1['ionizationPotential'].iloc[0]
    zero0s1 = row1['zero0s1'].iloc[0]
    zero0t1 = row1['zero0t1'].iloc[0]
    ###############################################
    return render_template('Popup.html', Img='static/'+imgname, smiles=smile, inchikey=inchikey, homo=homo, lumo=lumo, vee=vee, rps0=rps0, rps1=rps1, rpt1=rpt1, dms0=dms0, dms1=dms1, dmt1=dmt1, ip=ip, zero0s1=zero0s1, zero0t1=zero0t1)

# Z. Hu, function to download the CSV file
@app.route("/getCSVNew")
def getCSVNew():
    current_dir = os.getcwd()
    list_of_files = glob.glob(f'{current_dir}/query/*csv') 
    latest_file = max(list_of_files, key=os.path.getctime)
    #for filename in list_of_files: 
    #    if filename != latest_file:
    #       os.remove(filename)
    return send_file(latest_file,
                     mimetype='text/csv',
                     attachment_filename=os.path.basename(latest_file),
                     as_attachment=True,
                     cache_timeout=0) 

@app.route('/addSmile', methods=['GET','POST'])
def addSmile():
    addSmile = AddSmileForm(request.form)
    if request.method == 'POST':
        sendEmail(addSmile.data)
        return Response(status=200, response='Request successfully submitted.')

    return render_template('AddSmile.html', form=addSmile)

def process(data):
    sList = []
    smileList = data['smiles'].split(':')
    for s in smileList:
        s = s.strip('\r')
        s = s.strip('\n')
        s = s.strip()
        sList.append(s)
    return pd.DataFrame(data = sList, columns = ['SMILES'])

def sendEmail(data):
    data = process(data)
    message = Mail(
        from_email='s.lopez@northeastern.edu',
        to_emails='verdedb@northeastern.edu',
        subject='Request to Add New SMILES.',
        html_content=data.to_html())
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except:
        print('Error while emailing.')

def search_results(search, df):
    search_string = search.data
    for val in colDict.values():
        if (search_string[val] is not None and search_string[val] is not ''):
           if ':' in search_string[val]:
              minval, maxval = search_string[val].split(':')
              minval, maxval = float(minval), float(maxval)
              df = df[df[val] >= minval]
              df = df[df[val] <= maxval]
           else:
              try:
                 df = df[df[val] == float(search_string[val])]
              except:
                 df = df[df[val] == str(search_string[val])]
    table = Results(df.to_dict(orient='records'), table_id='dtHorizontalVertical')
    #table.border = True 
    #########################
    # Z. Hu
    # Also save the dataframe 
    table_df = df
    #return table
    return table, table_df
    #########################

@app.route('/adminLogin', methods=['GET','POST'])
def adminLogin():
    adminLogin = AdminLoginForm(request.form)
    if request.method == 'POST':
        if adminLogin.data['username'] != '' and adminLogin.data['username'] == 'admin' and adminLogin.data['password'] == 'admin':
            addSmileToDB = AddSmileToDBForm(request.form)
            return render_template('AddSmileToDB.html', form=addSmileToDB)
        elif adminLogin.data['username'] == '':
            addSmileToDB = AddSmileToDBForm(request.form)
            try:
                addToDB(addSmileToDB.data)
                return Response(status=200, response='Request successfully submitted.')
            except NameError:
                return Response(status=400, response='Invalid SMILE.')
            except ValueError:
                return Response(status=400, response='SMILE already exists.')
        return Response(status=401, response='Authentication failed.')
    return render_template('AdminLogin.html', form=adminLogin)

def addToDB(data):
    appendList = []
    # Z. Hu, updated csv 
    #interdf = pd.read_csv(os.getcwd() + '/data/verde_properties.csv')
    interdf = pd.read_csv(os.getcwd() + '/data/verde_properties_07232020.csv')
    #interdf = pd.read_csv(os.getcwd() + '/data/Parsed_data_for_verde-db_2022-05-15.csv')
    if len(interdf[interdf['smiles'] == str(data['smiles'])]) == 0:
        for c in interdf.columns.tolist():
            try:
                val = str(data[colDict[c]])
            except:
                val = float(data[colDict[c]])
            appendList.append(val)
        try:
            l = len(interdf)
            mol = Chem.MolFromSmiles(str(data['smiles']))
            fileName = Chem.MolToInchiKey(mol) + ".{}".format('png')
            Draw.MolToFile(mol, os.getcwd()+'/static/'+str(l)+'.png', size=(600,600))
            
            interdf.loc[l] = appendList
            smileToImage.loc[l] = [str(data['smiles']), str(l)+'.png', str(data['inchiKey'])]
            # Z. Hu, updated csv and csv for images 
            #smileToImage.to_csv(os.getcwd()+'/data/smileImageMapping.csv', index=None)
            #interdf.to_csv(os.getcwd()+'/data/verde_properties.csv', index=None)
            smileToImage.to_csv(os.getcwd()+'/data/smileImageMapping_12272020.csv', index=None)
            #smileToImage.to_csv(os.getcwd()+'/data/smileImageMapping_05172022.csv', index=None)
            interdf.to_csv(os.getcwd()+'/data/verde_properties_07232020.csv', index=None)
            #interdf.to_csv(os.getcwd()+'/data/Parsed_data_for_verde-db_2022-05-15.csv', index=None)
        except:
            raise NameError('Invalid SMILE.')
    else:
        raise ValueError('SMILE already exists.')

if __name__ == "__main__": 
	app.run(host='0.0.0.0',port=5000,debug=True)
