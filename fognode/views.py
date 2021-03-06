#coding=utf-8
#__author__='zhao'
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
from fognode.models import NodeInfo, TokenTable
from datetime import datetime, date
import hashlib
import datetime
from check_validity import Check_validity
# Create your views here.

PRIORITY = 5 #1-5，level 1 need to be handled firstly
SERVICE_TYPE = 0#0==nothing
SERVICE_LIMITATION=30 #30 DAYS
TOKEN_EXPIRE=1 #1 DAY
SECURITY_LEVEL=3

def Create_token(payload,node_pk):
    m = hashlib.md5()
    # print type(fog_mac_get),type(node_mac_get)
    m.update(payload['node_mac'] +payload['node_user'] + payload['create_time_str'])
    token = m.hexdigest()
    print token
    # print node_id

    create_token = TokenTable()
    # print dir(create_token)
    create_token.node_id = node_pk
    create_token.token = token
    create_token.priority = PRIORITY
    create_token.service_type = SERVICE_TYPE
    create_token.service_limitation = payload['service_limitation']
    create_token.timestamp = payload['timestamp']
    create_token.token_security_level=SECURITY_LEVEL
    create_token.save()
    JsonDict = {"token": token,
                "priority": PRIORITY,
                "service_type": SERVICE_TYPE,
                "service_limitation": create_token.service_limitation,
                'timestamp': create_token.timestamp,
                "token_start": create_token.token_start, "status": 0,
                'token_security_level':create_token.token_security_level
                }
    print JsonDict
    return  JsonDict



@csrf_exempt
def Register_NodeInfo(request):

    try:
        if request.method=='POST':
            print request.POST

            node_mac_get=request.POST.get('node_mac')
            node_user_get=request.POST.get('node_user')
            cloud_mac_get=request.POST.get('cloud_mac')
            service_limitation_get=request.POST.get('service_limitation')
            timestamp_get = request.POST.get('timestamp')

            get_create_nodeinfo=NodeInfo.objects.get_or_create(node_mac=node_mac_get,node_user=node_user_get,
                                                               defaults={'cloud_mac':cloud_mac_get,
                                                                         'service_limitation':service_limitation_get,
                                                                         'timestamp':timestamp_get
                                                                         })
            node_pk=get_create_nodeinfo[0].pk
            print node_pk
            #node_timestamp=get_create_nodeinfo[0].timestamp
            #node_service_limitation=get_create_nodeinfo[0].service_limitation
            create_time=datetime.datetime.now()
            create_time_str=create_time.strftime("%Y-%m-%d %H:%M:%S")

            if get_create_nodeinfo[1]:
                payload={"node_mac":node_mac_get,
                         "node_user":node_user_get,
                         'timestamp': get_create_nodeinfo[0].timestamp,
                         'service_limitation': get_create_nodeinfo[0].service_limitation,
                         "create_time_str":create_time_str,}
                JsonDict=Create_token(payload,node_pk)

            else:
                try:
                    print 'oooo2'
                    Token_node=TokenTable.objects.get(node_id=node_pk)
                    print Token_node,type(Token_node)
                    token=Token_node.token
                    priority=Token_node.priority
                    service_type=Token_node.service_type
                    service_limitation=Token_node.service_limitation
                    token_security_level=Token_node.token_security_level
                    token_start = Token_node.token_start
                    timestamp=Token_node.timestamp
                    #check=Check_validity(node_timestamp,node_service_limitation)
                    #token_expired=check.check_token_expire()
                    #print token_expired
                    JsonDict={"token":token,"priority":priority,
                                "service_type":service_type,
                                "service_limitation":service_limitation,
                                'token_start':token_start,
                                'token_security_level':token_security_level,
                                'timestamp':timestamp
                            }
                except :
                    payload = {"node_mac": node_mac_get,
                        "node_user": node_user_get,
                        'timestamp': get_create_nodeinfo[0].timestamp,
                        'service_limitation': get_create_nodeinfo[0].service_limitation,
                        "create_time_str": create_time_str
                               }
                    JsonDict = Create_token(payload, node_pk)

            print JsonDict
        return JsonResponse(JsonDict)

    except:
        print 'something wrong'

    return HttpResponse('ERROR')

@csrf_exempt
def Update_Token(request):
    try:
        if request.method == 'POST':
            print request.POST,2
            #node_mac_get = request.POST.get('node_mac')
            #node_user_get = request.POST.get('node_user')
            node_token_get=request.POST.get('node_token')
            #cloud_mac_get = request.POST.get('cloud_mac')
            #node_id=NodeInfo.objects.get(node_mac=node_mac_get,node_user=node_user_get)
            try:
                update_token=TokenTable.objects.get(token=node_token_get)
                print update_token
                create_time=datetime.datetime.now()
                create_time_str=create_time.strftime("%Y-%m-%d %H:%M:%S")
                m = hashlib.md5()
                # print type(fog_mac_get),type(node_mac_get)
                m.update(node_token_get + create_time_str)
                new_token = m.hexdigest()
                print new_token
                #update_token=TokenTable.objects.get(node_id=node_id)
                update_token.token=new_token
                update_token.save()
                #print update_token
                JsonDict = {"token": new_token,
                        "priority": update_token.priority,
                        "service_type": update_token.service_type,
                    "service_limitation": update_token.service_limitation,
                    'token_start': update_token.token_start,
                    "token_security_level":update_token.token_security_level,
                    'timestamp': update_token.timestamp,
                    'del_signal': 0
                    }
            except :
                print 111
                JsonDict={'del_signal':11}
        return JsonResponse(JsonDict)
    except:
        return HttpResponse('NOT OK')

@csrf_exempt
def Del_User(request):
    try:
        if request.method == 'POST':
            print request.POST,3
            node_mac_get = request.POST.get('node_mac')
            node_user_get = request.POST.get('node_user')
            try:
                node = NodeInfo.objects.get(node_mac=node_mac_get, node_user=node_user_get)
                del_num=node.delete()
                JsonDict = {"del_num": del_num,
                    'del_signal': 3#刪除用戶
                    }
            except :
                print 123
                JsonDict={"del_num": 0,'del_signal':3}
        return JsonResponse(JsonDict)
    except:
        return HttpResponse('NOT OK')