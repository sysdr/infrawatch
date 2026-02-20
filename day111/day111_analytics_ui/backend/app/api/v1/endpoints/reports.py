from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.report_service import ReportService
from app.schemas.analytics import ReportCreate, ReportOut

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=ReportOut)
async def create_report(payload: ReportCreate, db: AsyncSession = Depends(get_db)):
    return await ReportService(db).create_report(payload)

@router.get("/", response_model=list[ReportOut])
async def list_reports(db: AsyncSession = Depends(get_db)):
    return await ReportService(db).list_reports()

@router.get("/{report_id}/export/csv")
async def export_csv(report_id: int, db: AsyncSession = Depends(get_db)):
    content = await ReportService(db).generate_csv(report_id)
    return Response(content=content, media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"})

@router.get("/{report_id}/export/pdf")
async def export_pdf(report_id: int, db: AsyncSession = Depends(get_db)):
    content = await ReportService(db).generate_pdf(report_id)
    return Response(content=content, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"})
