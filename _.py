Titulo_Profesional.insert_many(
('No studies or incomplete school studies','High School',
'Degree',"Master's degree",'technologist'),
fields = (Titulo_Profesional.nombre,)
).execute()

Modalidad.insert_many(('Select','intern','in person','remote','mixed'),
    fields=(Modalidad.nombre,))