import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import base64

from config.settings import settings
from src.utils.logger import logger
from src.utils.exceptions import (
    AzureDevOpsAPIError, 
    AuthenticationError, 
    WorkItemNotFoundError, 
    BoardNotFoundError
)

@dataclass
class WorkItem:
    """Represents a work item from Azure DevOps"""
    id: int
    title: str
    work_item_type: str
    state: str
    priority: int
    assigned_to: Optional[str]
    created_date: datetime
    changed_date: datetime
    description: Optional[str]
    tags: List[str]
    area_path: str
    iteration_path: str
    url: str

@dataclass
class Board:
    """Represents a board from Azure DevOps"""
    id: str
    name: str
    board_type: str
    url: str

class AzureDevOpsService:
    """Service for interacting with Azure DevOps REST API"""
    
    def __init__(self):
        self.config = settings.azure_devops
        self.base_url = f"{self.config.base_url}/{self.config.organization}"
        self.headers = self._get_headers()
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        logger.info(f"Initialized Azure DevOps service for organization: {self.config.organization}, project: {self.config.project}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        credentials = f":{self.config.personal_access_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Azure DevOps API"""
        url = f"{self.base_url}/{endpoint}"
        try:
            logger.debug(f"Making request to: {url} (method={method})")
            if method == 'POST':
                response = self.session.post(url, params=params, json=data, timeout=30, headers=self.headers)
            else:
                response = self.session.get(url, params=params, timeout=30, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if response.status_code == 401:
                raise AuthenticationError("Invalid credentials. Please check your Personal Access Token.")
            elif response.status_code == 404:
                raise AzureDevOpsAPIError(f"Resource not found: {endpoint}", 404)
            else:
                raise AzureDevOpsAPIError(f"API request failed: {e}", response.status_code if 'response' in locals() else None)
    
    def test_connection(self) -> bool:
        """Test connection to Azure DevOps API"""
        try:
            # Try to get project info
            response = self._make_request("_apis/project")
            logger.info("Successfully connected to Azure DevOps API")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def validate_credentials(self) -> Dict[str, Any]:
        """Validate Azure DevOps credentials and return user info"""
        try:
            # Get current user info
            response = self._make_request("_apis/connectionData")
            
            user_info = {
                'authenticated': True,
                'user_id': response.get('authenticatedUser', {}).get('id'),
                'user_name': response.get('authenticatedUser', {}).get('displayName'),
                'organization': self.config.organization,
                'project': self.config.project
            }
            
            logger.info(f"Credentials validated for user: {user_info['user_name']}")
            return user_info
            
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return {
                'authenticated': False,
                'error': str(e)
            }
    
    def get_boards(self) -> List[Board]:
        """Get all boards for the project"""
        try:
            response = self._make_request(f"/{self.config.project}/_apis/work/boards", params={'api-version': '7.0'})
            boards = []
            
            for board in response.get('value', []):
                boards.append(Board(
                    id=board['id'],
                    name=board['name'],
                    board_type=board.get('boardType', 'Unknown'),
                    url=board['url']
                ))
            
            logger.info(f"Retrieved {len(boards)} boards")
            return boards
            
        except Exception as e:
            logger.error(f"Failed to get boards: {e}")
            raise
    
    def get_board_by_id(self, board_id: str) -> Optional[Board]:
        """Get a specific board by ID"""
        try:
            response = self._make_request(f"_apis/work/boards/{board_id}")
            
            board = Board(
                id=response['id'],
                name=response['name'],
                board_type=response.get('boardType', 'Unknown'),
                url=response['url']
            )
            
            logger.info(f"Retrieved board: {board.name}")
            return board
            
        except AzureDevOpsAPIError as e:
            if e.status_code == 404:
                raise BoardNotFoundError(board_id)
            raise
        except Exception as e:
            logger.error(f"Failed to get board {board_id}: {e}")
            raise
    
    def get_work_items(self, 
                      work_item_types: Optional[List[str]] = None,
                      state: Optional[str] = None,
                      assigned_to: Optional[str] = None,
                      top: int = 100) -> List[WorkItem]:
        """Get work items with optional filtering"""
        
        # Build WIQL query
        wiql = self._build_wiql_query(work_item_types, state, assigned_to)
        # Log WIQL query
        logger.info(f"WIQL gerado:\n{wiql}")
        # Remover quebras de linha e espaços desnecessários
        wiql_clean = ' '.join(wiql.strip().split())
        logger.info(f"WIQL enviado (compactado): {wiql_clean}")
        try:
            # Montar endpoint WIQL correto (sem organization no path)
            proj = self.config.project
            team = self.config.team.strip()
            if team:
                wiql_endpoint = f"{proj}/{team}/_apis/wit/wiql"
            else:
                wiql_endpoint = f"{proj}/_apis/wit/wiql"
            # Execute WIQL query (POST)
            query_response = self._make_request(wiql_endpoint, 
                                             params={'api-version': '5.0'},
                                             method='POST',
                                             data={'query': wiql_clean})
            
            # Get work item IDs from query result
            work_item_ids = [item['id'] for item in query_response.get('workItems', [])]
            
            if not work_item_ids:
                return []
            
            # Get detailed work item information
            work_items = self._get_work_item_details(work_item_ids[:top])
            
            logger.info(f"Retrieved {len(work_items)} work items")
            return work_items
            
        except Exception as e:
            logger.error(f"Failed to get work items: {e}")
            raise
    
    def get_product_backlog_items(self, state: Optional[str] = None, top: int = 100) -> List[WorkItem]:
        """Get Product Backlog Items"""
        return self.get_work_items(work_item_types=['Product Backlog Item'], state=state, top=top)
    
    def get_bugs(self, state: Optional[str] = None, top: int = 100) -> List[WorkItem]:
        """Get Bugs"""
        return self.get_work_items(work_item_types=['Bug'], state=state, top=top)
    
    def get_features(self, state: Optional[str] = None, top: int = 100) -> List[WorkItem]:
        """Get Features"""
        return self.get_work_items(work_item_types=['Feature'], state=state, top=top)
    
    def get_backlog_items(self, include_types: List[str] = None, state: Optional[str] = None, top: int = 100) -> List[WorkItem]:
        """Get all backlog items (PBI, Bug, Feature)"""
        if include_types is None:
            include_types = ['Product Backlog Item', 'Bug', 'Feature']
        
        return self.get_work_items(work_item_types=include_types, state=state, top=top)
    
    def _build_wiql_query(self, 
                          work_item_types: Optional[List[str]] = None,
                          state: Optional[str] = None,
                          assigned_to: Optional[str] = None) -> str:
        """Build WIQL query string"""
        
        conditions = []
        # Filtro obrigatório pelo projeto
        conditions.append(f"[System.TeamProject] = '{self.config.project}'")
        # Work item types
        if work_item_types:
            type_conditions = [f"[System.WorkItemType] = '{item_type}'" for item_type in work_item_types]
            conditions.append(f"({' OR '.join(type_conditions)})")
        # State filter
        if state:
            conditions.append(f"[System.State] = '{state}'")
        # Assigned to filter
        if assigned_to:
            conditions.append(f"[System.AssignedTo] = '{assigned_to}'")
        # Build final query
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        return f"SELECT [System.Id] FROM WorkItems WHERE {where_clause} ORDER BY [System.ChangedDate] DESC"
    
    def _get_work_item_details(self, work_item_ids: List[int]) -> List[WorkItem]:
        """Get detailed information for work items"""
        
        if not work_item_ids:
            return []
        
        # Get work items in batches
        batch_size = 200
        all_work_items = []
        
        for i in range(0, len(work_item_ids), batch_size):
            batch_ids = work_item_ids[i:i + batch_size]
            ids_param = ','.join(map(str, batch_ids))
            
            response = self._make_request(f"_apis/wit/workitems", 
                                       params={'ids': ids_param, 'api-version': '7.0'})
            
            for item in response.get('value', []):
                work_item = self._parse_work_item(item)
                all_work_items.append(work_item)
        
        return all_work_items
    
    def _parse_work_item(self, item_data: Dict) -> WorkItem:
        """Parse work item data from API response"""
        
        fields = item_data.get('fields', {})
        
        return WorkItem(
            id=item_data['id'],
            title=fields.get('System.Title', ''),
            work_item_type=fields.get('System.WorkItemType', ''),
            state=fields.get('System.State', ''),
            priority=fields.get('Microsoft.VSTS.Common.Priority', 0),
            assigned_to=fields.get('System.AssignedTo', {}).get('displayName') if fields.get('System.AssignedTo') else None,
            created_date=datetime.fromisoformat(fields.get('System.CreatedDate', '').replace('Z', '+00:00')),
            changed_date=datetime.fromisoformat(fields.get('System.ChangedDate', '').replace('Z', '+00:00')),
            description=fields.get('System.Description', ''),
            tags=fields.get('System.Tags', '').split(';') if fields.get('System.Tags') else [],
            area_path=fields.get('System.AreaPath', ''),
            iteration_path=fields.get('System.IterationPath', ''),
            url=item_data['url']
        )
    
    def get_work_item_by_id(self, work_item_id: int) -> Optional[WorkItem]:
        """Get a specific work item by ID"""
        try:
            response = self._make_request(f"_apis/wit/workItems/{work_item_id}")
            work_item = self._parse_work_item(response)
            
            logger.info(f"Retrieved work item {work_item_id}")
            return work_item
            
        except AzureDevOpsAPIError as e:
            if e.status_code == 404:
                raise WorkItemNotFoundError(work_item_id)
            raise
        except Exception as e:
            logger.error(f"Failed to get work item {work_item_id}: {e}")
            raise
    
    def get_work_item_details(self, work_item_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed work item information including all fields"""
        try:
            response = self._make_request(f"_apis/wit/workItems/{work_item_id}")
            
            # Get work item history
            history_response = self._make_request(f"_apis/wit/workItems/{work_item_id}/updates")
            
            # Get work item links
            links_response = self._make_request(f"_apis/wit/workItems/{work_item_id}/links")
            
            details = {
                'work_item': self._parse_work_item(response),
                'history': history_response.get('value', []),
                'links': links_response.get('value', []),
                'raw_data': response
            }
            
            logger.info(f"Retrieved detailed information for work item {work_item_id}")
            return details
            
        except Exception as e:
            logger.error(f"Failed to get work item details {work_item_id}: {e}")
            return None
    
    def search_work_items(self, search_text: str, work_item_types: Optional[List[str]] = None) -> List[WorkItem]:
        """Search work items by text"""
        
        # Build search query
        search_conditions = []
        
        if work_item_types:
            type_conditions = [f"[System.WorkItemType] = '{item_type}'" for item_type in work_item_types]
            search_conditions.append(f"({' OR '.join(type_conditions)})")
        
        search_conditions.append(f"[System.Title] CONTAINS '{search_text}' OR [System.Description] CONTAINS '{search_text}'")
        
        where_clause = " AND ".join(search_conditions)
        
        wiql = f"""
        SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State], 
               [System.Priority], [System.AssignedTo], [System.CreatedDate], 
               [System.ChangedDate], [System.Description], [System.Tags], 
               [System.AreaPath], [System.IterationPath]
        FROM WorkItems
        WHERE {where_clause}
        ORDER BY [System.ChangedDate] DESC
        """
        
        try:
            # Execute search query
            response = self._make_request("_apis/wit/wiql", 
                                       params={'api-version': '7.0'})
            
            work_item_ids = [item['id'] for item in response.get('workItems', [])]
            work_items = self._get_work_item_details(work_item_ids)
            
            logger.info(f"Search found {len(work_items)} work items for '{search_text}'")
            return work_items
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise 

    def get_project_info(self) -> dict:
        """Fetch project info from Azure DevOps API"""
        try:
            # Consulta informações do projeto
            project_response = self._make_request(f"_apis/projects/{self.config.project_id}")
            # Consulta times do projeto (opcional)
            teams_response = self._make_request(f"_apis/projects/{self.config.project_id}/teams")
            team_name = teams_response.get('value', [{}])[0].get('name', 'N/A') if teams_response.get('value') else 'N/A'
            
            return {
                "organization": self.config.organization,
                "project": project_response.get('name', self.config.project),
                "team": team_name,
                "url": project_response.get('url', self.base_url)
            }
        except Exception as e:
            logger.error(f"Failed to fetch project info: {e}")
            return {
                "organization": self.config.organization,
                "project": self.config.project,
                "team": "Erro",
                "url": self.base_url
            } 