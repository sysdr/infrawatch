from sqlalchemy.orm import Session
from app.models.template import EmailDelivery, DeliveryStatus, ReportExecution
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import os
from datetime import datetime
import time

class EmailService:
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = "reports@example.com"
    
    def send_report(self, db: Session, execution_id: int, recipients: list) -> list:
        """Send report via email to recipients"""
        execution = db.query(ReportExecution).filter(
            ReportExecution.id == execution_id
        ).first()
        
        if not execution or not execution.output_file:
            raise ValueError("Execution not found or report not generated")
        
        delivery_results = []
        
        for recipient in recipients:
            delivery = EmailDelivery(
                execution_id=execution_id,
                recipient=recipient,
                status=DeliveryStatus.QUEUED
            )
            db.add(delivery)
            db.commit()
            db.refresh(delivery)
            
            try:
                # Send email with retry logic
                success = self._send_with_retry(execution, recipient)
                
                if success:
                    delivery.status = DeliveryStatus.SENT
                    delivery.sent_at = datetime.utcnow()
                else:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.error_message = "Failed to send after retries"
                
                db.commit()
                delivery_results.append(delivery)
                
            except Exception as e:
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = str(e)
                db.commit()
                delivery_results.append(delivery)
        
        return delivery_results
    
    def _send_with_retry(self, execution: ReportExecution, recipient: str,
                        max_retries: int = 3) -> bool:
        """Send email with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                return self._send_email(execution, recipient)
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(wait_time)
                else:
                    raise
        return False
    
    def _send_email(self, execution: ReportExecution, recipient: str) -> bool:
        """Send single email"""
        # For demo, just log instead of actually sending
        print(f"[EMAIL] Sending report to {recipient}")
        print(f"[EMAIL] Report file: {execution.output_file}")
        
        # In production, use SendGrid:
        # message = Mail(
        #     from_email=self.from_email,
        #     to_emails=recipient,
        #     subject=f"Report: {execution.scheduled_report.name}",
        #     html_content=self._generate_email_body(execution)
        # )
        # 
        # # Attach report file
        # with open(execution.output_file, 'rb') as f:
        #     data = f.read()
        # encoded = base64.b64encode(data).decode()
        # attachment = Attachment(
        #     FileContent(encoded),
        #     FileName(os.path.basename(execution.output_file)),
        #     FileType('application/pdf'),
        #     Disposition('attachment')
        # )
        # message.attachment = attachment
        # 
        # sg = SendGridAPIClient(self.api_key)
        # response = sg.send(message)
        # return response.status_code == 202
        
        return True  # Demo mode
    
    def _generate_email_body(self, execution: ReportExecution) -> str:
        """Generate email body HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Your Report is Ready</h2>
            <p>Please find your scheduled report attached.</p>
            <p><strong>Report:</strong> {execution.scheduled_report.name}</p>
            <p><strong>Generated:</strong> {execution.completed_at}</p>
            <p><strong>Execution Time:</strong> {execution.execution_time}s</p>
            <hr>
            <p style="font-size: 12px; color: #666;">
                To unsubscribe from these reports, click 
                <a href="#">here</a>
            </p>
        </body>
        </html>
        """
