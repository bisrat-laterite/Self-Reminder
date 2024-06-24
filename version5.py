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
    pre= {key[0].rstrip().lstrip():key[1].rstrip().lstrip() for key in (pair.split(':') for pair in pairs) if key[0].rstrip().lstrip() in ['HHID', 'Variable', 'FC Name', 'Project ID']}
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
    gc=gspread.service_account(filename='credentials.json')
    if 'Project ID' in main_text.keys():
        key_='1jMi73_wf6nTD3rSJQ2ir0epMft6CHnmQRcq1xQhnA4k'
    else:
        key_='1VfJd_0fW9QeCXqgxLtvaC3RcJygTwBxxfJfBcF1iA94'
    ### Reading in the specific googles sheets file
    sh=gc.open_by_key(key_)

    # print(sh.worksheet('Data_Quality'))


    gs=sh.worksheet('Data Quality')
        
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
    else:
        edit=11
    for r in row:
        val = gs.cell(r, edit).value
        time.sleep(2)
        val2=gs.cell(r, 14).value
        print(val)
        print(val2)
        if val== None and val2!="Generic":
            time.sleep(2)
            gs.update_cell(r, edit, text)
            time.sleep(2)

# while True:
    # reading messages


if __name__ == "__main__":

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
        if 'reply_to_message' in message and message['reply_to_message']['from']['first_name']== 'Data Quality Bot':
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




