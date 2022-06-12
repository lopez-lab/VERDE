from flask_table import Table, Col, ButtonCol

class Results(Table):
    image = ButtonCol('Structure', 'openPopup', url_kwargs=dict(inchiKey='inchiKey'), form_attrs={"target": "_blank"})
    #smiles = Col('SMILES', show=False)
    #inchiKey = Col('InChIKey', show=False)
    homo = Col('HOMO (eV)')
    lumo = Col('LUMO (eV)')
    verticalExcitationEnergy = Col('VEE (eV)')
    redoxPotentialS0 = Col('\( \mathbf{E_h^{S_0}} \) (eV)')
    redoxPotentialS1 = Col('\( \mathbf{E_h^{S_1}} \) (eV)')
    redoxPotentialT1 = Col('\( \mathbf{E_h^{T_1}} \) (eV)')
    dipoleMomentS0 = Col('\( \mathbf{\mu^{S_0}} \) (D)')
    dipoleMomentS1 = Col('\( \mathbf{\mu^{S_1}} \) (D)')
    dipoleMomentT1 = Col('\( \mathbf{\mu^{T_1}} \) (D)')
    ionizationPotential = Col('\( \mathbf{E_i} \) (eV)')
    zero0s1 = Col('\( \mathbf{^{00}S_1}\) (eV)')
    zero0t1 = Col('\( \mathbf{^{00}T_1}\) (eV)')
