import gspread
import pandas as pd
import requests
import datetime
import time



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
def read_msg(update_id):
  base_url="https://api.telegram.org/bot6176422429:AAHpWNC6B_rmnRVpoF1ueIhtiD3JOs2twDI/"
  parameters={
        'offset':update_id 


  }

  resp=requests.get(base_url+"getUpdates",data=parameters)
  data=resp.json()

  return data['result']

### function to identify the data quality question being responded to 
def str_to_dict(string):
    # remove the curly braces from the string
    string = string.strip(' ').replace('Data Quality Bot', 'Data Quality Bot:None')
    # split the string into key-value pairs
    pairs = string.split('\n')
    # print(pairs)
    pre= {key[0].rstrip().lstrip():key[1].rstrip().lstrip() for key in (pair.split(':') for pair in pairs) if key[0].rstrip().lstrip() in ['HHID', 'Variable', 'FC Name', 'Project ID', 'Task']}
    # print(pre)
    return pre
  

# gettting the response from field and edit the associated gsheets file
def getting_responses(main_text, text):
    find_key=main_text['HHID']
    find_variable=main_text['Variable']
    if 'FC Name' in main_text.keys():
        find_fc_var=main_text['FC Name']
    else:
        find_fc_var=''
    if find_key=='' or find_variable=='':
        return None
    
    ### google developer account associated credeantial
    time.sleep(2)
    gc=gspread.service_account(filename='credentials.json')
    if 'Project ID' in main_text.keys():
        key_='1jMi73_wf6nTD3rSJQ2ir0epMft6CHnmQRcq1xQhnA4k'
    elif 'Task' in main_text.keys():
        key_='1uOspkth_a7jxrNODZNtMBDW7H9NgEyvF1Plp6qABvfE'
    else:
        key_='1VfJd_0fW9QeCXqgxLtvaC3RcJygTwBxxfJfBcF1iA94'
    ### Reading in the specific googles sheets file
    sh=gc.open_by_key(key_)

    # print(sh.worksheet('Data_Quality'))
    if key_=='1uOspkth_a7jxrNODZNtMBDW7H9NgEyvF1Plp6qABvfE':
        sheet_name='Data Quality - Translations'
    else:
        sheet_name='Data Quality'

    gs=sh.worksheet(sheet_name)
        
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
    if find_fc_var!='' and key_=='1VfJd_0fW9QeCXqgxLtvaC3RcJygTwBxxfJfBcF1iA94':
        edit=19
    elif find_fc_var!='' and key_=='1uOspkth_a7jxrNODZNtMBDW7H9NgEyvF1Plp6qABvfE':
        edit=12
    elif find_fc_var=='' and key_=='1uOspkth_a7jxrNODZNtMBDW7H9NgEyvF1Plp6qABvfE':
        edit=13
    else:
        edit=11
    for r in row:
        val = gs.cell(r, edit).value
        time.sleep(2)
        val2=gs.cell(r, 14).value
        #time.sleep(2)
        print(val)
        print(val2)
        if val2!="Generic" and val==None:
            time.sleep(1)
            gs.update_cell(r, edit, text)
            time.sleep(1)

# while True:
    # reading messages


