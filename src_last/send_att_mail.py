import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import datetime
from datetime import datetime

def send_alert_msg(beautipth,h_name,name_accman,email_id,number,date1,tdayfold,text):
    #date_f = datetime.date.today()
    # sender = "revseed@revnomix.com"
    # emailto = "vibhor.khetan@revnomix.com"
    rdate = datetime.strptime(date1, "%d%b%Y").date()
    rdate1=rdate.strftime("%d %b %Y")
    fileToSend = beautipth + '/'+ tdayfold +'/' + name_accman
    filename='iSell_{}_{}.xlsx'.format(h_name,date1)
    # fileToSend = "hi.csv"
    username = 'revseed@revnomix.com'
    # password = '@#RevPune@2023~'
    password ='kskrylcjmrqjxghg'
    recipients = email_id
    alias = 'Revnomix Revenue Management Services <revnomix.RMS@revnomix.com>'
    #alias = 'revseed@revnomix.com>'








#=======================================================================================================
    # msg = MIMEMultipart()
    # msg['From'] = alias
    # msg['To'] = ' ,'.join([str(elem) for elem in recipients.split(',')[:int(-number)]])
    # msg['Cc'] = ' ,'.join([str(elem) for elem in recipients.split(',')[int(-number):]])
    # msg["Subject"] = 'iSell ' +  ' | '  +  h_name  +  ' | '   + date
    # mail_content = '''Dear Team,
    #
    # Please find the enclosed iSell Report for your kind reference.
    #
    # {}
    #
    #
    # NOTE: The Competitor Rates are extracted directly from the Online Travel Portals.
    # These rates are extracted at a particular time of the day.
    # Hence, there will be a possibility of having different rates when checked online at any other time of the day.
    #
    # In case of any queries, please reach out to us.
    #
    # '''.format(text)
    #
    #
    #
    #
    # ctype, encoding = mimetypes.guess_type(fileToSend)
    # if ctype is None or encoding is not None:
    #     ctype = "application/octet-stream"
    #
    # maintype, subtype = ctype.split("/", 1)
    # msg.attach(MIMEText(mail_content))
#====================================================================================================
    # ==================================A.S. May23======================================================================
    msg = MIMEMultipart()
    msg['From'] = alias
    msg['To'] = ' ,'.join([str(elem) for elem in recipients.split(',')[:int(-number)]])
    msg['Cc'] = ' ,'.join([str(elem) for elem in recipients.split(',')[int(-number):]])
    msg["Subject"] = 'iSell ' + ' | ' + h_name + ' | ' + rdate1

    # ---------------------------------------A.S. Jul23-----------------------------------
    text1 = '{}'.format(text[0])
    text2 = '{}'.format(text[1])
    text3 = '{}'.format(text[2])

    text_note = '''NOTE: The Competitor Rates are extracted directly from the Online Travel Portals.
                         These rates are extracted at a particular time of the day.
                         Hence, there will be a possibility of having different rates when checked online at any other time of the day.

                         In case of any queries, please reach out to us.'''
    # #-------------------------------------------------------------------------------
    # html = """\
    #       <html>
    #       <body>
    #      <span style="padding-left: 20px;
    #                   padding-right: 80px;
    #                   padding-top: 50px;
    #                   padding-bottom: 5px;
    #                   font-size: 20px;
    #                   text-align: left !important;">
    #      Dear Team,
    #      </span>
    #      <p style="padding-left: 80px;
    #                   padding-right: 80px;
    #                   padding-top: 5px;
    #                   padding-bottom: 5px;
    #                   font-size: 20px;
    #                   text-align: left !important;">
    #       Please find the enclosed iSell Report for your kind reference.
    #       </br>
    #       </br>
    #       {0}
    #      </p>
    #      <p style="padding-left: 80px;
    #                   padding-right: 80px;
    #                   padding-top: 5px;
    #                   padding-bottom: 30px;
    #                   font-size: 18px;
    #                   text-align: left !important;">
    #       {1}
    #       <br>
    #       </p>
    #
    #       </body>
    #       </html>
    #       """.format(text, text_note)
    #    #---------------------------------------------------------------------------
    html = """\
       <html>
       <body>
      <span style="padding-left: 20px;
                   padding-right: 80px;
                   padding-top: 50px;
                   padding-bottom: 5px;
                   font-size: 20px;
                   text-align: left !important;">
      Dear Team,              
      </span>
      <p style="padding-left: 80px;
                   padding-right: 80px;
                   padding-top: 5px;
                   padding-bottom: 5px;
                   font-size: 20px;
                   text-align: left !important;">
       Please find the enclosed iSell Report for your kind reference.
       </br>
       </br>
       {0}
       </br>        
       {1}
       </br>
       {2}
      </p>
      <p style="padding-left: 80px;
                   padding-right: 80px;
                   padding-top: 5px;
                   padding-bottom: 30px;
                   font-size: 18px;
                   text-align: left !important;">
       {3}
       <br>
       </p>

       </body>
       </html>
       """.format(text1, text2, text3, text_note)

    # ------------------------------------------------------------------------------------


    # msg.attach(MIMEText(text_body, 'plain'))
    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)
    msg.attach(MIMEText(html, 'html'))


# ==========================================================================================================


    fp = open(fileToSend+'/'+filename, "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.office365.com",587)
    server.starttls()
    server.login(username,password)
    server.sendmail(msg['From'],  recipients.split(','), msg.as_string())
    server.quit()
    print(f"{h_name} iSell is sent Successfully")


# if __name__ =='__main__':

    # send_alert_msg(email_id,sub)