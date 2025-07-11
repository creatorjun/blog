# app/services/email_service.py (원본 코드로 완벽히 복구)

import smtplib
import httpx
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from app.core import config # config 경로는 core 폴더를 사용합니다.

def _format_post_as_html(post_data: dict) -> str:
    """블로그 포스트 데이터를 이메일 본문용 HTML로 변환합니다."""

    title = post_data.get("blog_title", "제목 없음")
    introduction = post_data.get("introduction", "")
    main_body = post_data.get("main_body", "")
    conclusion = post_data.get("conclusion", "")
    key_takeaways = post_data.get("key_takeaways", [])

    if post_data.get("featured_image_url"):
        main_body = main_body.replace("[IMAGE]", '<img src="cid:featured_image" style="max-width:100%; height:auto;"><br>')
    else:
        main_body = main_body.replace("[IMAGE]", "")

    main_body_html = main_body.replace("\n", "<br>")
    takeaways_html = "<ul>" + "".join(f"<li>{item}</li>" for item in key_takeaways) + "</ul>"

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #f1f1f1; padding-bottom: 5px; }}
            ul {{ background-color: #f9f9f9; border-left: 5px solid #3498db; padding: 15px; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p><i>{introduction}</i></p>
        <hr>
        <h2>본문</h2>
        <p>{main_body_html}</p>
        <h2>핵심 요약</h2>
        {takeaways_html}
        <h2>결론</h2>
        <p>{conclusion}</p>
    </body>
    </html>
    """
    return html

def send_post_via_email(post_data: dict) -> dict:
    """
    생성된 포스트 데이터를 이메일로 발송합니다.
    """
    sender_email = config.EMAIL_SENDER_ADDRESS
    sender_password = config.EMAIL_SENDER_PASSWORD
    recipient_email = config.EMAIL_RECIPIENT_ADDRESS

    if not all([sender_email, sender_password, recipient_email]):
        return {"success": False, "detail": ".env 파일에 이메일 관련 설정을 모두 입력해야 합니다."}

    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"AI 블로그 포스트 생성 완료: {post_data.get('blog_title', '')}"

    try:
        html_body = _format_post_as_html(post_data)
        msg.attach(MIMEText(html_body, 'html'))

        image_url = post_data.get("featured_image_url")
        if image_url:
            with httpx.Client() as client:
                response = client.get(image_url, timeout=30.0)
                response.raise_for_status()
                image = MIMEImage(response.content)
                image.add_header('Content-ID', '<featured_image>')
                msg.attach(image)

        # --- 이 부분을 원래의 성공했던 방식으로 복구했습니다 ---
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # TLS 암호화 시작
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("이메일이 성공적으로 발송되었습니다.")

        return {"success": True, "message": f"블로그 포스트 초안이 {recipient_email} 주소로 성공적으로 발송되었습니다."}

    except Exception as e:
        error_message = f"이메일 발송 중 에러 발생: {e}"
        print(error_message)
        return {"success": False, "detail": error_message}