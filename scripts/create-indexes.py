"""Create Azure AI Search indexes for supply profiles and job descriptions.

Usage:
    uv run python scripts/create-indexes.py
"""

import os

from dotenv import load_dotenv

load_dotenv()

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
VECTOR_DIMS = 1536  # text-embedding-3-small output dimensions

credential = AzureKeyCredential(API_KEY) if API_KEY else DefaultAzureCredential()
index_client = SearchIndexClient(endpoint=ENDPOINT, credential=credential)


# ---------------------------------------------------------------------------
# Vector search configuration (shared by both indexes)
# ---------------------------------------------------------------------------

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="hnsw-config"),
    ],
    profiles=[
        VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw-config"),
    ],
)


# ---------------------------------------------------------------------------
# Supply profiles index
# ---------------------------------------------------------------------------

supply_index = SearchIndex(
    name=os.getenv("AZURE_SEARCH_SUPPLY_INDEX", "supply-profiles"),
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SimpleField(name="employee_id", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="employee_name", type=SearchFieldDataType.String),
        SimpleField(name="band", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="availability_from", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="ageing_bucket", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="work_mode", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="location", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="experience", type=SearchFieldDataType.String),
        SearchableField(name="role_name", type=SearchFieldDataType.String),
        SimpleField(name="country", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="skills_iaspire", type=SearchFieldDataType.String),
        SearchableField(name="certified_skills", type=SearchFieldDataType.String),
        SearchableField(name="trained_skills", type=SearchFieldDataType.String),
        SearchableField(name="recent_skills", type=SearchFieldDataType.String),
        SearchableField(name="language_skills", type=SearchFieldDataType.String),
        SearchableField(name="role_cluster", type=SearchFieldDataType.String, filterable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMS,
            vector_search_profile_name="vector-profile",
        ),
    ],
    vector_search=vector_search,
)


# ---------------------------------------------------------------------------
# JD (job descriptions / demands) index
# ---------------------------------------------------------------------------

jd_index = SearchIndex(
    name=os.getenv("AZURE_JD_SEARCH_INDEX_NAME", "jd-index"),
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SimpleField(name="demand_id", type=SearchFieldDataType.Int32, filterable=True),
        SearchableField(name="customer_name", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="essential_skill", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="location", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="country", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="created_on", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="start_date", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="end_date", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="role_description", type=SearchFieldDataType.String),
        SimpleField(name="work_mode", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="band", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="open_positions", type=SearchFieldDataType.Int32, filterable=True),
        SearchableField(name="job_description", type=SearchFieldDataType.String),
        SearchableField(name="role_cluster", type=SearchFieldDataType.String, filterable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMS,
            vector_search_profile_name="vector-profile",
        ),
    ],
    vector_search=vector_search,
)


# ---------------------------------------------------------------------------
# Create or update indexes
# ---------------------------------------------------------------------------

for index in [supply_index, jd_index]:
    result = index_client.create_or_update_index(index)
    print(f"✓ Index '{result.name}' created/updated")
