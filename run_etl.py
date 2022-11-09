from pyspark import SparkConf
from pyspark.sql import SparkSession
from datetime import datetime
from typing import Sequence, Mapping, Any
import os

from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType
from pyspark.sql.types import StringType
from pyspark.sql.types import DoubleType

## BUCKETS S3
BUCKETS: Sequence[Mapping[str, Any]] = [
    {
        's3_dados_brutos': os.environ.get('S3_BUCKET_BRUTOS')
    },
    {
        's3_dados_tratados': os.environ.get('S3_BUCKET_TRATADOS')
    },
    {
        's3_logs': os.environ.get('S3_BUCKET_LOGS')
    }
]

## AMBIENTE AZURE
AMBIENTE: Sequence[Mapping[str, Any]] = [
    {
        'prod-url': os.environ.get('URL_DATABASE_AZURE_PROD'),
        'user': os.environ.get('USER_DATABASE_AZURE_PROD'),
        'pass': os.environ.get('PASS_DATABASE_AZURE_PROD'),
    },
    {
        'dev-url': os.environ.get('URL_DATABASE_AZURE_DEV'),
        'user': os.environ.get('USER_DATABASE_AZURE_DEV'),
        'pass': os.environ.get('PASS_DATABASE_AZURE_DEV'),
    }
]

# DATA DE PROCESSAMENTO
DATE_NOW = datetime.now().strftime("%d_%m_%Y")

## Iniciando Sessão no Spark
conf = SparkConf()
conf.set('spark.jars.packages', 'org.apache.hadoop:hadoop-aws:3.2.2,com.microsoft.azure:spark-mssql-connector_2.12:1.2.0')
conf.set('spark.hadoop.fs.s3a.aws.credentials.provider', 'com.amazonaws.auth.InstanceProfileCredentialsProvider')
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# Lendo o CSV e tratando o tipo de encoding para a ISO-8859-1
df_inscricao_fies_20211_bruto = spark.read \
    .option('encoding', 'ISO-8859-1') \
    .option('delimiter', ';') \
    .option('header', 'true') \
    .csv(f'{BUCKETS[0].get("s3_dados_brutos")}/fies/relatorio_inscricao_dados_abertos_fies_12021.csv')

df_inscricao_fies_20212_bruto = spark.read \
    .option('encoding', 'ISO-8859-1') \
    .option('delimiter', ';') \
    .option('header', 'true') \
    .csv(f'{BUCKETS[0].get("s3_dados_brutos")}/fies/relatorio_inscricao_dados_abertos_fies_22021.csv')

df_inscricao_fies_2021 = df_inscricao_fies_20211_bruto.union(df_inscricao_fies_20212_bruto)

