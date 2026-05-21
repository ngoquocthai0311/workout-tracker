from backend.app.services.dashboard_service import get_dashboard_service
from backend.app.services.dashboard_service import DashboardService
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.schemas.response_schemas import (
    DayReportResponse,
    WeekReportResponse,
    YearReportResponse,
)

router = APIRouter(tags=["dashboards"], prefix="/dashboards")

# NOTE: Do dashboard repository in the future


@router.get(
    "/weights/total/day",
    response_model=DayReportResponse,
)
def get_total_weights_by_day(
    target_date: str = datetime.today().strftime("%Y-%m-%d"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    try:
        return dashboard_service.get_total_weight_by_day(target_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "weights/total/week",
    response_model=WeekReportResponse,
)
def get_total_weights_by_week(
    start_date: str = datetime.today().strftime("%Y-%m-%d"),
    end_date: str = datetime.today().strftime("%Y-%m-%d"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    try:
        return dashboard_service.get_total_weight_by_week(start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "/weights/total/year",
    response_model=YearReportResponse,
)
def get_total_weights_by_year(
    year: int = datetime.now().year,
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    try:
        return dashboard_service.get_total_weight_by_year(year)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )


@router.get(
    "/glance",
)
def get_a_glance(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    try:
        return dashboard_service.get_a_glance()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {e.__class__.__name__}",
        )
