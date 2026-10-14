import sys
sys.path.insert(0, ".")
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient
import httpx

from backend.main import app
from backend.core.config import settings
from backend.services.stix_validator import STIXValidator, STIXValidationError
from backend.services.misp_client import MISPClient, MISPClientError, MISPConfigurationError
from backend.services.opencti_client import OpenCTIClient, OpenCTIClientError, OpenCTIConfigurationError

client = TestClient(app)

TENANT_A = "00000000-0000-0000-0000-00000000006a"
TENANT_B = "00000000-0000-0000-0000-00000000006b"
HEADERS_A = {"X-Tenant-ID": TENANT_A}
HEADERS_B = {"X-Tenant-ID": TENANT_B}


# ============================================================================
# 1. STIX 2.1 Validator Unit Tests
# ============================================================================

def test_stix_validator_supported_types():
    assert STIXValidator.validate_object_type("indicator") == "indicator"
    assert STIXValidator.validate_object_type("malware") == "malware"
    assert STIXValidator.validate_object_type("threat-actor") == "threat-actor"
    assert STIXValidator.validate_object_type("ipv4-addr") == "ipv4-addr"
    assert STIXValidator.validate_object_type("relationship") == "relationship"

    with pytest.raises(STIXValidationError) as exc:
        STIXValidator.validate_object_type("invalid-unsupported-type")
    assert "Unsupported STIX 2.1 object type" in str(exc.value)


def test_stix_validator_id_format():
    valid_uuid = str(uuid.uuid4())
    valid_id = f"indicator--{valid_uuid}"
    # Should succeed without error
    STIXValidator.validate_stix_id(valid_id, expected_type="indicator")

    # Mismatched type prefix
    with pytest.raises(STIXValidationError):
        STIXValidator.validate_stix_id(valid_id, expected_type="malware")

    # Invalid non-UUID format
    with pytest.raises(STIXValidationError):
        STIXValidator.validate_stix_id("indicator--not-a-valid-uuid")


def test_stix_validator_spec_version_and_confidence():
    assert STIXValidator.validate_spec_version("2.1") == "2.1"
    with pytest.raises(STIXValidationError):
        STIXValidator.validate_spec_version("1.2")

    assert STIXValidator.validate_confidence(85) == 85
    assert STIXValidator.validate_confidence(0) == 0
    assert STIXValidator.validate_confidence(100) == 100

    with pytest.raises(STIXValidationError):
        STIXValidator.validate_confidence(-5)
    with pytest.raises(STIXValidationError):
        STIXValidator.validate_confidence(150)


def test_stix_validator_timestamps():
    now = datetime.utcnow()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    # Valid order
    res = STIXValidator.validate_timestamps(created=past, modified=now, valid_from=past, valid_until=future)
    assert res["created"] == past
    assert res["valid_until"] == future

    # Invalid modified before created
    with pytest.raises(STIXValidationError):
        STIXValidator.validate_timestamps(created=future, modified=past)

    # Invalid valid_until before valid_from
    with pytest.raises(STIXValidationError):
        STIXValidator.validate_timestamps(valid_from=future, valid_until=past)


def test_stix_validator_patterns():
    # Valid indicator STIX pattern
    STIXValidator.validate_pattern("[ipv4-addr:value = '198.51.100.1']", pattern_type="stix", obj_type="indicator")
    STIXValidator.validate_pattern("[domain-name:value = 'malicious.xyz']", pattern_type="stix", obj_type="indicator")

    # Indicator missing pattern
    with pytest.raises(STIXValidationError):
        STIXValidator.validate_pattern("", pattern_type="stix", obj_type="indicator")

    # Malformed bracket syntax
    with pytest.raises(STIXValidationError):
        STIXValidator.validate_pattern("ipv4-addr:value = '1.2.3.4'", pattern_type="stix", obj_type="indicator")


# ============================================================================
# 2. STIX 2.1 API & Lifecycle & Cross-Tenant Collision Tests
# ============================================================================

