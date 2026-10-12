import json
from pathlib import Path
from typing import Any, Dict, Optional

import grpc
import pyvelociraptor
from pyvelociraptor import api_pb2, api_pb2_grpc

from backend.core.config import settings


class VelociraptorServiceError(Exception):
    """Raised when a collection cannot be scheduled."""


def dispatch_collection(
    client_id: str,
    artifact_name: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> str:
    """Schedule a client artifact collection and return its real flow ID."""

    if not settings.VELOCIRAPTOR_ENABLED:
        raise VelociraptorServiceError("Velociraptor integration is disabled.")

    config_path = settings.VELOCIRAPTOR_CONFIG_PATH
    if not config_path or not Path(config_path).is_file():
        raise VelociraptorServiceError(
            "Velociraptor API configuration is missing."
        )

    try:
        config = pyvelociraptor.LoadConfigFile(config_path)

        credentials = grpc.ssl_channel_credentials(
            root_certificates=config["ca_certificate"].encode("utf-8"),
            private_key=config["client_private_key"].encode("utf-8"),
            certificate_chain=config["client_cert"].encode("utf-8"),
        )

        options = (
            ("grpc.ssl_target_name_override", "VelociraptorServer"),
        )

        # Pass user-supplied values through the VQL environment rather than
        # interpolating them into the query string.
        env_values = {
            "ClientId": client_id,
            "ArtifactName": artifact_name,
            "ParametersJson": json.dumps(parameters or {}),
        }

        query = """
        SELECT collect_client(
            client_id=ClientId,
            artifacts=ArtifactName,
            env=parse_json(data=ParametersJson)
        ).flow_id AS FlowId
        FROM scope()
        """

        request = api_pb2.VQLCollectorArgs(
            org_id=settings.VELOCIRAPTOR_ORG_ID or "",
            max_wait=1,
            max_row=100,
            timeout=10,
            Query=[
                api_pb2.VQLRequest(
                    Name="CyGRCCollectArtifact",
                    VQL=query,
                )
            ],
            env=[
                api_pb2.VQLEnv(key=key, value=value)
                for key, value in env_values.items()
            ],
        )

        with grpc.secure_channel(
            config["api_connection_string"],
            credentials,
            options,
        ) as channel:
            stub = api_pb2_grpc.APIStub(channel)

            for response in stub.Query(request, timeout=15):
                if not response.Response:
                    continue

                rows = json.loads(response.Response)
                for row in rows:
                    flow_id = row.get("FlowId")
                    if flow_id:
                        return str(flow_id)

        raise VelociraptorServiceError(
            "Velociraptor did not return a collection flow ID."
        )

    except VelociraptorServiceError:
        raise
    except grpc.RpcError as exc:
        raise VelociraptorServiceError(
            "Velociraptor API request failed."
        ) from exc
    except Exception as exc:
        raise VelociraptorServiceError(
            "Unable to schedule the Velociraptor collection."
        ) from exc


