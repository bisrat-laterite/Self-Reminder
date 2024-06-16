import gspread
import pandas as pd
import requests
import datetime
import time

### google developer account associated credeantial
gc=gspread.service_account(filename='creds.json')
key_='1VfJd_0fW9QeCXqgxLtvaC3RcJygTwBxxfJfBcF1iA94'
### Reading in the specific googles sheets file
sh=gc.open_by_key(key_)

# print(sh.worksheet('Data_Quality'))


gs=sh.worksheet('Data Quality')

##function to send the message of the data quality questions 
def send_message_bis(chat_id,text):
  base_url="https://api.telegram.org/bot6176422429:AAHpWNC6B_rmnRVpoF1ueIhtiD3JOs2twDI/sendMessage"
  parameters={
        'chat_id':chat_id,
        'text':text,
        'parse_mode':'HTML',
        'disable_web_page_preview':True

  }
  success=requests.get(base_url, data=parameters)
  return success.status_code

##function to send the message of the data quality questions 
def send_message(chat_id,text):
  base_url="https://api.telegram.org/bot6176422429:AAHpWNC6B_rmnRVpoF1ueIhtiD3JOs2twDI/sendMessage"
  parameters={
        'chat_id':chat_id,
        'text':text,
        'parse_mode':'HTML',
        'disable_web_page_preview':True

  }
  success=requests.get(base_url, data=parameters)
  return success.status_code

### function for reading in the responses to the data quality questions sent
def read_msg():
  base_url="https://api.telegram.org/bot6176422429:AAHpWNC6B_rmnRVpoF1ueIhtiD3JOs2twDI/"
  resp=requests.get(base_url+"getUpdates")
  data=resp.json()

  return data['result']

### function to identify the data quality question being responded to 
def str_to_dict(string):
    # remove the curly braces from the string
    string = string.strip(' ').replace('Data Quality Bot', 'Data Quality Bot:None')
    # split the string into key-value pairs
    pairs = string.split('\n')
    # print(pairs)
    pre= {key[0].rstrip().lstrip():key[1].rstrip().lstrip() for key in (pair.split(':') for pair in pairs) if key[0].rstrip().lstrip() in ['HHID', 'Variable']}
    # print(pre)
    return pre
    # dict_=dict()
    # for key, value in pre:
    #     dict_.setdefault(key.strip(), []).append(value.strip())
    # return dict_
    # {x:y for x, y in z for z in pre}
    # return [(key, value) for key, value in (pair.split(':') for pair in pairs)]
    # return pairs
    # use a dictionary comprehension to create the dictionary, converting the values to integers and removing the quotes from the keys
    # return {key.strip().strip("'"): value.strip("'") for key, value in (pair.split(': ') for pair in pairs)}


# gettting the response from field and edit the associated gsheets file
def getting_responses(gs, main_text, text):
    find_key=main_text['HHID']
    find_variable=main_text['Variable']
    # finding hhid
    hhid=[]
    print(hhid)
    # print(text)
    # the filter to be abstracted away
    [hhid.append(l.row) for l in gs.findall(find_key)]
    # finding variable
    variable=[]
    # the filter to be abstracted away
    [variable.append(l.row) for l in gs.findall(find_variable)]
    row=list(set(hhid).intersection(variable))
    print(row)
    for r in row:
        val = gs.cell(r, 11).value
        val2=gs.cell(r, 14).value
        print(val)
        print(val2)
        if val== None and val2!="Generic":
            gs.update_cell(r, 11, text)

# while True:
    # reading messages
messages=read_msg()

