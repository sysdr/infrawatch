import io
import json
import csv
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.analytics import Report, MetricSnapshot
from app.schemas.analytics import ReportCreate, ReportOut

class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report(self, data: ReportCreate) -> ReportOut:
        report = Report(**data.model_dump())
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return ReportOut.model_validate(report)

    async def list_reports(self) -> list[ReportOut]:
        result = await self.db.execute(select(Report).order_by(Report.created_at.desc()))
        return [ReportOut.model_validate(r) for r in result.scalars().all()]

    async def generate_csv(self, report_id: int) -> bytes:
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        report = result.scalar_one_or_none()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        metrics = report.config.get("metrics", ["cpu_utilization", "memory_usage"])
        rows_result = await self.db.execute(
            select(MetricSnapshot)
            .where(MetricSnapshot.metric_name.in_(metrics))
            .order_by(MetricSnapshot.recorded_at.desc())
            .limit(500)
        )
        rows = rows_result.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["metric_name", "value", "unit", "recorded_at"])
        for row in rows:
            writer.writerow([row.metric_name, row.value, row.unit, row.recorded_at.isoformat()])

        report.last_run_at = datetime.now(timezone.utc)
        await self.db.commit()
        return output.getvalue().encode()

    async def generate_pdf(self, report_id: int) -> bytes:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm

        result = await self.db.execute(select(Report).where(Report.id == report_id))
        report = result.scalar_one_or_none()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        metrics = report.config.get("metrics", ["cpu_utilization", "memory_usage"])
        rows_result = await self.db.execute(
            select(MetricSnapshot)
            .where(MetricSnapshot.metric_name.in_(metrics))
            .order_by(MetricSnapshot.recorded_at.desc())
            .limit(30)
        )
        rows = rows_result.scalars().all()

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        w, h = A4
        c.setFont("Helvetica-Bold", 18)
        c.setFillColorRGB(0.24, 0.55, 0.34)
        c.drawString(2 * cm, h - 3 * cm, f"Analytics Report: {report.name}")
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(2 * cm, h - 3.8 * cm, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        c.drawString(2 * cm, h - 4.4 * cm, f"Metrics: {', '.join(metrics)}")

        y = h - 6 * cm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(2 * cm, y, "Metric Name"); c.drawString(8 * cm, y, "Value"); c.drawString(12 * cm, y, "Recorded At")
        y -= 0.6 * cm
        c.line(2 * cm, y, w - 2 * cm, y)
        y -= 0.4 * cm
        c.setFont("Helvetica", 9)
        for row in rows[:25]:
            if y < 3 * cm:
                c.showPage()
                y = h - 3 * cm
            c.drawString(2 * cm, y, row.metric_name)
            c.drawString(8 * cm, y, f"{row.value:.2f}")
            c.drawString(12 * cm, y, row.recorded_at.strftime("%Y-%m-%d %H:%M"))
            y -= 0.55 * cm

        c.save()
        report.last_run_at = datetime.now(timezone.utc)
        await self.db.commit()
        return buf.getvalue()
