from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .conexion import conexion
from .forms import File, Login
import pandas as pd
import os

def validar_columnas(columnas_pais):
    columnas = ['nombre', 'codigo' ,'usuario' ,'region', 
                'poblacion' ,'capital', 'moneda',
                'idioma', 'paisesFronterizos',
                'bandera', 'ubicacion']
    
    if len(columnas_pais) != len(columnas):
        return False
    for columna in columnas_pais:
        if columna not in columnas:
            return False
    return True


def validar_campos(lista_paises):
    db = conexion()
    coleccion = db['paises']
    result = []
    for index in range(len(lista_paises)):
        codigo = lista_paises[index]['codigo']
        nombre = lista_paises[index]['nombre']
        pais_encontrado = list(coleccion.find({"codigo":codigo}))
        if pais_encontrado != []:
            result.append('No se inserto el pais con codigo {}, ya existe en base de datos'.format(codigo))
            continue
        if str(codigo) == 'nan' or str(nombre) == 'nan':
            result.append('No se puedo insertar el pais de la posicion {}, no tiene uno de estos Campos requeridos. --->Codigo - Nombre</br>'.format(index+1))
        else:
            if str(lista_paises[index].get('ubicacion')) == 'nan':
                result.append('Pais con nombre: {}, Codigo: {} tiene datos incompletos. no se puede insertar'.format(nombre, codigo))
                continue
            for clave, valor in lista_paises[index].items():
                if clave == 'poblacion':
                    poblacion = lambda x: int(x) if str(x).isdigit() else 0 
                    lista_paises[index][clave] = poblacion(valor)
                if lista_paises[index][clave] == 'nan':
                    lista_paises[index][clave] = ''
            coleccion.insert_one(lista_paises[index])
            result.append('Pais con nombre: {}, Codigo: {}. ---- insertado'.format(nombre, codigo))
    return result
    
    
def log_in(request):
    if request.method == 'POST':
        formulario = Login(request.POST)
        if formulario.is_valid():
            datos = formulario.cleaned_data
            user = authenticate(request, username= datos['usuario'], password = datos['password'])
            if user is not None:
                login(request, user)
                return JsonResponse({'message':'Sesion inciada'})
            else:
                return JsonResponse({'message':'Usuario o contraseña incorrectas'})
    else:
        formulario = Login()
    return render(request,"login.html", {"form":formulario})


@login_required(login_url='/')
def log_out(request):
    logout(request)
    print("sesion terminada")
    return redirect('/')

def handle_uploaded_file(f):
    extensiones_permitidas = ['csv']
    nombre_archivo = f.name
    split_archivo = nombre_archivo.split('.')
    extension = split_archivo[len(split_archivo)-1]
    if extension not in extensiones_permitidas:
        return False
    with open('pais.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return True

@login_required(login_url='/')
def insertarPais(request):
    if request.method == "POST":
        formulario = File(request.POST,request.FILES)
        if formulario.is_valid():
            datos = request.FILES['file']
            if not handle_uploaded_file(datos):
                return JsonResponse({'message':'Archivo no valido, extencion no permitida'})
            try:
                df = pd.read_csv('pais.csv')
                os.remove('pais.csv')
                lista_paises = []
                columnas_dataFrame = df.columns.values
                if not validar_columnas(columnas_dataFrame):
                        return JsonResponse({'message':'Columnas Invalidas'})
                for content in df.iterrows():
                    pais = dict(content[1])
                    lista_paises.append(pais)
                return JsonResponse({'messages':validar_campos(lista_paises)})     
            except Exception as e:
                print("error al insertar en base de datos",e)
                return JsonResponse({'Error': str(e), 'ErrorMessage':"error al insertar en base de datos"})
    else:
        formulario = File()
    return render(request, 'insertarPais.html', {'form':formulario})

@login_required(login_url='/')
def getPaises(request):
    try:
        db = conexion()
        coleccion = db['paises']
        paises = list(coleccion.find())
        for index in range(len(paises)):
            paises[index]['_id'] = str(paises[index]['_id'])
            paises[index]['usuario'] = str(paises[index]['usuario'])
        return JsonResponse(list(paises), safe=False)
    except Exception as e:
        print(e)
        print("Error al buscar paises en la base de datos")
        return JsonResponse({'Error': str(e),'ErrorMessage':"Error al buscar paises en la base de datos"})

@login_required(login_url='/')
def getPaisByCodigo(request, codigo):
    try:
        db = conexion()
        coleccion = db['paises']
        pais_encontrado = coleccion.find_one({"codigo":codigo})
        if pais_encontrado == None:
            return JsonResponse({'message':'No se pudo encontrar paises con codigo {}'.format(codigo)})
        pais_encontrado['_id'] = str(pais_encontrado['_id'])
        pais_encontrado['usuario'] = str(pais_encontrado['usuario'])
        valores = list(pais_encontrado.values())
        items = list(pais_encontrado.keys())
        dataFramePais = pd.DataFrame([valores], columns = items)
        dataFramePais.to_csv('pais_encontrado.csv', index=False)
        
        return JsonResponse(pais_encontrado)
    except Exception as e:
        print(e)
        print("Error al buscar pais por el codigo")
        return JsonResponse({'ErrorCode': str(e), 'ErrorMessage': "Error al buscar pais por el codigo"})


  