x=pd.json_normalize(messages,)
# y=pd.DataFrame(messages['message'])
name=str(datetime.datetime.today()).replace(' ', '').replace(':', '').replace('.','')
x.to_excel(f'check_{name}.xlsx')
# y.to_excel(f'check2_{str(datetime.date.today())}.xlsx')
# # editing the gsheet based on the messages sent
for mes in messages:
    # print(mes)
    if 'edited_message' in mes:
        message=mes['edited_message']
        # print(message['text'])
        # print('edited')
    elif 'message' in mes:
        message=mes['message']
        # print(message['text'])
        # print('not edited')
    if 'reply_to_message' in message:
        # print(message)
        pre_message_inf=message['reply_to_message']
        if 'text' in pre_message_inf:
            if ":" in pre_message_inf['text']:
                # print(pre_message_inf['text'])
                pre_message=str_to_dict(pre_message_inf['text'])
                print(pre_message)
                # print(pre_message_inf['text'])
                # print(pre_message)
                # print(message.keys())
                if 'text' in message.keys():
                    reply_text=message['text']
                else:
                    reply_text=message['voice']
                    continue
                print(reply_text)
                getting_responses(gs, pre_message, reply_text)
                time.sleep(2)



# ### Reading in the specific googles sheets file
_all=sh.worksheet('Data Quality').get_all_records()

# working on the gsheets returned
dataframe = pd.DataFrame(_all)
#filtering the ones that need response if both pending and enum response is empty
filter1= dataframe['Comment Enumerator']==""
filter2= dataframe['Status']=="Pending"
filter3=dataframe['Sent']==""
filter4=dataframe['Chat_id']!=""
filter5= dataframe['Pending Main']=="Pending"

# # adding a dataframe to identify row
dataframe['row_num']=dataframe.index+2

#filtering the ones that need response
dataframe2=dataframe[filter1 & filter2 & filter4 & filter5 & filter3 ]

# grouping by and sending the messages
for chat_id, data in dataframe2.groupby('Chat_id'):
    # print(chat_id)
    for index, row in data.iterrows():
        text=(str(dict(row)))
        text =  "<a href='https://www.laterite.com/'>Data Quality Bot</a>" \
        + "\n" + f"<b>Enumerator Name: </b>"+ row['DC ID'] + \
            "\n" +   f"<b>HHID: </b>" + str(row['HHID'])  + \
            "\n" +   f"<b>Variable: </b>" + row['Variable'] \
            +  "\n" +   f"<b>Data Quality Question :</b>" + row['Comment'] \
        + "\n" + " "
        # text = f"<span class='tg-spoiler'>Enumerator Name:</span>"+ row['Enumerator Name'] +  "\n" +   f"<strong>Variable Name:</strong>" + row['variable']  

        # print(text)
        if send_message(chat_id,text):
            gs.update_cell(row['row_num'], 13, "Sent")
            print("done")
        time.sleep(0.4)
        send_message(585511605,row['DC ID'])
send_message(585511605,"All Done!")
        # if send_message(chat_id, text)==200:
        #     gs.update_cell(row['row_num'], 13, "Sent")

        #time.sleep()
"""
filternew= dataframe['Pending Main']=="Generic"
dataframe3=dataframe[filternew]

z=[]

for index, row in dataframe3.iterrows():
    for chat_idz in list(set(list(dataframe['Chat_id']))):
        text=(str(dict(row)))
        text =  "<a href='https://www.laterite.com/'>Data Quality Bot</a>" \
        + "\n" + f"<b>Enumerator Name: </b>"+ "Generic Comment"+ \
            "\n" +   f"<b>HHID: </b>" + "Generic Comment"  + \
            "\n" +   f"<b>Variable: </b>" + row['Variable'] \
            +  "\n" +   f"<b>Data Quality Question :</b>" + row['Comment']
        if send_message(chat_idz, text)==200:
            z.append(chat_idz)
    if len(z)==len(list(set(list(dataframe['Chat_id'])))):
        gs.update_cell(row['row_num'], 13, "Sent to all")
    else:
        s="|"
        txt=s.join(list(set([str(z) for a in z])))
        print(txt)
        gs.update_cell(row['row_num'], 13, f"Sent to{txt}")
    time.sleep(1.5)

"""
            
                