def test_stix_create_and_lifecycle_fields():
    indicator_id = f"indicator--{uuid.uuid4()}"
    valid_from = (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z"
    valid_until = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"

    payload = {
        "stix_id": indicator_id,
        "type": "indicator",
        "spec_version": "2.1",
        "name": "C2 Server IPv4",
        "description": "Observed active command-and-control IP",
        "pattern": "[ipv4-addr:value = '203.0.113.55']",
        "pattern_type": "stix",
        "valid_from": valid_from,
        "valid_until": valid_until,
        "revoked": False,
        "source": "ThreatStream-Alpha",
        "confidence": 90,
        "labels": ["malicious-activity", "c2"],
    }

    resp = client.post("/api/v1/stix/objects", json=payload, headers=HEADERS_A)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["stix_id"] == indicator_id
    assert data["pattern_type"] == "stix"
    assert data["revoked"] is False
    assert data["source"] == "ThreatStream-Alpha"
    assert data["confidence"] == 90

    # Retrieve by ID
    get_resp = client.get(f"/api/v1/stix/objects/{indicator_id}", headers=HEADERS_A)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "C2 Server IPv4"


def test_stix_validation_rejection_via_api():
    # Attempting to post invalid confidence score > 100
    payload = {
        "type": "indicator",
        "pattern": "[ipv4-addr:value = '10.0.0.1']",
        "confidence": 999,
    }
    resp = client.post("/api/v1/stix/objects", json=payload, headers=HEADERS_A)
    assert resp.status_code == 422
    assert "validation failure" in resp.text.lower()


def test_stix_cross_tenant_collision_and_isolation():
    shared_uuid = str(uuid.uuid4())
    shared_id = f"indicator--{shared_uuid}"

    # Tenant A stores indicator
    payload_a = {
        "stix_id": shared_id,
        "type": "indicator",
        "name": "Tenant A Secret Indicator",
        "pattern": "[ipv4-addr:value = '198.51.100.99']",
        "confidence": 80,
    }
    resp_a = client.post("/api/v1/stix/objects", json=payload_a, headers=HEADERS_A)
    assert resp_a.status_code == 201

    # Tenant B stores indicator with SAME stix_id
    payload_b = {
        "stix_id": shared_id,
        "type": "indicator",
        "name": "Tenant B Distinct Indicator",
        "pattern": "[domain-name:value = 'tenant-b.com']",
        "confidence": 75,
    }
    resp_b = client.post("/api/v1/stix/objects", json=payload_b, headers=HEADERS_B)
    assert resp_b.status_code == 201

    # Tenant A's record must remain unchanged
    get_a = client.get(f"/api/v1/stix/objects/{shared_id}", headers=HEADERS_A)
    assert get_a.status_code == 200
    assert get_a.json()["name"] == "Tenant A Secret Indicator"

    # Tenant B querying its object gets Tenant B's data
    get_b = client.get(f"/api/v1/stix/objects/{shared_id}", headers=HEADERS_B)
    assert get_b.status_code == 200
    assert get_b.json()["name"] == "Tenant B Distinct Indicator"


# ============================================================================
# 3. MISP Client & Adapter Tests (Mocked)
# ============================================================================

def test_misp_unconfigured_provider():
    with patch.object(settings, "MISP_URL", None), patch.object(settings, "MISP_API_KEY", None):
        assert not MISPClient.is_configured()

        # Check status endpoint
        status_resp = client.get("/api/v1/intel/status")
        assert status_resp.status_code == 200
        assert status_resp.json()["misp"]["configured"] is False

        # Calling live fetch returns unconfigured response
        fetch_resp = client.post("/api/v1/intel/misp/fetch", json={"page": 1}, headers=HEADERS_A)
        assert fetch_resp.status_code == 200
        assert fetch_resp.json()["status"] == "UNCONFIGURED"


@pytest.mark.asyncio
async def test_misp_live_client_mocked_fetch_and_sync():
    mock_misp_response = {
        "response": [
            {
                "Event": {
                    "info": "APT29 Phishing Campaign",
                    "Attribute": [
                        {
                            "type": "ip-dst",
                            "value": "192.0.2.144",
                            "category": "Network activity",
                            "timestamp": "1700000000",
                        },
                        {
                            "type": "domain",
                            "value": "apt29-c2-dropzone.org",
                            "category": "Network activity",
                            "timestamp": "1700000000",
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_misp_response

    with patch.object(settings, "MISP_URL", "https://misp.example.org"), \
         patch.object(settings, "MISP_API_KEY", "misp-test-token-12345"), \
         patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:

        mock_request.return_value = mock_resp

        fetch_resp = client.post(
            "/api/v1/intel/misp/fetch",
            json={"page": 1, "limit": 25},
            headers=HEADERS_A
        )
        assert fetch_resp.status_code == 200, fetch_resp.text
        data = fetch_resp.json()
        assert data["status"] == "SUCCESS"
        assert data["events_processed"] == 1
        assert data["stix_objects_ingested"] == 2

        # Verify authentication headers and payload sent
        mock_request.assert_called_once()
        _, kwargs = mock_request.call_args
        assert kwargs["headers"]["Authorization"] == "misp-test-token-12345"
        assert kwargs["json"]["page"] == 1
        assert kwargs["json"]["limit"] == 25


@pytest.mark.asyncio
async def test_misp_retry_and_backoff_on_transient_error():
    mock_error_resp = MagicMock()
    mock_error_resp.status_code = 503
    mock_error_resp.text = "Service Unavailable"

    mock_success_resp = MagicMock()
    mock_success_resp.status_code = 200
    mock_success_resp.json.return_value = {"response": []}

    with patch.object(settings, "MISP_URL", "https://misp.example.org"), \
         patch.object(settings, "MISP_API_KEY", "valid-key"), \
         patch.object(settings, "MISP_MAX_RETRIES", 2), \
         patch.object(settings, "MISP_BACKOFF_FACTOR", 0.01), \
         patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_req:

        # First call fails with 503, second succeeds with 200
        mock_req.side_effect = [mock_error_resp, mock_success_resp]

        result = await MISPClient.fetch_events(page=1)
        assert result == {"response": []}
        assert mock_req.call_count == 2


def test_misp_payload_sync_compatibility():
    payload = {
        "misp_payload": {
            "Event": {
                "info": "Legacy Payload Feed Test",
                "Attribute": [
                    {
                        "type": "sha256",
                        "value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "category": "Payload delivery"
                    }
                ]
            }
        }
    }
    resp = client.post("/api/v1/intel/misp/sync", json=payload, headers=HEADERS_A)
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"
    assert resp.json()["stix_objects_ingested"] >= 1


# ============================================================================
# 4. OpenCTI Client & Adapter Tests (Mocked)
# ============================================================================

def test_opencti_unconfigured_provider():
    with patch.object(settings, "OPENCTI_URL", None), patch.object(settings, "OPENCTI_API_KEY", None):
        assert not OpenCTIClient.is_configured()

        resp = client.post("/api/v1/intel/opencti/fetch", json={"first": 10}, headers=HEADERS_A)
        assert resp.status_code == 200
        assert resp.json()["status"] == "UNCONFIGURED"


@pytest.mark.asyncio
async def test_opencti_live_client_mocked_fetch_and_sync():
    mock_opencti_graphql = {
        "data": {
            "indicators": {
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": "cursor123"
                },
                "edges": [
                    {
                        "node": {
                            "id": "opencti-node-101",
                            "standard_id": f"indicator--{uuid.uuid4()}",
                            "entity_type": "indicator",
                            "name": "Cobalt Strike Beacon URL",
                            "description": "Known staging endpoint",
                            "pattern": "[url:value = 'https://malware-beacon.test/gate.php']",
                            "pattern_type": "stix",
                            "confidence": 95,
                            "valid_from": "2026-01-01T00:00:00Z",
                            "revoked": False,
                        }
                    }
                ]
            }
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_opencti_graphql

    with patch.object(settings, "OPENCTI_URL", "http://opencti.example.org/graphql"), \
         patch.object(settings, "OPENCTI_API_KEY", "opencti-bearer-token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:

        mock_post.return_value = mock_resp

        fetch_resp = client.post(
            "/api/v1/intel/opencti/fetch",
            json={"first": 50},
            headers=HEADERS_A
        )
        assert fetch_resp.status_code == 200
        data = fetch_resp.json()
        assert data["status"] == "SUCCESS"
        assert data["indicators_ingested"] == 1

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer opencti-bearer-token"
        assert "GetIndicators" in kwargs["json"]["query"]


def test_opencti_payload_compatibility():
    payload = {
        "graphql_data": {
            "data": {
                "stixDomainObjects": [
                    {
                        "id": f"indicator--{uuid.uuid4()}",
                        "entity_type": "indicator",
                        "name": "OpenCTI Payload Test Domain",
                        "pattern": "[domain-name:value = 'bad-actor.net']",
                        "confidence": 88
                    }
                ]
            }
        }
    }
    resp = client.post("/api/v1/intel/opencti/query", json=payload, headers=HEADERS_A)
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"
    assert resp.json()["opencti_entities_ingested"] >= 1


# ============================================================================
# 5. TAXII 2.1 Server Tests
# ============================================================================

def test_taxii_discovery_and_collections():
    # 1. Discovery
    disc_resp = client.get("/api/v1/taxii2/")
    assert disc_resp.status_code == 200
    assert "application/taxii+json;version=2.1" in disc_resp.headers["Content-Type"]
    disc_data = disc_resp.json()
    assert disc_data["title"] == "CyGRC TAXII 2.1 Threat Intel Server"
    assert "/api/v1/taxii2/" in disc_data["api_roots"]

    # 2. Collections List
    colls_resp = client.get("/api/v1/taxii2/collections/")
    assert colls_resp.status_code == 200
    assert "application/taxii+json;version=2.1" in colls_resp.headers["Content-Type"]
    colls = colls_resp.json()["collections"]
    assert any(c["id"] == "default-threat-intel" for c in colls)

    # 3. Collection Detail
    detail_resp = client.get("/api/v1/taxii2/collections/default-threat-intel/")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == "default-threat-intel"
    assert detail_resp.json()["can_read"] is True

    # 4. Unknown Collection returns TAXII error 404
    err_resp = client.get("/api/v1/taxii2/collections/non-existent-collection/")
    assert err_resp.status_code == 404
    assert "application/taxii+json;version=2.1" in err_resp.headers["Content-Type"]
    assert "Collection Not Found" in err_resp.json()["title"]


def test_taxii_bundle_ingest_and_status_tracking():
    test_obj_id = f"indicator--{uuid.uuid4()}"
    bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "id": test_obj_id,
                "type": "indicator",
                "name": "TAXII Ingested Phishing Host",
                "pattern": "[domain-name:value = 'login-bank-phish.net']",
                "confidence": 85,
            }
        ]
    }

    # Ingest bundle
    ingest_resp = client.post(
        "/api/v1/taxii2/collections/default-threat-intel/objects/",
        json=bundle,
        headers=HEADERS_A
    )
    assert ingest_resp.status_code == 202
    res_data = ingest_resp.json()
    assert res_data["status"] == "SUCCESS"
    assert res_data["objects_ingested"] == 1
    status_id = res_data["status_id"]

    # Verify status record
    status_resp = client.get(f"/api/v1/taxii2/status/{status_id}/")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "complete"
    assert status_resp.json()["success_count"] == 1

    # Retrieve object from collection with filtering
    get_objs_resp = client.get(
        "/api/v1/taxii2/collections/default-threat-intel/objects/?match[type]=indicator",
        headers=HEADERS_A
    )
    assert get_objs_resp.status_code == 200
    assert "application/stix+json;version=2.1" in get_objs_resp.headers["Content-Type"]
    bundle_objs = get_objs_resp.json()["objects"]
    assert any(o.get("id") == test_obj_id for o in bundle_objs)

    # Single object retrieval
    single_resp = client.get(
        f"/api/v1/taxii2/collections/default-threat-intel/objects/{test_obj_id}/",
        headers=HEADERS_A
    )
    assert single_resp.status_code == 200
    assert single_resp.json()["objects"][0]["id"] == test_obj_id


# ============================================================================
# 6. SOC Alert IOC Enrichment Tests
# ============================================================================

def test_alert_ioc_extraction_and_active_matching():
    # 1. Store active high-confidence indicator in Tenant A
    ip_uuid = str(uuid.uuid4())
    stix_id = f"indicator--{ip_uuid}"
    stix_payload = {
        "stix_id": stix_id,
        "type": "indicator",
        "name": "Active Ransomware C2 IP",
        "pattern": "[ipv4-addr:value = '198.51.100.77']",
        "confidence": 92,
        "revoked": False,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
        "source": "MISP",
    }
    stix_resp = client.post("/api/v1/stix/objects", json=stix_payload, headers=HEADERS_A)
    assert stix_resp.status_code == 201

    # 2. Ingest SOC alert containing the observable IP in description and payload
    alert_payload = {
        "title": "Suspicious outbound TLS handshake",
        "source": "Wazuh",
        "severity": "MEDIUM",
        "description": "Connection detected to destination 198.51.100.77 on port 443",
        "raw_payload": {
            "dst_ip": "198.51.100.77",
            "process_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "url": "https://malicious-domain.biz/payload.exe",
        }
    }
    alert_resp = client.post("/api/v1/alerts", json=alert_payload, headers=HEADERS_A)
    assert alert_resp.status_code == 201
    alert_id = alert_resp.json()["alert_id"]

    # 3. Enrich alert
    enrich_resp = client.post(f"/api/v1/alerts/{alert_id}/enrich", headers=HEADERS_A)
    assert enrich_resp.status_code == 200
    enrich_data = enrich_resp.json()["enrichment"]
    assert enrich_data["enriched"] is True
    assert enrich_data["matched_indicators_count"] >= 1
    assert any(ind["matched_observable"] == "198.51.100.77" for ind in enrich_data["indicators"])
    assert enrich_data["threat_confidence"] >= 90

    # 4. Confirm severity escalated to CRITICAL due to active match with confidence >= 80
    get_alert = client.get(f"/api/v1/alerts/{alert_id}", headers=HEADERS_A)
    assert get_alert.status_code == 200
    assert get_alert.json()["severity"] == "CRITICAL"


def test_alert_enrichment_excludes_revoked_and_expired_indicators():
    # 1. Store revoked indicator
    revoked_id = f"indicator--{uuid.uuid4()}"
    client.post("/api/v1/stix/objects", json={
        "stix_id": revoked_id,
        "type": "indicator",
        "name": "Revoked Cleaned IP",
        "pattern": "[ipv4-addr:value = '198.51.100.88']",
        "confidence": 95,
        "revoked": True,
    }, headers=HEADERS_A)

    # 2. Store expired indicator (valid_until in the past)
    expired_id = f"indicator--{uuid.uuid4()}"
    client.post("/api/v1/stix/objects", json={
        "stix_id": expired_id,
        "type": "indicator",
        "name": "Expired Historical IP",
        "pattern": "[ipv4-addr:value = '198.51.100.89']",
        "confidence": 95,
        "revoked": False,
        "valid_until": (datetime.utcnow() - timedelta(days=5)).isoformat() + "Z",
    }, headers=HEADERS_A)

    # 3. Create alert containing both IPs
    alert_resp = client.post("/api/v1/alerts", json={
        "title": "Traffic with revoked and expired addresses",
        "source": "Firewall",
        "severity": "LOW",
        "description": "Observed 198.51.100.88 and 198.51.100.89",
    }, headers=HEADERS_A)
    alert_id = alert_resp.json()["alert_id"]

    # 4. Enrich alert
    enrich_resp = client.post(f"/api/v1/alerts/{alert_id}/enrich", headers=HEADERS_A)
    assert enrich_resp.status_code == 200
    enrich_data = enrich_resp.json()["enrichment"]

    # Neither revoked nor expired indicator must be matched
    matched_ids = [ind["stix_id"] for ind in enrich_data["indicators"]]
    assert revoked_id not in matched_ids
    assert expired_id not in matched_ids
    assert enrich_data["matched_indicators_count"] == 0

    # Severity must NOT have been escalated
    get_alert = client.get(f"/api/v1/alerts/{alert_id}", headers=HEADERS_A)
    assert get_alert.json()["severity"] == "LOW"


def test_batch_alert_enrichment_and_tenant_isolation():
    # Indicator stored in Tenant B ONLY
    tenant_b_ip = "203.0.113.199"
    client.post("/api/v1/stix/objects", json={
        "type": "indicator",
        "name": "Tenant B Private Threat",
        "pattern": f"[ipv4-addr:value = '{tenant_b_ip}']",
        "confidence": 90,
    }, headers=HEADERS_B)

    # Create alerts in Tenant A referencing Tenant B's IP
    a1 = client.post("/api/v1/alerts", json={
        "title": "Tenant A Alert 1",
        "source": "Wazuh",
        "description": f"Connecting to {tenant_b_ip}",
    }, headers=HEADERS_A).json()["alert_id"]

    a2 = client.post("/api/v1/alerts", json={
        "title": "Tenant A Alert 2",
        "source": "Wazuh",
        "description": "Benign local broadcast",
    }, headers=HEADERS_A).json()["alert_id"]

    # Run batch enrichment for Tenant A
    batch_resp = client.post(
        "/api/v1/alerts/batch/enrich",
        json={"alert_ids": [a1, a2]},
        headers=HEADERS_A
    )
    assert batch_resp.status_code == 200
    data = batch_resp.json()
    assert data["total_requested"] == 2
    assert data["successful_count"] == 2

    # Tenant A must NOT match Tenant B's indicator (tenant isolation)
    for res in data["results"]:
        assert res["enrichment"]["matched_indicators_count"] == 0
