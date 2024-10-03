import sys
import boto3
import pandas as pd
import os

### Arquivo com script job para ser adicionado no bucket "ScriptBucket"

# Recupera os argumentos passados pela Lambda
args = sys.argv
S3_INPUT_PATH = args[0]
S3_OUTPUT_PATH = args[1]

# Inicializa o cliente S3
s3 = boto3.client('s3')

# Função para fazer download de arquivos S3
def download_s3_file(s3_path):
    bucket = s3_path.split('/')[2]
    key = '/'.join(s3_path.split('/')[3:])
    local_filename = '/tmp/' + key.split('/')[-1]
    s3.download_file(bucket, key, local_filename)
    return local_filename

# Função para fazer upload de arquivos para o S3
def upload_s3_file(local_file, s3_path):
    bucket = s3_path.split('/')[2]
    key = '/'.join(s3_path.split('/')[3:])
    s3.upload_file(local_file, bucket, key)

# Função para determinar o formato do arquivo com base na extensão
def get_file_format(path):
    if path.endswith(".csv"):
        return "csv"
    elif path.endswith(".json"):
        return "json"
    else:
        raise ValueError("Formato de arquivo não suportado. Somente arquivos CSV ou JSON são permitidos.")

# Baixa o arquivo de entrada do S3
input_file = download_s3_file(S3_INPUT_PATH)
file_format = get_file_format(input_file)

# Processa o arquivo de entrada e converte para Parquet
if file_format == "csv":
    df = pd.read_csv(input_file)
elif file_format == "json":
    df = pd.read_json(input_file)

# Salva o arquivo convertido em Parquet localmente
parquet_output_file = '/tmp/output.parquet'
df.to_parquet(parquet_output_file)

# Faz upload do arquivo Parquet para o destino no S3
upload_s3_file(parquet_output_file, S3_OUTPUT_PATH)

# Remove arquivos temporários
os.remove(input_file)
os.remove(parquet_output_file)