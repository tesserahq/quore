from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.system_setup import SystemSetup
from app.schemas.system import (
    SystemSetupResponse,
    ValidationStatus,
    SystemSettingsGrouped,
    AppGroup,
    LLMGroup,
    DataGroup,
    TelemetryGroup,
    RedisGroup,
    ExternalServicesGroup,
)
from app.schemas.common import DataResponse
from app.utils.auth import get_current_user
from app.config import get_settings

router = APIRouter(
    prefix="/system",
    tags=["system"],
    responses={404: {"description": "Not found"}},
)


@router.post("/setup", response_model=SystemSetupResponse)
def setup_system(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Perform system setup and validation.
    This endpoint runs all system-level validations and setup procedures.
    """
    validation_steps = SystemSetup.validate()
    success = all(step.status == ValidationStatus.OK for step in validation_steps)

    return SystemSetupResponse(
        success=success,
        message=(
            "System setup completed successfully" if success else "System setup failed"
        ),
        details=validation_steps,
    )


@router.get("/settings", response_model=DataResponse[SystemSettingsGrouped])
def get_system_settings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return grouped, non-sensitive system configuration settings for troubleshooting."""
    s = get_settings()

    app_group = AppGroup(
        name=s.app_name,
        environment=s.environment,
        log_level=s.log_level,
        disable_auth=s.disable_auth,
        port=s.port,
    )

    llm_group = LLMGroup(
        default_provider=s.default_llm_provider,
        default_llm=s.default_llm,
        default_embed_model=s.default_embed_model,
        default_embed_dim=s.default_embed_dim,
        default_system_prompt=s.default_system_prompt,
        ollama_base_url=s.ollama_base_url,
    )

    # Extract safe database info only (no credentials)
    database_host = None
    database_driver = None
    try:
        url_obj = s.database_url_obj
        database_host = url_obj.host
        database_driver = url_obj.get_backend_name()
    except Exception:
        pass

    data_group = DataGroup(
        default_data_dir=s.default_data_dir,
        database_host=database_host,
        database_driver=database_driver,
        is_production=s.is_production,
        is_test=s.is_test,
    )

    telemetry_group = TelemetryGroup(
        otel_enabled=s.otel_enabled,
        otel_exporter_otlp_endpoint=s.otel_exporter_otlp_endpoint,
        otel_service_name=s.otel_service_name,
    )

    redis_group = RedisGroup(
        host=s.redis_host,
        port=s.redis_port,
        namespace=s.redis_namespace,
    )

    services_group = ExternalServicesGroup(
        vaulta_api_url=s.vaulta_api_url,
        identies_host=s.identies_host,
    )

    grouped = SystemSettingsGrouped(
        app=app_group,
        llm=llm_group,
        data=data_group,
        telemetry=telemetry_group,
        redis=redis_group,
        services=services_group,
    )

    return DataResponse(data=grouped)
