import os
import pandas as pd
from google.cloud import bigquery
from typing import List, Dict, Any, Optional, Union

def initialize_client():
    """
    Inicializa e retorna o cliente BigQuery usando as credenciais configuradas.
    
    Returns:
        bigquery.Client: Cliente do BigQuery inicializado
    """
    # Verifica e define o caminho das credenciais se necessário
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        credenciais_path = "C:\\Users\\Vinicius\\Projetos\\agent_mcp_games\\valiant-complex-261112-341b439e39d3.json"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credenciais_path
    
    # Cria e retorna o cliente BigQuery
    client = bigquery.Client()
    return client

def list_datasets(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lista todos os datasets disponíveis no projeto.
    
    Args:
        project_id (str, optional): ID do projeto. Se não for fornecido, usa o projeto padrão.
        
    Returns:
        List[Dict]: Lista de datasets com seus IDs e nomes.
    """
    client = initialize_client()
    datasets = list(client.list_datasets(project=project_id))
    
    result = []
    if datasets:
        for dataset in datasets:
            result.append({
                "dataset_id": dataset.dataset_id,
                "full_path": f"{dataset.project}.{dataset.dataset_id}"
            })
    
    return result

def list_tables(dataset_id: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lista todas as tabelas de um dataset específico.
    
    Args:
        dataset_id (str): ID do dataset
        project_id (str, optional): ID do projeto. Se não for fornecido, usa o projeto padrão.
        
    Returns:
        List[Dict]: Lista de tabelas com seus IDs e esquema.
    """
    client = initialize_client()
    
    if project_id:
        dataset_ref = client.dataset(dataset_id, project=project_id)
    else:
        dataset_ref = client.dataset(dataset_id)
    
    tables = list(client.list_tables(dataset_ref))
    
    result = []
    if tables:
        for table in tables:
            result.append({
                "table_id": table.table_id,
                "full_path": f"{table.project}.{table.dataset_id}.{table.table_id}"
            })
    
    return result

def execute_query(query: str) -> pd.DataFrame:
    """
    Executa uma query SQL no BigQuery e retorna os resultados.
    
    Args:
        query (str): Query SQL a ser executada
        
    Returns:
        DataFrame: Resultado da query em formato DataFrame
    """
    client = initialize_client()
    
    try:
        query_job = client.query(query)
        results = query_job.result()
        
        # Converte para DataFrame
        df = results.to_dataframe()
        return df
        
    except Exception as e:
        print(f"Erro ao executar a query: {e}")
        raise

def get_table_data(table_id: str, dataset_id: str, project_id: Optional[str] = None, 
                   limit: Optional[int] = 1000) -> pd.DataFrame:
    """
    Obtém dados de uma tabela específica.
    
    Args:
        table_id (str): ID da tabela
        dataset_id (str): ID do dataset
        project_id (str, optional): ID do projeto. Se não for fornecido, usa o projeto padrão.
        limit (int, optional): Limite de linhas a retornar. Padrão é 1000.
        
    Returns:
        DataFrame: Dados da tabela em formato DataFrame
    """
    if project_id:
        full_table_id = f"{project_id}.{dataset_id}.{table_id}"
    else:
        client = initialize_client()
        full_table_id = f"{client.project}.{dataset_id}.{table_id}"
    
    query = f"SELECT * FROM `{full_table_id}` LIMIT {limit}"
    return execute_query(query)

def insert_rows(table_id: str, dataset_id: str, rows_data: List[Dict[str, Any]], 
                project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Insere novas linhas em uma tabela.
    
    Args:
        table_id (str): ID da tabela
        dataset_id (str): ID do dataset
        rows_data (List[Dict]): Lista de dicionários com os dados a serem inseridos
        project_id (str, optional): ID do projeto. Se não for fornecido, usa o projeto padrão.
        
    Returns:
        Dict: Resultado da operação com status e erros (se houver)
    """
    client = initialize_client()
    
    if project_id:
        table_ref = client.dataset(dataset_id, project=project_id).table(table_id)
    else:
        table_ref = client.dataset(dataset_id).table(table_id)
    
    table = client.get_table(table_ref)
    
    try:
        errors = client.insert_rows_json(table, rows_data)
        if not errors:
            return {"success": True, "message": f"{len(rows_data)} linhas inseridas com sucesso"}
        else:
            return {"success": False, "errors": errors}
    except Exception as e:
        return {"success": False, "error": str(e)}

def replace_table(table_id: str, dataset_id: str, data: Union[pd.DataFrame, List[Dict]], 
                  schema: Optional[List[bigquery.SchemaField]] = None, 
                  project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Substitui uma tabela existente por novos dados ou cria uma nova tabela.
    
    Args:
        table_id (str): ID da tabela
        dataset_id (str): ID do dataset
        data (DataFrame ou List[Dict]): Dados para a nova tabela
        schema (List[SchemaField], optional): Esquema da tabela. Se não for fornecido e data for um DataFrame,
                                              o esquema será inferido.
        project_id (str, optional): ID do projeto. Se não for fornecido, usa o projeto padrão.
        
    Returns:
        Dict: Resultado da operação
    """
    client = initialize_client()
    
    if project_id:
        dataset_ref = client.dataset(dataset_id, project=project_id)
    else:
        dataset_ref = client.dataset(dataset_id)
    
    table_ref = dataset_ref.table(table_id)
    
    # Converte para DataFrame se for uma lista de dicionários
    if isinstance(data, list) and isinstance(data[0], dict):
        data = pd.DataFrame(data)
    
    job_config = bigquery.LoadJobConfig()
    
    if schema:
        job_config.schema = schema
    else:
        # Auto-detecção de esquema
        job_config.autodetect = True
    
    # Configura para substituir a tabela
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    
    try:
        # Carrega os dados para a tabela
        job = client.load_table_from_dataframe(data, table_ref, job_config=job_config)
        job.result()  # Aguarda a conclusão do job
        
        # Obtém a tabela atualizada
        table = client.get_table(table_ref)
        
        return {
            "success": True,
            "message": f"Tabela {table_id} substituída com sucesso",
            "num_rows": table.num_rows
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_dataset(dataset_id: str, project_id: Optional[str] = None, 
                   location: str = "US") -> Dict[str, Any]:
    """
    Cria um novo dataset no BigQuery.
    
    Args:
        dataset_id (str): ID do dataset a ser criado
        project_id (str, optional): ID do projeto. Se não for fornecido, usa o projeto padrão.
        location (str, optional): Localização dos dados. Padrão é "US".
        
    Returns:
        Dict: Resultado da operação
    """
    client = initialize_client()
    
    dataset = bigquery.Dataset(f"{project_id or client.project}.{dataset_id}")
    dataset.location = location
    
    try:
        dataset = client.create_dataset(dataset)
        return {
            "success": True,
            "message": f"Dataset {dataset_id} criado com sucesso",
            "full_path": dataset.full_dataset_id
        }
    except Exception as e:
        return {"success": False, "error": str(e)}