df_inscricao_fies_2021_tratado = df_inscricao_fies_2021.select(
    col('Ano do processo seletivo').cast(StringType()).alias('ANO_PROCESSO_SELETIVO'),
    col('Semestre do processo seletivo').cast(StringType()).alias('SEMESTRE_PROCESSO_SELETIVO'),
    col('ID do estudante').cast(StringType()).alias('ID_DO_ESTUDANTE'), # CRIPTOGRAFAR
    col('Sexo').cast(IntegerType()).alias('SEXO'),
    col('Data de Nascimento').cast(StringType()).alias('DATA_NASCIMENTO'),
    col('UF de residência').cast(StringType()).alias('UF_RESIDENCIA'),
    col('Municipio de residência').cast(StringType()).alias('MUNICIPIO_RESIDENCIA'),
    col('Etnia/Cor').cast(StringType()).alias('ETNIA_COR'),
    col('Pessoa com deficiência?').cast(StringType()).alias('PESSOAL_COM_DEFICIENCIA'),
    col('Tipo de escola no ensino médio').cast(StringType()).alias('TIPO_ESCOLA_ENSINO_MEDIO'),
    col('Ano conclusão ensino médio').cast(StringType()).alias('ANO_CONCLUSAO_ENSINO_MEDIO'),
    col('Concluiu curso superior?').cast(StringType()).alias('IS_ONCLUIU_CURSO_SUPERIOR'),
    col('Professor rede pública ensino?').cast(StringType()).alias('IS_PROFESSOR_REDE_PUBLICA_ENSINO'),
    col('Nº de membros Grupo Familiar').cast(IntegerType()).alias('QTDE_MEMBROS_GRUPO_FAMILIAR'),
    col('Renda familiar mensal bruta').cast(DoubleType()).alias('RENDA_FAMILIAR_MENSAL_BRUTA'),
    col('Renda mensal bruta per capita').cast(DoubleType()).alias('RENDA_MENSAL_BRUTA_PER_CAPITA'),
    col('Região grupo de preferência').cast(StringType()).alias('REGIAO_GRUPO_DE_PREFERENCIA'),
    col('UF').cast(StringType()).alias('UF'),
    col('`Cod.Microrregião`').cast(IntegerType()).alias('COD_MICROREGIAO'),
    col('Microrregião').cast(StringType()).alias('MICROREGIAO'),
    col('Conceito de curso do GP').cast(StringType()).alias('CONCEITO_CURSO_DO_GP'),
    col('Área do conhecimento').cast(StringType()).alias('AREA_CONHECIMENTO'),
    col('Subárea do conhecimento').cast(StringType()).alias('SUBAREA_CONHECIMENTO'),
    col('`Cod. do Grupo de preferência`').cast(IntegerType()).alias('COD_GRUPO_PREFERENCIA'),
    col('Nota Corte Grupo Preferência').cast(DoubleType()).alias('NOTA_CORTE_GRUPO_PREFERENCIA'),
    col('Opções de cursos da inscrição').cast(IntegerType()).alias('OPCOES_CURSOS_DA_INSCRICAO'),
    col('Nome mantenedora').cast(StringType()).alias('NOME_MANTENEDORA'),
    col('Natureza Jurídica Mantenedora').cast(StringType()).alias('NATUREZA_JURIDICA_MANTENEDORA'),
    col('CNPJ da mantenedora').cast(StringType()).alias('CNPJ_MANTENEDORA'),
    col('Código e-MEC da Mantenedora').cast(StringType()).alias('COD_EMEC_MANTENEDORA'),
    col('Nome da IES').cast(StringType()).alias('NOME_DA_IES'),
    col('Código e-MEC da IES').cast(StringType()).alias('COD_EMEC_DA_IES'),
    col('Organização Acadêmica da IES').cast(StringType()).alias('ORGANIZACAO_ACADEMICA_DA_IES'),
    col('Município da IES').cast(StringType()).alias('MUNICIPIO_DA_IES'),
    col('UF da IES').cast(StringType()).alias('UF_DA_IES'),
    col('Nome do Local de oferta').cast(StringType()).alias('NOME_DO_LOCAL_DE_OFERTA'),
    col('Munícipio do Local de Oferta').cast(StringType()).alias('MUNICIPIO_DO_LOCAL_DE_OFERTA'),
    col('UF do Local de Oferta').cast(StringType()).alias('UF_DO_LOCAL_DE_OFERTA'),
    col('Código do curso').cast(StringType()).alias('COD_CURSO'),
    col('Nome do curso').cast(StringType()).alias('NOME_CURSO'),
    col('Turno').cast(StringType()).alias('TURNO_CURSO'),
    col('Grau').cast(StringType()).alias('GRAU_CURSO'),
    col('Conceito').cast(IntegerType()).alias('COD_CONCEITO'),
    col('Média nota Enem').cast(DoubleType()).alias('MEDIA_NOTA_ENEM'),
    col('Ano do Enem').cast(StringType()).alias('ANO_DO_ENEM'),
    col('Redação').cast(IntegerType()).alias('NOTA_REDACAO'),
    col('Matemática e suas Tecnologias').cast(DoubleType()).alias('NOTA_MATEMATICA_E_SUAS_TECNOLOGIAS'),
    col('Linguagens, Códigos e suas Tec').cast(DoubleType()).alias('NOTA_LINGUAGENS_E_CODICOS_E_SUAS_TECNOLOGIAS'),
    col('Ciências Natureza e suas Tec').cast(DoubleType()).alias('NOTA_CIENCIA_NATUREZA_E_SUAS_TECNOLOGIAS'),
    col('Ciências Humanas e suas Tec').cast(DoubleType()).alias('NOTA_CIENCIA_HUMANAS_E_SUAS_TECNOLOGIAS'),
    col('Situação Inscrição Fies').cast(StringType()).alias('SITUACAO_INSCRICAO_FIES'),
    col('Percentual de financiamento').cast(StringType()).alias('PERCENTUAL_DE_FINANCIAMENTO'),
    col('Semestre do financiamento').cast(StringType()).alias('SEMESTRE_DO_FINANCIAMENTO'),
    col('Qtde semestre financiado').cast(IntegerType()).alias('QTDE_SEMESTRE_FINANCIADO'),
)

