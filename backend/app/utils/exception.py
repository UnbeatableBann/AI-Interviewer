from fastapi import Request, status
from fastapi.responses import JSONResponse

# Custom exception for email sending errors
class EmailSendException(Exception):
    def __init__(self, email: str, message: str = "Failed to send email"):
        self.email = email
        self.message = message
        super().__init__(self.message)

# Custom ExJSONResponseler to return JSON on EmailSendException
async def email_send_exception_handler(request: Request, exc: EmailSendException):  # noqa: F821
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": f"Error sending email to {exc.email}: {exc.message}"}
    )