#!/usr/bin/env python3
"""
Ukázka práce s Apache Atlas pro metadata management v Cloudera ekosystému.
Tento skript demonstruje registraci a sledování metadat a datových lineage.
"""

import json
import requests
import base64
from datetime import datetime

class AtlasClient:
    """Jednoduchý klient pro komunikaci s Apache Atlas REST API."""
    
    def __init__(self, host="localhost", port=21000, username="admin", password="admin"):
        """Inicializace Atlas klienta."""
        self.base_url = f"http://{host}:{port}/api/atlas"
        self.auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def search_entity(self, query, limit=10):
        """Vyhledání entity podle DSL query."""
        url = f"{self.base_url}/v2/search/dsl"
        params = {"query": query, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Chyba při vyhledávání: {response.status_code}")
            print(response.text)
            return None
    
    def get_entity_by_guid(self, guid):
        """Získání detailu entity podle GUID."""
        url = f"{self.base_url}/v2/entity/guid/{guid}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Chyba při získávání entity: {response.status_code}")
            print(response.text)
            return None
    
    def create_entity(self, entity_def):
        """Vytvoření nové entity v Atlas."""
        url = f"{self.base_url}/v2/entity"
        response = requests.post(url, headers=self.headers, data=json.dumps(entity_def))
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Chyba při vytváření entity: {response.status_code}")
            print(response.text)
            return None
    
    def get_lineage(self, guid, depth=3, direction="BOTH"):
        """Získání lineage pro entitu."""
        url = f"{self.base_url}/v2/lineage/{guid}"
        params = {"depth": depth, "direction": direction}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Chyba při získávání lineage: {response.status_code}")
            print(response.text)
            return None

def atlas_demo():
    """Demonstrace práce s Apache Atlas v Cloudera."""
    # Vytvoření klienta pro Atlas
    client = AtlasClient(host="atlas-server", port=21000, username="admin", password="admin1234")
    
    # 1. Vyhledání všech Hive tabulek
    print("Vyhledávání Hive tabulek...")
    hive_tables = client.search_entity("from hive_table", limit=5)
    
    if hive_tables and "entities" in hive_tables:
        print(f"Nalezeno {len(hive_tables['entities'])} Hive tabulek:")
        for entity in hive_tables['entities']:
            print(f"  - {entity['displayText']} (GUID: {entity['guid']})")
        
        # Vybereme první tabulku pro další operace
        if len(hive_tables['entities']) > 0:
            table_guid = hive_tables['entities'][0]['guid']
            table_name = hive_tables['entities'][0]['displayText']
            
            # 2. Zobrazení detailu tabulky
            print(f"\nDetail tabulky {table_name}:")
            table_detail = client.get_entity_by_guid(table_guid)
            if table_detail:
                entity = table_detail['entity']
                print(f"Jméno: {entity['attributes'].get('name', 'N/A')}")
                print(f"Vytvořeno: {entity['attributes'].get('createTime', 'N/A')}")
                print(f"Popis: {entity['attributes'].get('description', 'N/A')}")
                
                # Zobrazení sloupců
                if 'columns' in entity['relationshipAttributes']:
                    print("\nSloupce:")
                    for column in entity['relationshipAttributes']['columns']:
                        print(f"  - {column['displayText']}")
            
            # 3. Zobrazení lineage pro tabulku
            print(f"\nLineage pro tabulku {table_name}:")
            lineage = client.get_lineage(table_guid)
            if lineage and 'relations' in lineage:
                print(f"Počet vztahů: {len(lineage['relations'])}")
                for relation in lineage['relations']:
                    print(f"  - {relation['fromEntityId']} -> {relation['toEntityId']}")
    
    # 4. Vytvoření nové entity (dataset)
    print("\nVytváření nové entity v Atlas...")
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dataset = {
        "entity": {
            "typeName": "hdfs_path",
            "attributes": {
                "name": f"/user/data/processed/example_{current_time}",
                "description": "Demonstrační dataset vytvořený pomocí Atlas API",
                "qualifiedName": f"/user/data/processed/example_{current_time}@cluster1",
                "path": f"/user/data/processed/example_{current_time}",
                "createTime": int(datetime.now().timestamp() * 1000),
                "modifiedTime": int(datetime.now().timestamp() * 1000),
                "owner": "data_engineer",
                "clusterName": "cluster1"
            },
            "classifications": [
                {
                    "typeName": "PII",
                    "attributes": {
                        "type": "CUSTOMER_INFO"
                    }
                },
                {
                    "typeName": "ETL",
                    "attributes": {
                        "pipeline": "daily_processing"
                    }
                }
            ]
        }
    }
    
    result = client.create_entity(new_dataset)
    if result and 'guidAssignments' in result:
        guid_values = list(result['guidAssignments'].values())
        if guid_values:
            new_guid = guid_values[0]
            print(f"Nová entita byla vytvořena s GUID: {new_guid}")
            
            # Zobrazení detailu nově vytvořené entity
            print("\nDetail nově vytvořené entity:")
            new_entity = client.get_entity_by_guid(new_guid)
            if new_entity and 'entity' in new_entity:
                print(json.dumps(new_entity['entity'], indent=2))

if __name__ == "__main__":
    print("===== Demonstrace Apache Atlas pro metadata management v Cloudera =====")
    atlas_demo()
    print("===== Konec demonstrace =====") 