# Salvando o arquivo processado com os dados de inscrição no fies tratados na S3
df_inscricao_fies_2021_tratado \
    .coalesce(1) \
    .write \
    .mode('append') \
    .option('encoding', 'UTF-8') \
    .csv(f'{BUCKETS[1].get("s3_dados_tratados")}/{DATE_NOW}/fies/')

df_inscricao_fies_2021_tratado.write.mode("overwrite") \
    .format("jdbc") \
    .option('url', f'{AMBIENTE[0].get("prod-url")}') \
    .option("dbtable", 'FIES') \
    .option("user", f'{AMBIENTE[0].get("user")}') \
    .option("password", f'{AMBIENTE[0].get("pass")}') \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .save()

# Liberando o dataframe da memória e disco
df_inscricao_fies_2021_tratado.unpersist()

# Dados do prouni
df_prouni_2020_bruto = spark.read \
    .option('encoding', 'ISO-8859-1') \
    .option('delimiter', ';') \
    .option('header', 'true') \
    .csv(f'{BUCKETS[0].get("s3_dados_brutos")}/prouni/ProuniRelatorioDadosAbertos2020.csv')

df_prouni_2020_tratado = df_prouni_2020_bruto.select(
    col('ANO_CONCESSAO_BOLSA').cast(IntegerType()),
    col('CODIGO_EMEC_IES_BOLSA').cast(IntegerType()),
    col('NOME_IES_BOLSA').cast(StringType()),
    col('TIPO_BOLSA').cast(StringType()),
    col('MODALIDADE_ENSINO_BOLSA').cast(StringType()),
    col('NOME_CURSO_BOLSA').cast(StringType()),
    col('NOME_TURNO_CURSO_BOLSA').cast(StringType()),
    col('CPF_BENEFICIARIO').cast(StringType()),
    col('SEXO_BENEFICIARIO').cast(StringType()),
    col('RACA_BENEFICIARIO').cast(StringType()),
    col('DATA_NASCIMENTO').cast(StringType()),
    col('BENEFICIARIO_DEFICIENTE_FISICO').cast(StringType()).alias('IS_BENEFICIARIO_DEFICIENTE_FISICO'),
    col('REGIAO_BENEFICIARIO').cast(StringType()),
    col('UF_BENEFICIARIO').cast(StringType()),
    col('MUNICIPIO_BENEFICIARIO').cast(StringType()),
)

df_prouni_2020_tratado \
    .coalesce(1) \
    .write \
    .mode('append') \
    .option('encoding', 'ISO-8859-1') \
    .csv(f'{BUCKETS[1].get("s3_dados_tratados")}/{DATE_NOW}/prouni/')

df_prouni_2020_tratado.write.mode("overwrite") \
    .format("jdbc") \
    .option('url', f'{AMBIENTE[0].get("prod-url")}') \
    .option("dbtable", 'PROUNI') \
    .option("user", f'{AMBIENTE[0].get("user")}') \
    .option("password", f'{AMBIENTE[0].get("pass")}') \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .save()

# Liberando o dataframe da memória e disco
df_prouni_2020_tratado.unpersist()


# Dados de clima Inmet
df_inmet_bruto = spark.read \
    .option('encoding', 'ISO-8859-1') \
    .option('delimiter', ';') \
    .option('header', 'true') \
    .csv(f'{BUCKETS[0].get("s3_dados_tratados")}/inmet/INMET_SE_SP_A771_SAO PAULO - INTERLAGOS_01-01-2021_A_31-12-2021.csv')

