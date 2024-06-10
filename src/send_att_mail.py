import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import datetime
from datetime import datetime #A.S may23

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

    # password = 'Revenue@123'
    password ='kskrylcjmrqjxghg'


    recipients = email_id
    alias = 'Revnomix Revenue Management Services <revnomix.RMS@revnomix.com>'
    #alias = 'revseed@revnomix.com>'

#-----------------------------------------------------------------------------------------------------------
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
    # ctype, encoding = mimetypes.guess_type(fileToSend)
    # if ctype is None or encoding is not None:
    #     ctype = "application/octet-stream"
    #
    # maintype, subtype = ctype.split("/", 1)
    # msg.attach(MIMEText(mail_content))

#==================================A.S. May23======================================================================
    msg = MIMEMultipart()
    msg['From'] = alias
    msg['To'] = ' ,'.join([str(elem) for elem in recipients.split(',')[:int(-number)]])
    msg['Cc'] = ' ,'.join([str(elem) for elem in recipients.split(',')[int(-number):]])
    msg["Subject"] = 'iSell ' +  ' | '  +  h_name  +  ' | '   + rdate1

    text1='{}'.format(text[0])
    text2 = '{}'.format(text[1])
    text3 = '{}'.format(text[2])

    text_note ='''NOTE: The Competitor Rates are extracted directly from the Online Travel Portals.
                     These rates are extracted at a particular time of the day.
                     Hence, there will be a possibility of having different rates when checked online at any other time of the day.

                     In case of any queries, please reach out to us.'''

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
      """.format(text1,text2,text3,text_note)

    # msg.attach(MIMEText(text_body, 'plain'))
    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)
    msg.attach(MIMEText(html, 'html'))

#==========================================================================================================
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

#=====================A.S. Dec23===========================================================
def inv_open_msg(h_name, date1, email_id, number, df_inv):
    # date_f = datetime.date.today()
    # sender = "revseed@revnomix.com"
    # emailto = "vibhor.khetan@revnomix.com"
    rdate = datetime.strptime(date1, "%d%b%Y").date()
    rdate1 = rdate.strftime("%d %b %Y")

    # fileToSend = beautipth + '/' + tdayfold + '/' + name_accman
    # filename = 'iSell_{}_{}.xlsx'.format(h_name, date1)
    # fileToSend = "hi.csv"
    username = 'revseed@revnomix.com'

    # password = 'Revenue@123'
    password = 'kskrylcjmrqjxghg'

    recipients = email_id
    alias = 'Revnomix Revenue Management Services <revnomix.RMS@revnomix.com>'

    msg = MIMEMultipart()
    msg['From'] = alias
    msg['To'] = ' ,'.join([str(elem) for elem in recipients.split(',')[:int(-number)]])
    msg['Cc'] = ' ,'.join([str(elem) for elem in recipients.split(',')[int(-number):]])
    msg["Subject"] = 'Low Inventory Alert' + ' | ' + h_name + ' | ' + rdate1

    # text1 = '{}'.format(text[0])
    # text2 = '{}'.format(text[1])
    # text3 = '{}'.format(text[2])

    text_note = '''NOTE: The Competitor Rates are extracted directly from the Online Travel Portals.
                     These rates are extracted at a particular time of the day.
                     Hence, there will be a possibility of having different rates when checked online at any other time of the day.

                     In case of any queries, please reach out to us.'''

    html = """\

      <html>
      <body>
      <style>
        th {{height: 40px; background-color: #606d99 !important; font-weight: bold;}}
        td {{vertical-align: center;}}
        table {{width: 85%; border-collapse: collapse; height: 120px; font-size: 20px;margin-left: auto;
        margin-right: auto;}}
        table, th, td {{border:1px solid black; text-align: center  !important;}}
      </style>

     <span style="padding-left: 20px;
                  padding-right: 80px;
                  padding-top: 50px;
                  padding-bottom: 5px;
                  font-size: 20px;
                  text-align: left !important;">
    <br>Dear Team,     
     <br><br>
       Greetings of the day! 

     </span>
     <p style="padding-left: 80px;
                  padding-right: 80px;
                  padding-top: 5px;
                  padding-bottom: 5px;
                  font-size: 20px;
                  text-align: left !important;">

Note: This email is auto-generated considering the availability on the CM. If the channel manager and PMS are live and we have offline blocking for the rooms or we are already sold out for the dates mentioned kindly disregard this email.
      </br>
      </br>
Live inventory management plays a crucial role in Hotel Revenue Management. 
It refers to the real-time tracking and control of available room inventory across various distribution channels, 
such as online travel agencies (OTAs), direct booking websites.      
      </br>
      </br>
In summary, live inventory management is vital in Hotel Revenue Management as it allows hotels to optimize revenue, 
prevent overbooking or under booking, manage distribution channels effectively, 
implement dynamic pricing strategies, and make data-driven decisions. 
By leveraging real-time inventory information, hotels can enhance their revenue potential, operational efficiency,
and overall profitability.
<br><br>

 {0}  

 <br><br>

      <p style="padding-left: 80px;
                  padding-right: 80px;
                  padding-top: 5px;
                  padding-bottom: 5px;
                  font-size: 20px;
                  text-align: left !important;">



The importance of live inventory management and providing real time room availability for your property can be beneficial in following ways:

<br><br>
<b><u>A) Maximizing Revenue</u></b>: 

By maintaining accurate and up-to-date information about available inventory, hotels can optimize their revenue potential. 
<br>

<b><u>B) Avoiding Overbooking or Under booking</u></b>:

With live inventory management, hotels can prevent both overbooking (when more rooms are sold than available) and under booking (when rooms remain unsold).
<br>

<b><u>C) Channel Management</u></b>:

Live inventory management enables effective management of multiple distribution channels. It ensures that the inventory is synchronized across different channels, preventing overselling or underselling of rooms.
<br>

<b><u>D) Rate Optimization</u></b>:

Live inventory management allows hotels to implement dynamic pricing strategies. By monitoring demand patterns, competitor rates, and other market factors, hotels can adjust room rates in real-time.
<br>

<b><u>E) Data-driven Decision Making</u></b>:
Live inventory management provides hotels with valuable data and insights about their performance, demand patterns, and customer behavior.
<br>



 </body>
 </html>
      """.format(df_inv.to_html(index=False))

    # msg.attach(MIMEText(text_body, 'plain'))
    # ctype, encoding = mimetypes.guess_type(fileToSend)
    # if ctype is None or encoding is not None:
    #     ctype = "application/octet-stream"

    # maintype, subtype = ctype.split("/", 1)
    msg.attach(MIMEText(html, 'html'))

    # =========================================================
    # fp = open(fileToSend + '/' + filename, "rb")
    # attachment = MIMEBase(maintype, subtype)
    # attachment.set_payload(fp.read())
    # fp.close()
    # encoders.encode_base64(attachment)
    # attachment.add_header("Content-Disposition", "attachment", filename=filename)
    # msg.attach(attachment)

    server = smtplib.SMTP("smtp.office365.com", 587)
    server.starttls()
    server.login(username, password)
    server.sendmail(msg['From'], recipients.split(','), msg.as_string())
    server.quit()
    print(f"{h_name} inventory_mail is sent Successfully")
