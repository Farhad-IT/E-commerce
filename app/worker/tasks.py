from app.celery_app import celery_app
from app.core.log import logger
from app.worker.email_service import send_order_email, send_welcome_email


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def send_order_confirmation_email(self, email: str, order_id: int):
    try:
        logger.info(f"Sending order confirmation email {email} for order {order_id}")

        result = send_order_email(email=email, order_id=order_id)

        logger.info(f"Order confirmation email {email} sent")
        return result
    except RuntimeError as e:
        logger.error(f"Order confirmation email {email} failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def send_welcome_confirmation_email(self, email: str, name: str, user_id: int):
    try:
        logger.info(f"User {name} (#{user_id}) login at.")

        result = send_welcome_email(email=email, name=name)

        logger.info(f"Welcome confirmation email {email} sent")
        return result
    except RuntimeError as e:
        logger.error(f"Welcome confirmation email {email} failed: {e}")
        raise self.retry(exc=e)
