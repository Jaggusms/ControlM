from email import message
#from Authorization_Process import send_email,emails
import os,time
#os.remove("MESSAGE_20221024210045384.log")
message_log=sorted([file for file in os.listdir(os.getcwd()) if file.endswith(".log") or file.endswith(".log")])
print(message_log)
# # mail_from,mail_to,mail_cc=emails()
# # attachments=message_log
# # body=" Please Fild the log file for prevous authorization"
# # mail_sub="ESP Endevor Selfservice log mail"
# # send_email(mail_from,mail_to,mail_sub,body,mail_cc=mail_cc,attachments=attachments)
for log in message_log:
    os.remove(os.path.join(os.getcwd(),log))  