if __name__ == "__main__":
    ### Reading the update_id
    main=gspread.service_account(filename='credentials.json')
    main_key='1kq0JxL3PxB4yxZfBv_2_WOEHvy6kptP7jqB31v0XZoU'
    sheet=main.open_by_key(main_key)
    name_sheet='Master'
    ms=sheet.worksheet(name_sheet)

    update_id = ms.cell(1, 2).value

    messages=read_msg(update_id)
    x=pd.json_normalize(messages,)
    # y=pd.DataFrame(messages['message'])
    name=str(datetime.datetime.today()).replace(' ', '').replace(':', '').replace('.','')
    x.to_excel(f'check_{name}.xlsx')
    # y.to_excel(f'check2_{str(datetime.date.today())}.xlsx')
    # # editing the gsheet based on the messages sent
    for mes in messages:
        print(mes)
        if 'edited_message' in mes:
            message=mes['edited_message']
            # print(message['text'])
            # print('edited')
        elif 'message' in mes:
            message=mes['message']
            # print(message['text'])
            # print('not edited')
        if 'reply_to_message' in message and message['reply_to_message']['from']['first_name']== 'Data Quality Bot' and 'Number of Data Quality Items' not in message['reply_to_message']['text']:
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
                        print(reply_text)
                        getting_responses(pre_message, reply_text)
                        send_message_bis(585511605, reply_text)
                        time.sleep(2)
                    else:
                        #reply_text=message['voice']
                        continue



    gc=gspread.service_account(filename='credentials.json')
    key_='1VfJd_0fW9QeCXqgxLtvaC3RcJygTwBxxfJfBcF1iA94'
    ### Reading in the specific googles sheets file
    sh=gc.open_by_key(key_)

    _all=sh.worksheet('Data Quality').get_all_records()

    # working on the gsheets returned
    dataframe = pd.DataFrame(_all)
    #filtering the ones that need response if both pending and enum response is empty
    filter1= dataframe['Comment Enumerator']==""
    filter2= dataframe['Status']=="Pending"
    filter3=dataframe['Identifier']==""
    filter4=dataframe['Chat_id']!=""
    filter5= dataframe['Pending Main']=="Pending"

    # # adding a dataframe to identify row
    dataframe['row_num']=dataframe.index+2

    #filtering the ones that need response
    dataframe2=dataframe[filter1 & filter2 & filter4 & filter5 ]

    # grouping by and sending the messages
    for chat_id, data in dataframe2.groupby('Chat_id'):
        # print(chat_id)
        for index, row in data.iterrows():
            text=(str(dict(row)))
            text =  "<a href='https://www.laterite.com/'>Data Quality Bot</a>"  \
            + "\n" + f"<b>Enumerator Name: </b>"+ row['DC ID'] + \
                "\n" +   f"<b>HHID: </b>" + str(row['HHID'])  + \
                "\n" +   f"<b>Variable: </b>" + row['Variable'] \
                +  "\n" +   f"<b>Data Quality Question :</b>" + row['Comment'] \
            + "\n" + " "
            # text = f"<span class='tg-spoiler'>Enumerator Name:</span>"+ row['Enumerator Name'] +  "\n" +   f"<strong>Variable Name:</strong>" + row['variable']  

            print(text)
            # gs=sh.worksheet('Data Quality')
            if send_message(chat_id,text):
                # gs.update_cell(row['row_num'], 13, "Sent")
                # gs.update_cell(row['row_num'], 15, f"{datetime.datetime.now()}")
                # print(f"{datetime.datetime.now()}")
                send_message(585511605,row['DC ID'])
            #time.sleep(0.4)
            # send_message(585511605,row['DC ID'])
    update_id_update=str(x.update_id.max())
    if len(x)!=0:
        ms.update_cell(1, 2, update_id_update)

    # grouping by and sending the messages
    # Reading in the specific googles sheets file

    ### Reading in the specific googles sheets file
    key_='1jMi73_wf6nTD3rSJQ2ir0epMft6CHnmQRcq1xQhnA4k'
    sh=gc.open_by_key(key_)

    # print(sh.worksheet('Data_Quality'))


    gs=sh.worksheet('Data Quality')

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
    dataframe=dataframe[filter1 & filter2 & filter4 & filter5 ]
    for chat_id, data in dataframe.groupby('Chat_id'):
            count_=data.count()['Variable']
            print(count_)
            name_=list(data['DC ID'])[0]
        # print(chat_id)
        # for index, row in data.iterrows():
        #     text=(str(dict(row)))
            text =  "<a href='https://www.laterite.com/'>Data Quality Bot</a>" \
            + "\n" + f"<b>Enumerator Name: </b>"+ name_ + \
                "\n" +   f"<b>Number of Data Quality Items: </b>" + str(count_) 
            #     "\n" +   f"<b>Variable: </b>" + row['Variable'] \
            #     +  "\n" +   f"<b>Data Quality Question :</b>" + row['Comment'] \
            # + "\n" +  f"<b>Project ID: </b> WB_HH_R8" 
            # text = f"<span class='tg-spoiler'>Enumerator Name:</span>"+ row['Enumerator Name'] +  "\n" +   f"<strong>Variable Name:</strong>" + row['variable']  

            print(text)
            
            # print(send_message(chat_id, text))
            # print(send_message(585511605, text))
            if send_message(chat_id, text)==200:
                # gs.update_cell(row['row_num'], 13, "Sent")
                # gs.update_cell(row['row_num'], 15, f"{datetime.datetime.now()}")
                send_message(585511605, text)
            #send_message(585511605, text)

    # _all=sh.worksheet('Data Quality').get_all_records()

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
    dataframe=dataframe[filter1 & filter2 & filter4 & filter5 ]

    # grouping by and sending the messages
    for chat_id, data in dataframe.groupby('Chat_id'):
        # print(chat_id)
        for index, row in data.iterrows():
            text=(str(dict(row)))
            text =  "<a href='https://www.laterite.com/'>Data Quality Bot</a>" \
            + "\n" + f"<b>Enumerator Name: </b>"+ row['DC ID'] + \
                "\n" +   f"<b>HHID: </b>" + str(row['HHID'])  + \
                "\n" +   f"<b>Variable: </b>" + row['Variable'] \
                +  "\n" +   f"<b>Data Quality Question :</b>" + row['Comment'] \
            + "\n" +  f"<b>Project ID: </b> WB_HH_R8" 
            sent_status=send_message(chat_id, text)
            send_message(585511605, str(sent_status)+ f" from {row['DC ID']}")
            if sent_status==200 and filter3:
                gs.update_cell(row['row_num'], 13, "Sent")
                gs.update_cell(row['row_num'], 15, f"{datetime.datetime.now()}")
                # send_message(585511605, text)

        # time.sleep(2)