df_inmet_tratado = df_inmet_bruto.select(
    col('`Data`').cast(StringType()).alias('DATA'),
    col('`Hora UTC`').cast(StringType()).alias('HORA_UTC'),
    col('`PRECIPITAÇÃO TOTAL, HORÁRIO (mm)`').cast(DoubleType()).alias('PRECIPTACAO_TOTAL'),
    col('`PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)`').cast(DoubleType()).alias('PRESSAO_ATMOSFERICA_NIVEL_ESTACAO'),
    col('`PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)`').cast(DoubleType()).alias('PRESSAO_ATMOSFERICA_MAX'),
    col('`PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)`').cast(DoubleType()).alias('PRESSAO_ATMOSFERICA_MIN'),
    col('`RADIACAO GLOBAL (Kj/m²)`').cast(DoubleType()).alias('RADIACAO_GLOBAL'),
    col('`TEMPERATURA DO PONTO DE ORVALHO (°C)`').cast(DoubleType()).alias('TEMPERATURA_PONTO_ORVALHO'),
    col('`TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)`').cast(DoubleType()).alias('TEMPERATURA_MAX'),
    col('`TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)`').cast(DoubleType()).alias('TEMPERATURA_MIN'),
    col('`TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)`').cast(DoubleType()).alias('TEMPERATURA_ORVALHO_MAX'),
    col('`UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)`').cast(DoubleType()).alias('UMIDADE_RELATIVA_MAX'),
    col('`UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)`').cast(DoubleType()).alias('UMIDADE_RELATIVA_MIN'),
    col('`UMIDADE RELATIVA DO AR, HORARIA (%)`').cast(DoubleType()).alias('UMIDADE_RELATIVA_AR'),
    col('`VENTO, DIREÇÃO HORARIA (gr) (° (gr))`').cast(DoubleType()).alias('VENTO_DIRECAO_HORARIA'),
    col('`VENTO, RAJADA MAXIMA (m/s)`').cast(DoubleType()).alias('VENTO_REJADA_MAXIMA'),
    col('`VENTO, VELOCIDADE HORARIA (m/s)`').cast(DoubleType()).alias('VELOCIDADE_VENTO')
)

df_inmet_tratado \
    .coalesce(1) \
    .write \
    .mode('append') \
    .option('encoding', 'ISO-8859-1') \
    .csv(f'{BUCKETS[1].get("s3_dados_tratados")}/{DATE_NOW}/inmet/')

df_inmet_tratado.write.mode("overwrite") \
    .format("jdbc") \
    .option('url', f'{AMBIENTE[0].get("prod-url")}') \
    .option("dbtable", 'INMET_SP') \
    .option("user", f'{AMBIENTE[0].get("user")}') \
    .option("password", f'{AMBIENTE[0].get("pass")}') \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .save()

# Liberando o dataframe da memória e disco
df_inmet_tratado.unpersist()


# Itens prova ENEM
df_enem_itens_prova_bruto = spark.read \
    .option('delimiter', ';') \
    .option('header', 'true') \
    .csv(f'{BUCKETS[0].get("s3_dados_tratados")}/enem/ITENS_PROVA_2021.csv')


df_enem_itens_prova_tratado = df_enem_itens_prova_bruto.select(
    col('CO_POSICAO').cast(IntegerType()),
    col('SG_AREA').cast(StringType()),
    col('CO_ITEM').cast(IntegerType()),
    col('TX_GABARITO').cast(StringType()),
    col('CO_HABILIDADE').cast(IntegerType()),
    col('IN_ITEM_ABAN').cast(IntegerType()),
    col('TX_MOTIVO_ABAN').cast(StringType()),
    col('NU_PARAM_A').cast(DoubleType()),
    col('NU_PARAM_B').cast(DoubleType()),
    col('TX_COR').cast(StringType()),
    col('TP_LINGUA').cast(StringType()),
    col('IN_ITEM_ADAPTADO').cast(StringType())
)

df_enem_itens_prova_tratado \
    .coalesce(1) \
    .write \
    .mode('append') \
    .csv(f'{BUCKETS[1].get("s3_dados_tratados")}/{DATE_NOW}/enem/itens_prova/')

