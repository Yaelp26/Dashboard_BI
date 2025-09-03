from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework import status
from django.db import connection
from .models import Dataset
from .serializers import DatasetSerializer
from django.views.generic import TemplateView
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

class UploadDatasetView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = DatasetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Leer el archivo CSV directamente desde la request
            uploaded_file = request.FILES['file']
            df = pd.read_csv(io.StringIO(uploaded_file.read().decode('utf-8')))

            # Crear una tabla única basada en el ID del dataset
            dataset_id = serializer.instance.id
            table_name = f"dataset_{dataset_id}"

            with connection.cursor() as cursor:
                # Eliminar tabla si ya existe
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

                # Crear tabla con columnas como TEXT
                create_sql = f'CREATE TABLE "{table_name}" ('
                for col in df.columns:
                    create_sql += f'"{col}" TEXT, '
                create_sql = create_sql.rstrip(', ') + ')'
                cursor.execute(create_sql)

                # Insertar filas
                for _, row in df.iterrows():
                    values = "', '".join(str(val).replace("'", "''") for val in row)
                    insert_sql = f"INSERT INTO \"{table_name}\" VALUES ('{values}')"
                    cursor.execute(insert_sql)

            return Response({
                "message": "Dataset subido y almacenado correctamente.",
                "dataset_id": dataset_id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DatasetListView(ListAPIView):
    queryset = Dataset.objects.all().order_by('-uploaded_at')
    serializer_class = DatasetSerializer

class DatasetDetailView(RetrieveAPIView):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

@api_view(['GET'])
def dataset_shape_view(request, id):
    try:
        dataset = Dataset.objects.get(pk=id)
        df = pd.read_csv(dataset.file.path)

        shape = {
            "rows": df.shape[0],
            "columns": df.shape[1]
        }

        return Response(shape)

    except Dataset.DoesNotExist:
        return Response({"error": "Dataset no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def dataset_dtypes_view(request, id):
    try:
        dataset = Dataset.objects.get(pk=id)
        df = pd.read_csv(dataset.file.path)

        dtypes = [
            {"column": col, "dtype": str(dtype)}
            for col, dtype in df.dtypes.items()
        ]

        return Response(dtypes)

    except Dataset.DoesNotExist:
        return Response({"error": "Dataset no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def dataset_nulls_view(request, id):
    try:
        dataset = Dataset.objects.get(pk=id)
        df = pd.read_csv(dataset.file.path)

        nulls = df.isnull().sum()
        result = [{"column": col, "nulls": int(nulls[col])} for col in df.columns]

        return Response(result)

    except Dataset.DoesNotExist:
        return Response({"error": "Dataset no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def dataset_duplicates_view(request, id):
    try:
        dataset = Dataset.objects.get(pk=id)
        df = pd.read_csv(dataset.file.path)

        duplicates = int(df.duplicated().sum())

        return Response({"duplicate_rows": duplicates})

    except Dataset.DoesNotExist:
        return Response({"error": "Dataset no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def dataset_unique_values_view(request, id):
    try:
        dataset = Dataset.objects.get(pk=id)
        df = pd.read_csv(dataset.file.path)

        uniques = df.nunique()
        result = [{"column": col, "unique_values": int(uniques[col])} for col in df.columns]

        return Response(result)

    except Dataset.DoesNotExist:
        return Response({"error": "Dataset no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def dataset_describe_view(request, id):
    try:
        dataset = Dataset.objects.get(pk=id)
        df = pd.read_csv(dataset.file.path)

        describe = df.describe(include='number').transpose()

        result = []
        for col, stats in describe.iterrows():
            result.append({
                "column": col,
                "count": float(stats["count"]),
                "mean": float(stats["mean"]),
                "std": float(stats["std"]),
                "min": float(stats["min"]),
                "25%": float(stats["25%"]),
                "50%": float(stats["50%"]),
                "75%": float(stats["75%"]),
                "max": float(stats["max"]),
            })

        return Response(result)

    except Dataset.DoesNotExist:
        return Response({"error": "Dataset no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def dataset_histograms_view(request, id):
    try:
        dataset = Dataset.objects.get(pk=id)
        df = pd.read_csv(dataset.file.path)

        numeric_cols = df.select_dtypes(include='number').columns
        histograms = []

        for col in numeric_cols:
            plt.figure()
            df[col].plot(kind='hist', bins=20, title=f"Histograma de {col}")
            plt.xlabel(col)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)

            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            histograms.append({
                "column": col,
                "histogram_base64": f"data:image/png;base64,{image_base64}"
            })

        return Response(histograms)

    except Dataset.DoesNotExist:
        return Response({"error": "Dataset no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def dataset_boxplots_view(request, id):
    try:
        dataset = Dataset.objects.get(pk=id)
        df = pd.read_csv(dataset.file.path)

        numeric_cols = df.select_dtypes(include='number').columns
        boxplots = []

        for col in numeric_cols:
            plt.figure()
            df.boxplot(column=col)
            plt.title(f"Boxplot de {col}")
            plt.ylabel(col)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)

            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            boxplots.append({
                "column": col,
                "boxplot_base64": f"data:image/png;base64,{image_base64}"
            })

        return Response(boxplots)

    except Dataset.DoesNotExist:
        return Response({"error": "Dataset no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

@api_view(['DELETE'])
def eliminar_datasets_view(request):
    with connection.cursor() as cursor:
        # Eliminar tablas tipo dataset_#
        cursor.execute("""
            SELECT tablename FROM pg_tables
            WHERE tablename LIKE 'dataset_%'
        """)
        tablas = cursor.fetchall()
        for (tabla,) in tablas:
            cursor.execute(f'DROP TABLE IF EXISTS "{tabla}" CASCADE')

        # Eliminar registros del modelo Dataset
        Dataset.objects.all().delete()

        # Reiniciar secuencia del ID
        cursor.execute("ALTER SEQUENCE data_analysis_dataset_id_seq RESTART WITH 1")

    return Response({"message": "Todos los datasets eliminados y secuencia reiniciada."})