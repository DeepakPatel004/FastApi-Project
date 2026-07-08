from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json;

app = FastAPI();

def load_data():
    with open('patient.json','r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patient.json','w') as f:
        json.dump(data,f)

class Patient(BaseModel):
    id : Annotated[str,Field(...,description='ID of patient',examples=['P001'])]
    name : Annotated[str, Field(...,description='enter patient name')]
    city : Annotated[str, Field(...,description='Enter city name')]
    age : Annotated[int, Field(...,gt=0,lt=120,description='age of the patient')]
    gender : Annotated[Literal['Male','Female','Others'],Field(...,description='gender of the patient')]
    height : Annotated[float,Field(...,gt=0,description='int meter')]
    weight : Annotated[float,Field(...,gt=0,description='int kg')]

    @computed_field
    @property
    def bmi(self) ->float : 
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
        

class PatientUpdate(BaseModel):
    name : Annotated[Optional[str], Field(default=None)]
    city : Annotated[Optional[str],Field(default=None)]
    age : Annotated[Optional[int],Field(default=None)]
    gender : Annotated[Optional[Literal['Male','Female','Others']],Field(default=None)]
    height : Annotated[Optional[str], Field(default=None)]
    weight : Annotated[Optional[str], Field(default=None)]
    

@app.get("/")
def hello():
    return {'message' : 'Patient'}

@app.get('/about')
def about():
    return {'message' : 'since 1999'}

@app.get('/view')
def view():
    data = load_data()
    return data


@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    # load all the patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    data = load_data()

    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data



@app.post('/create')
def create_patient(patient : Patient):
    #load existing data
    data = load_data()

    #check if patient already exist

    if patient.id in data:
            raise HTTPException(status_code=400, detail='patient already exists')
    
    #new patient add to database
    data[patient.id] = patient.model_dump(exclude=['id']);

    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient successfully created'})
    

@app.put('/edit/{patient_id}')
def edit_profile(patient_update: PatientUpdate,patient_id: str = Path(...,description='Enter patient ID')):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = Patient(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str = Path(...,description='Enter patient ID')):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=400,detail="patientid is not exist")
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=201,content={'message':'patient detail deleted successfully'})




