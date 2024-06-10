import network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect('1311','SiMCosta')

with open('aqd.csv', 'r') as infile:
    content = infile.read()
 
import umail
smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True) # Gmail's SSL port
smtp.login('datalogger.simcosta@gmail.com', 'hjmlsxdxqyhoiifv')
smtp.to('simcostapcs@gmail.com')
smtp.write("From: dUdU logger <datalogger.simcosta@gmail.com>\n")
smtp.write("To: pcs <simcostapcs@gmail.com>\n")
smtp.write("Subject: teste dados aqd\n\n")
smtp.write("email enviado do dUdU logger com teste do aqd.\n")
smtp.write(content)
smtp.write("\nfeito!!.\n")
smtp.write("...\n")
smtp.send()
smtp.quit()
# 
# from send_email import send_mail
# 
# send_mail({'to': 'simcostapcs@gmail.com', 'subject': 'Message from camera', 'text': 'check this out'})
