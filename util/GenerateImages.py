import pandas as pd
import os
import rdkit
from rdkit import Chem
from rdkit.Chem import Draw

#df = pd.read_csv(os.getcwd() + '/data/verde_properties.csv')
# Z. Hu, updated csv
#df = pd.read_csv(os.getcwd() + '/data/verde_properties_07232020.csv')
df = pd.read_csv(os.getcwd() + '/data/Parsed_data_for_verde-db_2022-05-15.csv')
smileToImage = pd.DataFrame(columns=['smiles','imageName','inchiKey'])

for i, row in df.iterrows():
    smile = row[1]
    mol = Chem.MolFromSmiles(smile)
    fileName = Chem.MolToInchiKey(mol) + ".{}".format('png')
    Draw.MolToFile(mol, os.getcwd()+'/static/'+str(i)+'.png', size=(600,600))
    smileToImage.loc[i] = [row['smiles'], str(i)+'.png', row['inchi_key']]
#smileToImage.to_csv(os.getcwd()+'/data/smileImageMapping.csv', index=None)
# Z. Hu, updated csv for images
#smileToImage.to_csv(os.getcwd()+'/data/smileImageMapping_12272020.csv', index=None)
smileToImage.to_csv(os.getcwd()+'/data/smileImageMapping_05172022.csv', index=None)
