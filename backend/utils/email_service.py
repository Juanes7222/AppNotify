import os
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, body: str):
    """Send email via Gmail SMTP"""
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    
    if not smtp_user or not smtp_password:
        logger.warning("SMTP credentials not configured, skipping email send")
        return False
    
    message = MIMEMultipart()
    message['From'] = smtp_user
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))
    
    try:
        await aiosmtplib.send(
            message,
            timeout=30,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def format_date_spanish(event_date: datetime, user_timezone: str = "America/Bogota") -> str:
    """Format date in Spanish, converting from UTC to user's timezone"""
    # Convert UTC to user's timezone
    if event_date.tzinfo is None:
        from datetime import timezone as tz
        event_date = event_date.replace(tzinfo=tz.utc)
    
    local_date = event_date.astimezone(ZoneInfo(user_timezone))
    
    months_es = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
        'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
        'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    formatted_date_en = local_date.strftime("%d de %B de %Y")
    formatted_date = formatted_date_en
    for en, es in months_es.items():
        formatted_date = formatted_date.replace(en, es)
    return formatted_date


def format_time_12h(event_date: datetime, user_timezone: str = "America/Bogota") -> str:
    """Format time in 12-hour format, converting from UTC to user's timezone"""
    # Convert UTC to user's timezone
    if event_date.tzinfo is None:
        from datetime import timezone as tz
        event_date = event_date.replace(tzinfo=tz.utc)
    
    local_date = event_date.astimezone(ZoneInfo(user_timezone))
    
    hour = local_date.hour
    minute = local_date.minute
    am_pm = 'AM' if hour < 12 else 'PM'
    hour_12 = hour if hour <= 12 else hour - 12
    hour_12 = 12 if hour_12 == 0 else hour_12
    return f"{hour_12}:{minute:02d} {am_pm}"


def generate_reminder_email(event: dict, contact: dict, user_timezone: str = "America/Bogota") -> tuple[str, str]:
    """Generate reminder email HTML"""
    event_date = event['event_date']
    if isinstance(event_date, str):
        event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
    
    formatted_date = format_date_spanish(event_date, user_timezone)
    formatted_time = format_time_12h(event_date, user_timezone)
    
    subject = f"Recordatorio: {event['title']}"
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #1f2937; background: #f3f4f6; }}
            .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px 30px; text-align: center; }}
            .header-icon {{ width: 64px; height: 64px; margin: 0 auto 20px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; }}
            .header h1 {{ color: white; font-size: 24px; font-weight: 600; margin: 0; }}
            .content {{ padding: 40px 30px; }}
            .greeting {{ color: #374151; font-size: 16px; margin-bottom: 20px; }}
            .event-card {{ background: linear-gradient(to bottom, #f9fafb 0%, #ffffff 100%); border: 2px solid #e5e7eb; border-radius: 12px; padding: 25px; margin: 25px 0; }}
            .event-title {{ color: #1f2937; font-size: 22px; font-weight: 600; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #e5e7eb; }}
            .event-detail {{ display: flex; align-items: center; margin: 15px 0; padding: 12px; background: white; border-radius: 8px; }}
            .detail-icon {{ width: 48px; height: 48px; background: #f3f4f6; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0; font-size: 24px; line-height: 1; }}
            .detail-content {{ flex: 1; }}
            .detail-label {{ color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 600; }}
            .detail-value {{ color: #1f2937; font-size: 15px; font-weight: 500; }}
            .description {{ color: #4b5563; font-size: 14px; line-height: 1.6; padding: 15px; background: #f9fafb; border-radius: 8px; border-left: 3px solid #6366f1; }}
            .footer {{ background: #f9fafb; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e7eb; }}
            .footer p {{ color: #6b7280; font-size: 12px; margin: 0; }}
            .cta-box {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 20px; margin: 25px 0; text-align: center; }}
            .cta-box p {{ color: #1e40af; font-size: 14px; font-weight: 500; margin: 0; }}
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #f3f4f6; padding: 20px;">
            <tr>
                <td align="center">
                    <div class="container">
                        <div class="header">
                            <div class="header-icon" style="font-size: 40px; line-height: 1;">🔔</div>
                            <h1>Recordatorio de Evento</h1>
                        </div>
                        <div class="content">
                            <p class="greeting">Hola <strong>{contact['name']}</strong>,</p>
                            <p style="color: #4b5563; font-size: 14px; margin-bottom: 20px;">Te recordamos que tienes el siguiente evento programado:</p>
                            
                            <div class="event-card">
                                <div class="event-title">{event['title']}</div>
                                
                                <div class="event-detail">
                                    <div class="detail-icon">📅</div>
                                    <div class="detail-content">
                                        <div class="detail-label">FECHA</div>
                                        <div class="detail-value">{formatted_date}</div>
                                    </div>
                                </div>
                                
                                <div class="event-detail">
                                    <div class="detail-icon">🕐</div>
                                    <div class="detail-content">
                                        <div class="detail-label">HORA</div>
                                        <div class="detail-value">{formatted_time}</div>
                                    </div>
                                </div>
                                
                                {f'''<div class="event-detail">
                                    <div class="detail-icon">📍</div>
                                    <div class="detail-content">
                                        <div class="detail-label">UBICACIÓN</div>
                                        <div class="detail-value">{event['location']}</div>
                                    </div>
                                </div>''' if event.get('location') else ''}
                                
                                {f'<div style="margin-top: 20px;"><div class="detail-label" style="margin-bottom: 8px;">Descripción</div><div class="description">{event["description"]}</div></div>' if event.get('description') else ''}
                            </div>
                            
                            <div class="cta-box">
                                <p>Marca este evento en tu calendario para no olvidarlo</p>
                            </div>
                        </div>
                        <div class="footer">
                            <p>Este es un recordatorio automático generado por <strong>RemindSender</strong></p>
                            <p style="margin-top: 8px;">Sistema de gestión de eventos y notificaciones</p>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return subject, body


def generate_test_reminder_email(event: dict, contact: dict, user_timezone: str = "America/Bogota") -> tuple[str, str]:
    """Generate test reminder email HTML"""
    event_date = event['event_date']
    if isinstance(event_date, str):
        event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
    
    formatted_date = format_date_spanish(event_date, user_timezone)
    formatted_time = format_time_12h(event_date, user_timezone)
    
    subject = f"[PRUEBA] Recordatorio: {event['title']}"
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #1f2937; background: #f3f4f6; }}
            .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-top: 4px solid #f59e0b; }}
            .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 40px 30px; text-align: center; }}
            .header-badge {{ display: inline-block; background: rgba(255,255,255,0.2); color: white; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px; }}
            .header h1 {{ color: white; font-size: 24px; font-weight: 600; margin: 0; }}
            .content {{ padding: 40px 30px; }}
            .event-card {{ background: linear-gradient(to bottom, #fef3c7 0%, #fef9e3 100%); border: 2px solid #fbbf24; border-radius: 12px; padding: 25px; margin: 25px 0; }}
            .event-title {{ color: #78350f; font-size: 22px; font-weight: 600; margin-bottom: 20px; }}
            .event-detail {{ display: flex; align-items: center; margin: 12px 0; padding: 12px; background: white; border-radius: 8px; }}
            .detail-icon {{ width: 36px; height: 36px; background: #fef3c7; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px; }}
            .detail-content {{ color: #1f2937; font-size: 14px; }}
            .detail-content strong {{ display: block; color: #92400e; font-size: 12px; margin-bottom: 2px; }}
            .warning-box {{ background: #fffbeb; border: 2px dashed #f59e0b; border-radius: 8px; padding: 20px; margin: 25px 0; text-align: center; }}
            .warning-box p {{ color: #92400e; font-size: 13px; font-weight: 500; margin: 0; }}
            .footer {{ background: #f9fafb; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e7eb; }}
            .footer p {{ color: #6b7280; font-size: 12px; margin: 0; }}
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #f3f4f6; padding: 20px;">
            <tr>
                <td align="center">
                    <div class="container">
                        <div class="header">
                            <div class="header-badge">Modo Prueba</div>
                            <h1>Recordatorio de Evento</h1>
                        </div>
                        <div class="content">
                            <p style="color: #374151; font-size: 16px; margin-bottom: 20px;">Hola <strong>{contact['name']}</strong>,</p>
                            <p style="color: #4b5563; font-size: 14px; margin-bottom: 20px;">Este es un recordatorio de prueba para el siguiente evento:</p>
                            
                            <div class="event-card">
                                <div class="event-title">{event['title']}</div>
                                
                                <div class="event-detail">
                                    <div class="detail-icon" style="font-size: 20px; color: #f59e0b;">📅</div>
                                    <div class="detail-content">
                                        <strong>FECHA</strong>
                                        {formatted_date}
                                    </div>
                                </div>
                                
                                <div class="event-detail">
                                    <div class="detail-icon" style="font-size: 20px; color: #f59e0b;">🕐</div>
                                    <div class="detail-content">
                                        <strong>HORA</strong>
                                        {formatted_time}
                                    </div>
                                </div>
                                
                                {f'''<div class="event-detail">
                                    <div class="detail-icon" style="font-size: 20px; color: #f59e0b;">📍</div>
                                    <div class="detail-content">
                                        <strong>UBICACIÓN</strong>
                                        {event['location']}
                                    </div>
                                </div>''' if event.get('location') else ''}
                                
                                {f'<div style="margin-top: 15px; padding: 12px; background: white; border-radius: 8px;"><strong style="color: #92400e; font-size: 12px;">DESCRIPCIÓN</strong><p style="color: #4b5563; font-size: 14px; margin: 8px 0 0 0;">{event["description"]}</p></div>' if event.get('description') else ''}
                            </div>
                            
                            <div class="warning-box">
                                <p>Este es un correo de prueba enviado manualmente.</p>
                                <p style="margin-top: 5px; font-size: 12px; color: #b45309;">Los recordatorios reales se enviarán automáticamente según la configuración del evento.</p>
                            </div>
                        </div>
                        <div class="footer">
                            <p>Correo de prueba generado por <strong>RemindSender</strong></p>
                            <p style="margin-top: 8px;">Sistema de gestión de eventos y notificaciones</p>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return subject, body


def generate_test_smtp_email(user: dict) -> tuple[str, str]:
    """Generate SMTP test email HTML"""
    from datetime import timezone
    
    subject = "Correo de Prueba - RemindSender"
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #1f2937; background: #f3f4f6; }}
            .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; }}
            .header-icon {{ width: 64px; height: 64px; margin: 0 auto 20px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; }}
            .header h1 {{ color: white; font-size: 24px; font-weight: 600; margin: 0; }}
            .header p {{ color: rgba(255,255,255,0.9); font-size: 14px; margin-top: 8px; }}
            .content {{ padding: 40px 30px; }}
            .success-box {{ background: #f0fdf4; border: 2px solid #10b981; border-radius: 8px; padding: 20px; margin-bottom: 30px; }}
            .success-box h2 {{ color: #047857; font-size: 18px; margin-bottom: 10px; }}
            .success-box p {{ color: #065f46; font-size: 14px; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin: 25px 0; }}
            .info-table td {{ padding: 12px 0; border-bottom: 1px solid #e5e7eb; font-size: 14px; }}
            .info-table td:first-child {{ color: #6b7280; font-weight: 500; width: 120px; }}
            .info-table td:last-child {{ color: #1f2937; }}
            .info-table tr:last-child td {{ border-bottom: none; }}
            .footer {{ background: #f9fafb; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e7eb; }}
            .footer p {{ color: #6b7280; font-size: 12px; margin: 0; }}
            .badge {{ display: inline-block; background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; }}
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #f3f4f6; padding: 20px;">
            <tr>
                <td align="center">
                    <div class="container">
                        <div class="header">
                            <div class="header-icon">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                                    <path d="M9 11l3 3L22 4"></path>
                                    <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path>
                                </svg>
                            </div>
                            <h1>Sistema de Correos Funcionando</h1>
                            <p>Verificación exitosa de configuración SMTP</p>
                        </div>
                        <div class="content">
                            <div class="success-box">
                                <h2>Prueba Exitosa</h2>
                                <p>Si estás leyendo este correo, significa que la configuración SMTP está funcionando correctamente y el sistema puede enviar notificaciones automáticas.</p>
                            </div>
                            <p style="color: #374151; font-size: 14px; margin-bottom: 15px;"><strong>Detalles de la Prueba:</strong></p>
                            <table class="info-table">
                                <tr>
                                    <td>Usuario</td>
                                    <td><strong>{user.get('display_name', 'Usuario de prueba')}</strong></td>
                                </tr>
                                <tr>
                                    <td>Correo</td>
                                    <td>{user['email']}</td>
                                </tr>
                                <tr>
                                    <td>Fecha y Hora</td>
                                    <td>{datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")}</td>
                                </tr>
                                <tr>
                                    <td>Estado</td>
                                    <td><span class="badge">Operativo</span></td>
                                </tr>
                            </table>
                        </div>
                        <div class="footer">
                            <p>Este es un correo de prueba enviado desde <strong>RemindSender</strong></p>
                            <p style="margin-top: 8px;">Sistema de gestión de eventos y recordatorios automáticos</p>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return subject, body
