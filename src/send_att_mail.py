import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import datetime

def send_alert_msg(beautipth,h_name,name_accman,email_id,number,date,tdayfold):
    date_f = datetime.date.today()
    # sender = "revseed@revnomix.com"
    # emailto = "vibhor.khetan@revnomix.com"
    fileToSend = beautipth + '/'+ tdayfold +'/' + name_accman
    filename='iSell_{}_{}.xlsx'.format(h_name,date)
    # fileToSend = "hi.csv"
    username = 'revseed@revnomix.com'
    password = 'Revenue@123'
    recipients = email_id
    alias = 'Revnomix Revenue Management Services <revnomix.RMS@revnomix.com>'


    msg = MIMEMultipart()
    msg['From'] = alias
    msg['To'] = ' ,'.join([str(elem) for elem in recipients.split(',')[:int(-number)]])
    msg['Cc'] = ' ,'.join([str(elem) for elem in recipients.split(',')[int(-number):]])
    msg["Subject"] = 'iSell ' +  ' | '  +  h_name  +  ' | '   + date
    mail_content = '''Dear Team,

    Please find the enclosed iSell Report for your kind reference. 

    Important:- Inventories/Stop Sale need to be re-looked for Sale Online. As Best Practices, we suggest updating Real Inventory
    in the channel manager and for Sold Out Dates Inventory should be marked as Zero instead of Stop Sale.
    
    Positioning:- As best practices, we suggest responding to all the reviews especially negative reviews on priorities.

    Pricing:- As a best practice, we request the hotel General Manager to review the pricing in the iSell Report and share their feedback
    in order to take control of Pricing instantly.  

    Please Note:- Rate Shopping done for 180 days (Mon & Fri), and 30 Days (Tue, Wed, Thu)  Source: (booking.com/expedia.com).

    
    In case of any queries, please reach out to us.
    '''


    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)
    msg.attach(MIMEText(mail_content))

    fp = open(fileToSend+'/'+filename, "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(username,password)
    server.sendmail(msg['From'],  recipients.split(','), msg.as_string())
    server.quit()
# if __name__ =='__main__':

    # send_alert_msg(email_id,sub)