df_enem_itens_prova_tratado.write.mode("overwrite") \
    .format("jdbc") \
    .option('url', f'{AMBIENTE[0].get("prod-url")}') \
    .option("dbtable", 'ENEM_ITENS_PROVA') \
    .option("user", f'{AMBIENTE[0].get("user")}') \
    .option("password", f'{AMBIENTE[0].get("pass")}') \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .save()

# Liberando o dataframe da memória e disco
df_enem_itens_prova_tratado.unpersist()

df_enem_microdados_bruto = spark.read \
    .option('delimiter', ';') \
    .option('header', 'true') \
    .csv(f'{BUCKETS[0].get("s3_dados_tratados")}/enem/MICRODADOS_ENEM_2021.csv')

df_enem_microdados_tratado = df_enem_microdados_bruto.select(
    col('NU_INSCRICAO').cast(StringType()).alias('NUMERO_INSCRICAO'),
    col('NU_ANO').cast(IntegerType()).alias('ANO'),
    col('TP_FAIXA_ETARIA').cast(IntegerType()),
    col('TP_SEXO').cast(StringType()),
    col('TP_ESTADO_CIVIL').cast(IntegerType()).alias('COD_ESTADO_CIVIL'),
    col('TP_COR_RACA').cast(IntegerType()).alias('COD_COR_RACA'),
    col('TP_NACIONALIDADE').cast(IntegerType()).alias('COD_NACIONALIDADE'),
    col('TP_ST_CONCLUSAO').cast(IntegerType()).alias('SEMESTRE_CONCLUSAO'),
    col('TP_ANO_CONCLUIU').cast(IntegerType()).alias('ANO_CONCLUSAO'),
    col('TP_ESCOLA').cast(IntegerType()).alias('TIPO_ESCOLA'),
    col('TP_ENSINO').cast(IntegerType()).alias('TIPO_ENSINO'),
    col('IN_TREINEIRO').cast(IntegerType()),
    col('CO_MUNICIPIO_ESC').cast(IntegerType()).alias('COD_MUNICIPIO_ESCOLAR'),
    col('NO_MUNICIPIO_ESC').cast(StringType()).alias('NOME_MUNICIPIO_ESCOLAR'),
    col('CO_UF_ESC').cast(IntegerType()).alias('COD_UF_ESCOLAR'),
    col('SG_UF_ESC').cast(StringType()).alias('SIGLA_UF_ESCOLAR'),
    col('TP_DEPENDENCIA_ADM_ESC').cast(IntegerType()).alias('COD_TIPO_DEPENDENCIA_ADM_ESCOLAR'),
    col('TP_LOCALIZACAO_ESC').cast(IntegerType()).alias('COD_LOCALIZACAO_ESCOLAR'),
    col('TP_SIT_FUNC_ESC').cast(IntegerType()).alias('COD_SITUACAO_FUNCIONAMENTO_ESCOLAR'),
    col('CO_MUNICIPIO_PROVA').cast(IntegerType()).alias('COD_MUNICIPIO_PROVA'),
    col('CO_UF_PROVA').cast(StringType()).alias('COD_UF_PROVA'),
    col('NO_MUNICIPIO_PROVA').cast(StringType()).alias('NOME_MUNICIPIO_PROVA'),
    col('SG_UF_PROVA').cast(StringType()).alias('SIGLA_UF_PROVA'),
    col('TP_PRESENCA_CN').cast(IntegerType()).alias('COD_PRESENCA_PROVA_CIENCIA_NATUREZA'),
    col('TP_PRESENCA_CH').cast(IntegerType()).alias('COD_PRESENCA_CIENCIAS_HUMANAS'),
    col('TP_PRESENCA_LC').cast(IntegerType()).alias('COD_PRESENCA_LINGUAGENS_CODIGOS'),
    col('TP_PRESENCA_MT').cast(IntegerType()).alias('COD_PRESENCA_MATEMATICA'),
    col('CO_PROVA_CN').cast(IntegerType()).alias('COD_TIPO_PROVA_CIENCIA_NATUREZA'),
    col('CO_PROVA_CH').cast(IntegerType()).alias('COD_TIPO_PROVA_CIENCIAS_HUMANAS'),
    col('CO_PROVA_LC').cast(IntegerType()).alias('COD_TIPO_PROVA_LINGUAGENS_CODIGO'),
    col('CO_PROVA_MT').cast(IntegerType()).alias('COD_TIPO_PROVA_MATEMATICA'),
    col('NU_NOTA_CN').cast(DoubleType()).alias('NOTA_PROVA_CIENCIA_NATUREZA'),
    col('NU_NOTA_CH').cast(DoubleType()).alias('NOTA_PROVA_CIENCIAS_HUMANAS'),
    col('NU_NOTA_LC').cast(DoubleType()).alias('NOTA_PROVA_LINGUAGENS_CODIGO'),
    col('NU_NOTA_MT').cast(DoubleType()).alias('NOTA_PROVA_MATEMATICA'),
    col('TX_RESPOSTAS_CN').cast(StringType()).alias('RESPOSTAS_CIENCIA_NATUREZA'),

    col('TX_RESPOSTAS_CH').cast(StringType()).alias('RESPOSTAS_CIENCIAS_HUMANAS'),
    col('TX_RESPOSTAS_LC').cast(StringType()).alias('RESPOSTAS_LINGUAGENS_CODIGOS'),
    col('TX_RESPOSTAS_MT').cast(StringType()).alias('RESPOSTAS_MATEMATICA'),

    col('TP_LINGUA').cast(StringType()).alias('COD_LINGUAGEM_PROVA'),
    col('TX_GABARITO_CN').cast(StringType()).alias('GABARITO_CIENCIA_NATUREZA'),
    col('TX_GABARITO_CH').cast(StringType()).alias('GABARITO_CIENCIAS_HUMANAS'),
    col('TX_GABARITO_LC').cast(StringType()).alias('GABARITO_LINGUAGENS_CODIGOS'),
    col('TX_GABARITO_MT').cast(StringType()).alias('GABARITO_MATEMATICA'),

    col('TP_STATUS_REDACAO').cast(StringType()).alias('COD_STATUS_REDACAO'),
    col('NU_NOTA_COMP1').cast(IntegerType()).alias('NOTA_COMPETENCIA_1'),
    col('NU_NOTA_COMP2').cast(IntegerType()).alias('NOTA_COMPETENCIA_2'),
    col('NU_NOTA_COMP3').cast(IntegerType()).alias('NOTA_COMPETENCIA_3'),
    col('NU_NOTA_COMP4').cast(IntegerType()).alias('NOTA_COMPETENCIA_4'),
    col('NU_NOTA_COMP5').cast(IntegerType()).alias('NOTA_COMPETENCIA_5'),

    col('NU_NOTA_REDACAO').cast(IntegerType()).alias('NOTA_REDACAO'),
    col('Q001').cast(StringType()),
    col('Q002').cast(StringType()),
    col('Q003').cast(StringType()),
    col('Q004').cast(StringType()),
    col('Q005').cast(StringType()),
    col('Q006').cast(StringType()),
    col('Q007').cast(StringType()),
    col('Q008').cast(StringType()),
    col('Q009').cast(StringType()),
    col('Q010').cast(StringType()),
    col('Q011').cast(StringType()),
    col('Q012').cast(StringType()),
    col('Q013').cast(StringType()),
    col('Q014').cast(StringType()),
    col('Q015').cast(StringType()),
    col('Q016').cast(StringType()),
    col('Q017').cast(StringType()),
    col('Q018').cast(StringType()),
    col('Q019').cast(StringType()),
    col('Q020').cast(StringType()),
    col('Q021').cast(StringType()),
    col('Q022').cast(StringType()),
    col('Q023').cast(StringType()),
    col('Q024').cast(StringType()),
    col('Q025').cast(StringType())
)

df_enem_microdados_tratados = df_enem_microdados_tratado.limit(20_000)

df_enem_microdados_tratados \
    .coalesce(1) \
    .write \
    .mode('append') \
    .csv(f'{BUCKETS[1].get("s3_dados_tratados")}/{DATE_NOW}/enem/microdados/')

df_enem_microdados_tratados.write.mode("overwrite") \
    .format("jdbc") \
    .option('url', f'{AMBIENTE[0].get("prod-url")}') \
    .option("dbtable", 'ENEM_MICRODADOS') \
    .option("user", f'{AMBIENTE[0].get("user")}') \
    .option("password", f'{AMBIENTE[0].get("pass")}') \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .save()

