import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = func.FunctionApp()

@app.function_name(name="ServiceBusQueueTrigger1")
@app.service_bus_queue_trigger(arg_name="msg", queue_name="notificationqueue",
                               connection="nanomigrationservicebus_SERVICEBUS") 
def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', [notification_id])

    # Open DB connection
    conn = psycopg2.connect("host=nano-migration-dbserver.postgres.database.azure.com dbname=techconfdb user=valentin password=xORD4HnTDdml")
    cur = conn.cursor()

    try:
        # Get notification message and subject from database using the notification_id
        cur.execute("SELECT subject, message FROM notification WHERE id=(%s);", ([notification_id]))
        subject, message = cur.fetchone()

        # Get attendees email and name
        cur.execute("SELECT first_name, email FROM attendee;")
        attendees = cur.fetchall()

        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees: 
            logging.info("Send message with subject: " + subject +". Message: " + message + " to " + attendee[0] + " with email " + attendee[1])
            email = Mail(
                from_email='valentinbumeder@gmail.com',
                to_emails=attendee[1],
                subject=subject,
                html_content=message)
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(email)
                logging.info(response.status_code)
                logging.info(response.body)
                logging.info(response.headers)
            except Exception as e:
                logging.error(e.message)

        # Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        updated_status = "Notified " + str(len(attendees)) + " attendees"
        updated_time = str(datetime.now)
        cur.execute("UPDATE notification SET status=(%s), completed_date=CURRENT_TIMESTAMP WHERE id=(%s)", (updated_status, notification_id))
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error.with_traceback)
    finally:
        # Close DB connection
        cur.close()
        conn.close()