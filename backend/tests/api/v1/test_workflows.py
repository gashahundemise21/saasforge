import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.models.workflow import Workflow


@pytest.mark.asyncio
async def test_create_and_get_workflow(
    auth_client: AsyncClient, db_session: AsyncSession, test_user
):
    # 1. Create org
    org_res = await auth_client.post(
        "/api/v1/organizations", json={"name": "Workflow Org", "slug": "workflow-org"}
    )
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]
    org_slug = org_res.json()["slug"]

    # 2. Create workflow
    workflow_data = {
        "name": "On Task Created",
        "description": "Send webhook when task is created",
        "trigger_type": "task.created",
        "is_active": True,
        "actions": [
            {
                "action_type": "webhook",
                "config": {"url": "https://example.com"},
                "order": 1
            }
        ]
    }
    create_res = await auth_client.post(
        "/api/v1/workflows",
        json=workflow_data,
        headers={"X-Organization-Slug": org_slug}
    )
    print(create_res.json())
    assert create_res.status_code == 201
    created_workflow = create_res.json()
    assert created_workflow["name"] == "On Task Created"
    assert len(created_workflow["actions"]) == 1
    assert created_workflow["actions"][0]["action_type"] == "webhook"

    workflow_id = created_workflow["id"]

    # 3. Get workflow
    get_res = await auth_client.get(
        f"/api/v1/workflows/{workflow_id}",
        headers={"X-Organization-Slug": org_slug}
    )
    assert get_res.status_code == 200
    assert get_res.json()["id"] == workflow_id
    
    # 4. List workflows
    list_res = await auth_client.get(
        "/api/v1/workflows",
        headers={"X-Organization-Slug": org_slug}
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["id"] == workflow_id

